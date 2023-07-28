import streamlit as st
from pydantic import BaseModel,Field
import pandas as pd
from deta import Deta
import json


# Connect to Deta Base with your Data Key
deta = Deta(st.secrets["eurex_base"])

db_wlshare = deta.Base("watchlist_share")

# read all share in database
@st.cache_data
def read_base():
    db = deta.Base("eurex_base")
    db_content = db.fetch().items
    return pd.DataFrame(data=db_content)

# read watchlists of shares
#
class Watchlist(BaseModel):
    key : str
    name: str = Field()
    symbols: list[str] = Field(unique_items=True)

def wls_read_all() -> list[Watchlist]:
    db_content = db_wlshare.fetch().items
    return db_content
    
def wls_read(key:str) -> Watchlist:
    #wls = db_wlshare.fetch({"name":name}).items[0]
    wls = db_wlshare.get(key)
    return Watchlist(key=wls['key'],name=wls['name'],symbols=wls['symbols'])
    
def wls_put(wls:Watchlist):
    return db_wlshare.insert(dict(name=wls.name,symbols=wls.symbols))

def wls_update(wls:Watchlist):
    return db_wlshare.update(dict(name=wls.name,symbols=wls.symbols),wls.key)

def wls_delete(key:str):    
    return db_wlshare.delete(key)


# def read_all_wls():
#     db_content = db_wlshare.fetch().items
#     return db_content

# def read_one_wls(name):
#     return db_wlshare.fetch(name=name)

# def create_wls(name='',listofshares=[]):
#     data = dict(name=name,listofshares=listofshares)
#     try:
#         db_wlshare.put(data)
#     except:
#         print('Error in creating watchlist')

# def update_wls_list(name,listofshares=[]):
#     #data = db_wlshare.fetch().items
#     try:
#         data = db_wlshare.fetch(name=name)
#         data['listofshares']=listofshares
#         db_wlshare.update(data)
#     except:
#         print('error updating %s'%name)

# def update_wls_name(name,newname):
#     data = db_wlshare.fetch(name=name)
#     data['name']=newname
#     db_wlshare.fetch(name=name)

# def delete_wls_name(name):
#     data = db_wlshare.fetch(name=name)
#     db_wlshare.delete(data['key'])


def dataframe_with_selections(df,preselect=[]):
    df_with_selections = df.copy()
    df_with_selections.insert(0, "Select", False)
    # set all preselected to True
    df_with_selections.loc[df_with_selections['symbol_ticker'].isin(preselect),'Select']=True


    # Get dataframe row-selections from user with st.data_editor
    edited_df = st.data_editor(
        df_with_selections,
        hide_index=True,
        column_config={"Select": st.column_config.CheckboxColumn(required=True)},
        disabled=df.columns,
    )

    # Filter the dataframe using the temporary column, then drop the column
    selected_rows = edited_df[edited_df.Select]
    return selected_rows.drop('Select', axis=1)

db_df = read_base()
#st.dataframe(db_df)

all_lists = wls_read_all()
listofwatchlists = [wls['name'] for wls in all_lists]

mylist = st.sidebar.selectbox('Watchlist',options=listofwatchlists)
# dict of selected name
data = all_lists[listofwatchlists.index(mylist)]
mywls = Watchlist(key=data['key'],name=data['name'],symbols=data['symbols'])
mykey = mywls.key


menu = ['New','View','Update','Delete']
select = st.sidebar.selectbox('Action',options=menu,index=1)


if select =='New':
    newcount = len(listofwatchlists)+1
    name = st.text_input("Watch List Name",value='Watchlist %d'%newcount)
    

    selection = dataframe_with_selections(db_df[['name','indices','symbol_ticker']],[])
    st.write("Your selection:")
    #st.write(db_df.loc[selection.index])
    st.dataframe(selection)
    create = st.button("Save")
    if create:
        # create list of symbols
        listofsymbols = list(selection['symbol_ticker'].values)
        mywls = Watchlist(key=name,name=name,symbols=listofsymbols)
        ok = wls_put(mywls)
        if ok:
            st.success('%s saved'%name)
            mywls = Watchlist(key=ok['key'],name=ok['name'],symbols=ok['symbols'])
            mykey = mywls.key

if select=='Update':
    mywls = wls_read(mykey)
    st.header(mywls.name)
    selection = dataframe_with_selections(db_df[['name','indices','symbol_ticker']],mywls.symbols)
    st.dataframe(selection)
    #st.dataframe(db_df.loc[db_df['symbol_ticker'].isin(mywls.symbols)])
    update = st.button('Update')
    if update:
        listofsymbols = list(selection['symbol_ticker'].values)
        mywls = Watchlist(key=mywls.key,name=mywls.name,symbols=listofsymbols)
        ok = wls_update(mywls)
        if ok:
            st.success('%s updated'%mywls.name)
        select='View'

if select=='Delete':
    #mywls = wls_read(mykey)
    #confirm = st.button('Delete %s'% mywls.name )
    st.header(mywls.name)
    confirm = st.button('Delete List %s'%mywls.name)
    if confirm:
        ok = wls_delete(mykey)
        if ok:
            st.success('%s deleted'%mywls.name)
        select='View'

if select =='View':
    st.header(mywls.name)
    mywls = wls_read(mykey)
    #st.write(mywls)
    #selection = dataframe_with_selections(db_df[['name','indices','symbol_ticker']],mywls['symbols'])
    st.dataframe(db_df.loc[db_df['symbol_ticker'].isin(mywls.symbols)])
    
    

