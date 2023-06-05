"""
get all products from EUREX
"""
import requests 
import json 
import datetime
import os
import pandas as pd

from pytickersymbols import PyTickerSymbols


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
    return [entry['symbol'],entry['symbols'][0]['yahoo'],entry['symbols'][0]['google'],entry['isins'][0]] 
  except:
     print (entry['symbols'])
     return None

def share_repo(my_iterator):
  sharedict = {entry['name']: _get_symbol(entry) for entry in my_iterator if (type(entry) is dict) and (entry['symbol'] is not None)}  
  return sharedict

def create_repos():
  stock_data = PyTickerSymbols()
  countries = stock_data.get_all_countries()
  indices = stock_data.get_all_indices()
  industries = stock_data.get_all_industries()

  ixlist =['DAX','MDAX','AEX','CAC 40','IBEX 35','BEL 20','FTSE 100','SDAX']#,'NASDAQ 100','DOW JONES']
  repo = {}
  for market in ixlist:
    stocks = stock_data.get_stocks_by_index(market)
    stocklist = [stock for stock in stocks]
    repo.update(share_repo(stocklist) )
  symbols={}
  for k,v in repo.items():
     if isinstance(v,list):
        symbols[v[0]]=k  # gives symbol['DTE']=name
  
  return repo,symbols


name_repo,symbols = create_repos()  # repo by name, symbols is dict symbol -> name

url_base = ("https://risk.developer.deutsche-boerse.com/prisma-margin-estimator-2-0-0/")
api_header = {"X-DBP-APIKEY": "0838934e-9c0d-40e3-90be-46ce591c7740"}

effective_date = datetime.date.today() + datetime.timedelta(days=2)
maturity_date = effective_date.replace(year=effective_date.year+10)


products = requests.get(url_base + "products",
                 params = {},
                 headers = api_header).json()

dprod = pd.DataFrame(products['products'])  # not needed

#all symbols in Eurex products
symbols_eurex = [prod['product'] for prod in products['products'] if prod['product'] in symbols.keys()]
for prod in products['products']:
   if prod['product'] in symbols.keys():
      print(symbols[prod['product']], name_repo[symbols[prod['product']]])

print(len(symbols_eurex))

series = requests.get(url_base + "series",
                 params = {'products': 'DTE'},
                 headers = api_header).json()

print(f'I am Live: {series["live"]}')


# get all options around actual price
price=20.
#for x in series['list_series'][::]:
#    if abs(x['exercise_price']-price)/price < 0.1 :
#        print (x['contract_maturity'],f"{x['exercise_price']:.2f}")

actual_series = [x for x in series['list_series'] if abs(x['exercise_price']-price)/price < 0.1 ]
[print (x['contract_maturity'],f"{x['exercise_price']:.2f}") for x in actual_series]

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

def get_portfolio_margins(list_of_products):
  req = {
  "portfolio_components": [
    {
      "type": "etd_portfolio",
      "etd_portfolio": list_of_products
    }
  ]
  }
  resp = requests.post(url=url_base+'estimator',json=req,headers=api_header).json()
  p_drill = pd.DataFrame(resp['drilldowns']).set_index('line_no')
  return p_drill  # dataframe with 


pass
