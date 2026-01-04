import streamlit as st
import pandas as pd
import option.option as opt
from pytickersymbols import PyTickerSymbols

import yfinance as yf

@st.cache_data
def cached_rent(symbol):
  try:
    tickerobj,price,rent = opt.get_current_rent(symbol)
    return price,rent
  except:
    return None,None


tickers = ['DTE.DE','DBK.DE','BAS.DE']
for sha in tickers:
  ticker = yf.Ticker(sha)
  p,r = cached_rent(sha)
  
  st.write(sha,p,r)

ticks = yf.Tickers(tickers)
st.write(ticks.history())