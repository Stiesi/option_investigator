import streamlit as st
import pandas as pd
import option.option as opt
from pytickersymbols import PyTickerSymbols


@st.cache_data
def cached_rent(symbol):
  try:
    tickerobj,price,rent = opt.get_current_rent(symbol)
    return price,rent
  except:
    return None,None


@st.cache_data
def generate_table():
  #import src.test_eurex as te
  # only use stock that exist in EUREX
  #eurex_existnames = list(te.SYMBOLS['reverseid'].keys())
  stock_data = PyTickerSymbols()
  countries = stock_data.get_all_countries()
  indices = stock_data.get_all_indices()
  industries = stock_data.get_all_industries()
  all = stock_data.get_all_stocks()

  ixlist =['DAX','MDAX','AEX','CAC 40','IBEX 35','BEL 20','FTSE 100','SDAX','NASDAQ 100','DOW JONES']
  dfrepo=None
  for market in ixlist:
    stocks = stock_data.get_stocks_by_index(market)
    #stocklist = [stock for stock in stocks if stock['name'] in eurex_existnames]
    dftemp=pd.DataFrame.from_dict(share_repo(stocks)).T
    dftemp.columns=['_id','yahoo','google','ISIN']
    dftemp[market]=1
    if dfrepo is None:
      dfrepo = dftemp
    else:
      dfrepo = pd.concat((dfrepo,dftemp))
  #dfrepo.columns[:3]=['_id','yahoo','google']
  dfrepo.dropna(inplace=True,subset='_id')
  return dfrepo



def _get_symbol(entry):
  
  try:  
    return [entry['symbol'],entry['symbols'][0]['yahoo'],entry['symbols'][0]['google'],entry['isins'][0]] 
  except:
     print (entry['symbols'])
     return None


def share_repo(my_iterator):
  sharedict = {entry['name']: _get_symbol(entry) for entry in my_iterator if (type(entry) is dict) and (entry['symbol'] is not None)}  
  return sharedict


st.title('Dividends')
# for first generation
#df = generate_table()
#df.to_csv('all_shares.csv')
tst_ticker = st.sidebar.text_input('Enter ticker')
if tst_ticker:  
  st.sidebar.write(opt.get_current_rent(tst_ticker)) # DPW.F
df=opt.read_gs_all_shares()

#def write2box(price,rent):
#  if 'textbox' in st.session_state.keys():
#    #st.session_state.textbox = '%.2f %.2f'%(price,rent)
#    st.session_state['textbox'] = '%.2f %.2f'%(price,rent)

#txtbox = st.empty()
#tb=st.text_area('Reading',value='',key='textbox')
# for testing
if 0:
  for ix,row in df.iterrows():
    try:
      price,rent = cached_rent(row.yahoo)
    #st.text_area('reading',value='%.2f %.2f'%(price,rent))
    #st.session_state['textbox'] = '%.2f %.2f'%(price,rent)
      #st.write('%.2f %.2f'%(price,rent))
    except:
      st.write('error on %s %s'%(row.name,row.yahoo))
    #write2box(price,rent)
with st.spinner('Request Tickers ...'):
  df_rent = df.apply(lambda row: cached_rent(row.yahoo),axis='columns')#, result_type='expand')
  df[['price','rent']]=pd.DataFrame(df_rent.to_list(),index=df.index)
#df = pd.concat([df, df_rent], axis='columns')
st.dataframe(df)
