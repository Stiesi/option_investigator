import streamlit as st
import pandas as pd
from deta import Deta


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


# Create a new database "example-db"
# If you need a new database, just use another name.


db_df = read_base()
st.dataframe(db_df)

msel  = st.selectbox('Share',options=db_df['name'])
dataset = db_df[db_df['name']==msel]
st.write(dataset)

with st.form("form"):
    name = st.text_input("Watch List Name")
    age = st.number_input("Your age")
    submitted = st.form_submit_button("Store in database")

if submitted:
    db_wlshare.put({"name": name, "age": age})