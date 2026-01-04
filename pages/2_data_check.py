import streamlit as st

import pandas as pd
import option.option as opt

import src.test_eurex as optex


from pytickersymbols import PyTickerSymbols


@st.cache_data(ttl=3600,show_spinner='Fetch Data from yahoo')
def test_share_history(symbol):
    try:
        return 'OK'
    except:
        return 'error'

@st.cache_data
def get_optionset(symbol):
    try:
        return optex.get_options(symbol)
    except:
        return 'error'

@st.cache_data(ttl=1200,show_spinner='Fetch Data from Eurex')
def get_margins(option_set):
    resp =optex.get_portfolio_margins(option_set)
    df = optex.df_from_portfolio(resp)
    return df

@st.cache_data
def test_options(symbol):
    try:
        optset = get_optionset(symbol)
        df = get_margins(optset)
        if df is not None:
            return 'OK'
        else: 
            return 'no data'
    except:
        return 'error'
    


#my_repo = opt.create_repos() # dictionary with stock data!!! NO!! Zuordnungen markets: [tickers]
my_db = opt.read_gsrepos() # dataframe with stock data
markets = opt.get_markets()
#my_repo = {...}
market_key=st.sidebar.selectbox('Market',options=markets,index=0)
if st.button(f'start checking  {market_key}'):
#share_dict=my_repo[market_key]
    share_df = my_db[my_db[market_key]==1]
    share_df['check_yahoo'] = share_df['yahoo'].apply(lambda x: test_share_history(x) )
    share_df['check_eurex'] = share_df['sec_id'].apply(lambda x: test_options(x) )
    #share_df['check_eurex'] = share_df.apply(lambda x: test_options(rowIndex) ,axis=1)

    st.dataframe(share_df[['_id','security_mnemonic','sec_id','check_eurex','yahoo','check_yahoo']])
