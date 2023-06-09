"""
get all products from EUREX
"""

import requests 
import json 
import datetime
import os
import pandas as pd
import yfinance as yf

#import option as opt

#from fastapi import FastAPI
from pydantic import BaseModel

from pytickersymbols import PyTickerSymbols



url_base = ("https://risk.developer.deutsche-boerse.com/prisma-margin-estimator-2-0-0/")
try:
  eurex_key = os.environ['eurex_margins']  
except:
  print('set Environment variable >>> eurex_margins <<< to access key for Deutsche Boerse API')  

api_header = {"X-DBP-APIKEY": eurex_key}

effective_date = datetime.date.today() + datetime.timedelta(days=2)
maturity_date = effective_date.replace(year=effective_date.year+10)



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


def markets():
  stock_data = PyTickerSymbols()
  countries = stock_data.get_all_countries()
  indices = stock_data.get_all_indices()
  industries = stock_data.get_all_industries()

  ixlist =['DAX','MDAX','AEX','CAC 40','FTSE 100']#,'IBEX 35','BEL 20','SDAX']#,'NASDAQ 100','DOW JONES']
  repo = {}
  
  for market in ixlist:
    stocks = stock_data.get_stocks_by_index(market)
    stocklist = [stock for stock in stocks]
    repo[market] = share_repo(stocklist) 

  return repo

def create_repos():

  if os.path.exists('EUREX_DB.json'):
    with open('EUREX_DB.json') as fr:
      SYMBOLS=json.load(fr)
    return SYMBOLS
  
  repo = markets()
  symbols={'reverseid':{}}
  for market,stock_repo in repo.items():
    
    for share,stock_data in stock_repo.items():
      try:
        resp = requests.get(url_base + "securities",
                    params = {'isin':stock_data['isin']}, # isin connection of Eurex and Pyticker
                    headers = api_header).json()
        eurex_data = resp['securities']
        if eurex_data[0]: # not empty            
            veurex = {k:v for k,v in (eurex_data[0]).items()} # eurex data
            veurex['_id']=share  # connection to repo index
            veurex.update(stock_data)
            #stock_data.update(veurex) # add all entries from eurex
            symbols[veurex['sec_id']] = veurex  # make symbol key for 
            symbols['reverseid'][share]=veurex['sec_id']

      except:
          print(f'Share {share} not available')    

  with open('EUREX_DB.json','w') as fp:
    json.dump(symbols,fp)
  
  return symbols


def get_history(symbol):
   ticker = get_ticker(symbol)
   history=ticker.history(period='2y')
   today = datetime.date.today()
   history['dates']=history.index.date
   history.index=history.dates
   #history.reindex()
   history['reversedates']= history.dates.values[::-1]
   # mirror dates from past to future:
   #   add delta days from reversdates to today
   history['prodates']=(today - history.dates).apply(lambda x: today + x) # shift reversedates to future

   return history


def get_ticker(symbol):
    
    print(">>", symbol, end=' ... ')
    try:
        ticker = yf.Ticker(symbol)    
    
    # always should have info and history for valid symbols
        assert(ticker.fast_info is not None and ticker.fast_info != {})
        assert(ticker.history(period="max").empty is False)

        # following should always gracefully handled, no crashes
        if 0:
          ticker.cashflow
          ticker.balance_sheet
          ticker.financials
          ticker.sustainability
          ticker.major_holders
          ticker.institutional_holders

        print("OK")
    except:
        print('Problem')
    return  ticker



def get_eurex_products(SYMBOLS):

  products = requests.get(url_base + "products",
                 params = {},
                 headers = api_header).json()

  #dprod = pd.DataFrame(products['products'])  # not needed

  #all symbols in Eurex products
  symbols_eurex = [prod['product'] for prod in products['products'] if prod['instrument_type'] =='option']
  #for prod in products['products']:
  #  if prod['product'] in symbols.keys():
  #    print(symbols[prod['product']], name_repo[symbols[prod['product']]])

  print(len(symbols_eurex))
  return symbols_eurex

class Option(BaseModel):
  product_id:str
  contract_maturity: str
  exercise_price: float
  contract_date: int  # date in 8 digits yyyymmdd
  call_put_flag: str  # C or P
  


class Portfolio(BaseModel):
  options: list[Option]
  net_ls_balance: list[int]


def get_yahoo_symb(symbol):
  return SYMBOLS[symbol]['yahoo']

