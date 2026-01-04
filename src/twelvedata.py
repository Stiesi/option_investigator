
# test API from twelvedata
import requests 
import json 
import datetime
import os
import pandas as pd
import yfinance as yf
import numpy as np

url_base="https://api.twelvedata.com/"

def get_symbols(symbol,type='stocks'):
    products = requests.get(url_base + "%s?symbol=%s"%(type,symbol),                            
    #             params = {'extrafields':'underlying_isin'},
    #            headers = api_header).json()
    )
    return eval(products.content)['data']

def get_history(symbol):
    products = requests.get(url_base + "products",
                 params = {'extrafields':'underlying_isin'},
                 headers = api_header).json()


if __name__=='__main__1':


  # test if it works, get all symbols at EUREX out of SYMBOLS
  #sym_eurex = get_eurex_products(SYMBOLS)

  # get prices
  symbol = 'DTE'
  symbols = get_symbols(symbol)
  data = pd.DataFrame.from_dict(symbols)
  print(data)


    # for greater simplicity install our package
    # https://github.com/twelvedata/twelvedata-python

import requests

response = requests.get("https://api.twelvedata.com/time_series?apikey=1df6ddc51271471290230b52f951761e&interval=1min&symbol=S6DW&exchange=FSX&previous_close=true&format=JSON&country=DE&type=etf&start_date=2024-10-03 10:53:00")

print(response.text)


# for greater simplicity install our package
# https://github.com/twelvedata/twelvedata-python

import requests

response = requests.get("https://api.twelvedata.com/time_series?apikey=1df6ddc51271471290230b52f951761e&interval=1day&symbol=BAS&format=JSON&exchange=XETR&start_date=2024-10-03 11:00:00&country=DE")

print(response.text)
    
        

