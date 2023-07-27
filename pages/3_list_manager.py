import streamlit as st
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

def read_all_wls():
    db_content = db_wlshare.fetch().items
    return db_content

def read_one_wls(name):
    return db_wlshare.fetch(name=name)

def create_wls(name='',listofshares=[]):
    data = dict(name=name,listofshares=listofshares)
    try:
        db_wlshare.put(data)
    except:
        print('Error in creating watchlist')

def update_wls_list(name,listofshares=[]):
    #data = db_wlshare.fetch().items
    try:
        data = db_wlshare.fetch(name=name)
        data['listofshares']=listofshares
        db_wlshare.update(data)
    except:
        print('error updating %s'%name)

def update_wls_name(name,newname):
    data = db_wlshare.fetch(name=name)
    data['name']=newname
    db_wlshare.fetch(name=name)

def delete_wls_name(name):
    data = db_wlshare.fetch(name=name)
    db_wlshare.delete(data['key'])


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
st.dataframe(db_df)

tab1,tab2,tab3 = st.tabs(['Watchlists','Share Selector','Option Selector'])
with tab1:
    col1,col2,col3 = st.columns((1,1,1))
    with col1:
        new = st.button('New')
    watchlists = db_wlshare.fetch().items
    watchlists_names = [watchlist['name'] for watchlist in watchlists]
    if watchlists:  # watchlists exist
        name_selected = st.selectbox('Watchlist',watchlists_names)
        wls_selected = db_wlshare.fetch(dict(name=name_selected)).items[0]
        list_of_tickers = json.loads(wls_selected['watchlist_shares'])['symbol_ticker'].values()

        #selected = list_of_tickers
    else: 
        name_selected = 'Watchlist 1'
        list_of_tickers = []
    
    ws_create = st.text_input('New Watchlist',value='Watchlist 1')
    

with tab2:
    st.write(name_selected)
    selection = dataframe_with_selections(db_df[['name','indices','symbol_ticker']],list_of_tickers)
    st.write("Your selection:")
    st.write(db_df.loc[selection.index])

    # Create a new database "example-db"
    # If you need a new database, just use another name.



    with st.form("form"):
        name = st.text_input("Watch List Name",value=name_selected)
        
        create = st.form_submit_button("Store in database")
        update = st.form_submit_button("Update in database")

    if create:
        listofshares = db_df[['symbol_ticker','isin']].loc[selection.index].to_json()
        db_wlshare.put({"name": name, "watchlist_shares": listofshares})
    if update:
        data = db_wlshare.fetch(name=name)
        db_wlshare.update({"name": name, "watchlist_shares": db_df[['symbol_ticker','isin']].loc[selection.index]})

with tab3:
    st.write('Hi')