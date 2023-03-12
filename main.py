import streamlit as st
import pandas as pd
import numpy as np
import option.option as opt

st.set_page_config(page_title="Option Investigator",    
                )

def _get_latest(future):
  latedate = future.dates.max()
  
  lateprice = future.loc[future.dates==latedate].Close.values[0]
  return latedate,lateprice

@st.cache_data
def get_share_data(symbol):
    history = opt.get_history(symbol)
    future  = opt.create_future(history)
    
    rent = opt.get_current_rent(symbol)
    lastdate,lastprice = _get_latest(future)
    ret = rent[-1]/lastprice *100
    return((future,lastdate,lastprice,ret))

def main():
  my_repo = opt.create_repos()
  market_key=st.sidebar.selectbox('Market',options=my_repo.keys(),index=0)
  share_dict=my_repo[market_key]
  
  # here it goes
  col1,col2 = st.columns((1,1))
  with col1:
    sharename1 = st.selectbox('Share 1',options=share_dict.keys(),index=1)
    symbol1,symbolyahoo1 = share_dict[sharename1][:2]
    

    future1,lastdate1,lastprice1,rent1=get_share_data(symbolyahoo1)
    st.markdown(f'{lastdate1}: **{lastprice1:.2f}**') 
    st.markdown(f'Dividend Return: {rent1:.2f}%')
  with col2:
    sharename2 = st.selectbox('Share 2',options=share_dict.keys(),index=2)
    symbol2,symbolyahoo2 = share_dict[sharename2][:2]

    future2,lastdate2,lastprice2,rent2=get_share_data(symbolyahoo2)
    st.markdown(f'{lastdate2}: **{lastprice2:.2f}**')
    st.markdown(f'Dividend Return: {rent2:.2f}%')

  tab1,tab2,tab3 = st.tabs(['Share','Option','about'])

  #st.dataframe(history)
  #print(history)
  with tab1:
    fig = opt.plot_shares(sharename1,future1,sharename2,future2)
  #fig = plot_share(sharename,history,history.prodates.max(),volatility=0.2)
    st.plotly_chart(fig)
  with tab2:
    st.write('here i am')
  with tab3:
    with open('README.md','r') as fr:
      txt = fr.read()
      st.write(txt)

if __name__ == '__main__':

  main()
