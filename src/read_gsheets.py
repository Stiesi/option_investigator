# Test reading from google sheets
#
import json
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import test_eurex as te

# Create a connection object.
if 1:
    conn = st.connection("gsheets", type=GSheetsConnection)

    df = conn.read()
    #worksheets = conn.worksheets()
    #[print(ws.title) for ws in worksheets]
    #df = conn.read(
    #    worksheet="name2ticker",  # geht nicht!! Bad Request
        #sheet="Tabellenblatt2", #  option nicht bekannt
        #ttl="10m",
        #usecols=[0, 1],
        #nrows=3,
    #)

    # Print results.
    for row in df.itertuples():
        st.write(f"{row.sec_name} find at {row.yahoo}:")
    
else:
    with open("Eurex_db.json") as fe:
        data = json.load(fe)

        #df = pd.read_json(fe)    
    del data['reverseid']
    #
    sharelist = [v for k,v in data.items() if k ] # no empty key
    df = pd.DataFrame(sharelist)
    #print (df)

if 1:
    # add columns with markets 1s
    mk = te.markets()
    #st.write(mk)
    # create colums with share index and mark association
    for market,mdict in mk.items():
        mnames = mdict.keys()
        sub = df.query('_id.isin(@mnames)')        
        df[market]= 0
        df[market][sub.index]=1
    st.dataframe(df)
### save df
df.to_csv('Eurex.csv')