def get_options(symbol):

  series = requests.get(url_base + "series",
                 params = {'products': symbol},
                 headers = api_header).json()

  print(f'I am Live: {series["live"]}')

  #actual_series = [x for x in series['list_series'] if abs(x['exercise_price']-last_price)/last_price < tolerance ]
  #[print (x['contract_maturity'],f"{x['exercise_price']:.2f}") for x in actual_series]
  options = [dict(
            product_id=symbol,
              contract_maturity=x['contract_maturity'],
              exercise_price=x['exercise_price'],
              contract_date=x['contract_date'],
              call_put_flag=x['call_put_flag'],              
              )
            for x in series['list_series']
            ]
  return options


def get_portfolio_margins(list_of_products,line_nos=[]):
  if line_nos==[]:
    line_nos = range(len(list_of_products))
  # updates in objects, no new list
  [ x.update(dict(line_no=i,net_ls_balance=-1)) for i,x in zip(line_nos,list_of_products) ]

  req = {
  "portfolio_components": [
    {
      "type": "etd_portfolio",
      "etd_portfolio": list_of_products
    }
  ]
  }
  try:
    resp = requests.post(url=url_base+'estimator',json=req,headers=api_header).json()
    return resp
  except:
    print('Error in portfolio from Eurex')
    return None

def df_from_portfolio(resp):
  p_drill = pd.DataFrame(resp['drilldowns']).set_index('line_no').astype(dict(contract_date=int,maturity=int,exercise_price=float))  
  return p_drill[['product_id', 'contract_date', 'maturity', 'call_put_flag',
       'exercise_price', 'version_number', 'net_ls_balance',
       'component_margin',
       #'component_margin_currency',
       'premium_margin',  # thats it!!
       #'premium_margin_currency'
       ]]  # dataframe with 


# colorstyle pandas
def color_CP(s, column):
    is_put = pd.Series(data=False, index=s.index)
    is_put[column] = s.loc[column] == 'P'
    return ['background-color: wheat' if is_put.any() else 'background-color: lightgreen' for v in is_put]

def df_filter_strike(df:pd.DataFrame,last_price:float,tolerance:float):
  # yyyymm

  #until_year8 = (until_year)+1*10000 # add 4 digits
  df['deviation']=abs(df['exercise_price']-last_price)/last_price
  return df.loc[df['deviation']<=tolerance]


def df_filter_date(df,from_due:int,until_due:int):
  # yyyymm

  #until_year8 = (until_year)+1*10000 # add 4 digits
  return df.loc[(df['maturity']>=from_due)&(df['maturity']<=until_due)]

# GLOBAL Data
SYMBOLS = create_repos()  # repo by name, symbols is dict symbol -> name


if __name__=='__main__':


  # test if it works, get all symbols at EUREX out of SYMBOLS
  #sym_eurex = get_eurex_products(SYMBOLS)

  # get prices
  symbol = 'DTE'
  history = get_history(get_yahoo_symb(symbol))
  last_price = history.iloc[-1].Close

  # get options of DTE
  option_set = get_options(symbol,last_price)
  
  # get margins of option_set
  resp = get_portfolio_margins(option_set)
  df = df_from_portfolio(resp)
  print(df_filter_date(df,202312,202412))
##############
'''
Index(['iid', 'product_id', 'contract_date', 'maturity', 'call_put_flag',
       'exercise_price', 'version_number', 'net_ls_balance',
       'liquidation_group', 'liquidation_group_split', 'component_margin',
       'component_margin_currency', 'premium_margin',
       'premium_margin_currency'],
      dtype='object')

req ={
  "portfolio_components": [
    {
      "type": "etd_portfolio",
      "etd_portfolio": [
        {
          "line_no": 1,
          "product_id": "DTE",
          "contract_date": 20230616,
          "call_put_flag": "C",
          "exercise_price": 20,
          "net_ls_balance": 10
        },
        {
          "line_no": 3,
          "product_id": "DTE",
          "contract_date": 20230616,
          "call_put_flag": "C",
          "exercise_price": 19,
          "net_ls_balance": 10
        }
      ]
    }
  ]
}
resp = requests.post(url=url_base+'estimator',json=req,headers=api_header).json()

p_drill = pd.DataFrame(resp['drilldowns']).set_index('line_no')
print(p_drill)

pass
'''