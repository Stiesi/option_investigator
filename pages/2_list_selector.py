import streamlit as st
import pandas as pd
import src.test_eurex as te

from pytickersymbols import PyTickerSymbols

#sym_repo = te.SYMBOLS

def tickerfilters():
  stock_data = PyTickerSymbols()
  # there are too many combination. Here is a complete list of all getters
  all_ticker_getter_names = list(filter(
    lambda x: (
         x.endswith('_google_tickers') or x.endswith('_yahoo_tickers')
    ),
    dir(stock_data),
    ))
  return all_ticker_getter_names


def _get_symbol(entry):
  
  try:  
    #return [entry['symbol'],entry['symbols'][0]['yahoo'],entry['symbols'][0]['google'],entry['isins'][0]] 
    return dict(symbol=entry['symbol'],yahoo=entry['symbols'][0]['yahoo'],google=entry['symbols'][0]['google'],isin=entry['isins'][0])
  except:
     print (entry['symbols'])
     return None


def share_repo(my_iterator):
  sharedict = {entry['name']: _get_symbol(entry) for entry in my_iterator if (type(entry) is dict) and (entry['symbol'] is not None)}  
  return sharedict

@st.cache_data
def pd_stocks():
  stock_data = PyTickerSymbols()
  #countries = stock_data.get_all_countries()
  #indices = stock_data.get_all_indices()
  #industries = stock_data.get_all_industries()


  #ixlist =['DAX','MDAX','AEX','CAC 40','FTSE 100','IBEX 35','BEL 20','SDAX']#,'NASDAQ 100','DOW JONES']
  #repo = {}
  
  # get all
  stocks = stock_data.get_all_stocks()
  
  stocklist = [stock for stock in stocks]
  repo = share_repo(stocklist)   
  df_stocks = pd.DataFrame(repo).T
  df_stocks['name']=df_stocks.index  
  return df_stocks

@st.cache_data
def eurex_symbols():
  all_eurex = te.get_eurex_products_list()
  eurex_df = pd.DataFrame(all_eurex,columns=['symbol','prod_name','underlying_isin'])
  return eurex_df


eurex_df = eurex_symbols()

st.write(eurex_df[eurex_df['symbol']=='VOW'])

# get a list of all shares available 
df = pd_stocks() 
#market = st.sidebar.selectbox('Market',options=markets.keys(),index=0)
#share_name = st.sidebar.selectbox('Share',options=(markets[market]).keys(),index=0) # shares of market

#share = markets[market][share_name]  


#symbol = sym_repo['reverseid'][share_name]
#share_name = sym_repo[symbol][0]['sec_name']
#yahoo_symbol = te.get_yahoo_symb(symbol)


#df['name']=df.index
#df = df.set_index('symbol') 
st.dataframe(df)
st.write(len(df))#,symbol,yahoo_symbol)


#st.write(all_eurex)

#found = [symbol for symbol in df.index if symbol in all_eurex]

# known symbols in EUREX
found = df['isin'].isin(eurex_df['underlying_isin'])
#df_found = df[~found]
#df_found = df[found]
df_mix = df.merge(eurex_df,left_on='isin',right_on='underlying_isin',how='inner',suffixes=('_ticker','_eurex'))
st.dataframe(df_mix.sort_index())
st.write(len(df_mix))#,symbol,yahoo_symbol)


