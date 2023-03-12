import streamlit as st
import pandas as pd
import numpy as np
import option.option as opt
import option.option_ as op_
import option.models as models

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
    zinsp=st.sidebar.number_input('Interest Rate in %',value=2.0,min_value=-10.,max_value=50.,step=0.1)
    zins=zinsp/100.

    st.markdown(f'{sharename1}')
    ddates = opt.find_future_duedates(future1) # these are list of dates (indexes in future)
    df1_dates = opt.option_periods(lastdate1,quarters=8) # dataframe object
    df1_future = future1.loc[ddates]
    df1_dates['vola'] = df1_future['vola'].values
    norm_time = (df1_dates.duedate - lastdate1).apply(lambda x: x.days/365.)
    df1_dates['normtime']=norm_time
    strike = lastprice1    
    #opt1_price = [op_.bs(strike,lastprice1,zins,vola,tau,1,rent1)[0]
    #                                     for (vola,tau) in df1_dates[['vola','normtime']].iterrows() ]
    #opt1_price=[]
    #df1_dates['cprice']=df1_dates.apply(lambda x,strike,price,zins,rent: 
    #                                    op_.bs(strike,price,zins,x.vola*0.01,x.normtime,1,rent)[0],
    #                                    axis=1,strike=strike,price=lastprice1,zins=zins,rent=rent1/100)
    #df1_dates['pprice']=df1_dates.apply(lambda x,strike,price,zins,rent: 
    #                                    op_.bs(strike,price,zins,x.vola*0.01,x.normtime,-1,rent)[0],
    #                                    axis=1,strike=strike,price=lastprice1,zins=zins,rent=rent1/100)
    df1_dates = op_.bs_apply(df1_dates,strike,lastprice1,zins,rent1/100)

    #for row in df1_dates.iterrows():
    #  vola=row.vola.value
    #  tau=row.normtime.value
    #  x = op_.bs(strike,lastprice1,zins,vola,tau,1,rent1)
    st.dataframe(df1_dates[['shortcut','vola','cprice','pprice']].round(2).T)

    st.markdown(f'{sharename2}')

    ddates = opt.find_future_duedates(future2) # these are list of dates (indexes in future)
    df2_dates = opt.option_periods(lastdate2,quarters=8) # dataframe object
    df2_future = future2.loc[ddates]
    df2_dates['vola'] = df2_future['vola'].values
    norm_time = (df2_dates.duedate - lastdate2).apply(lambda x: x.days/365.)
    df2_dates['normtime']=norm_time
    strike = lastprice2
    #opt1_price = [op_.bs(strike,lastprice1,zins,vola,tau,1,rent1)[0]
    #                                     for (vola,tau) in df1_dates[['vola','normtime']].iterrows() ]
    #opt1_price=[]
    #df1_dates['cprice']=df1_dates.apply(lambda x,strike,price,zins,rent: 
    #                                    op_.bs(strike,price,zins,x.vola*0.01,x.normtime,1,rent)[0],
    #                                    axis=1,strike=strike,price=lastprice1,zins=zins,rent=rent1/100)
    #df1_dates['pprice']=df1_dates.apply(lambda x,strike,price,zins,rent: 
    #                                    op_.bs(strike,price,zins,x.vola*0.01,x.normtime,-1,rent)[0],
    #                                    axis=1,strike=strike,price=lastprice1,zins=zins,rent=rent1/100)
    df2_dates = op_.bs_apply(df2_dates,strike,lastprice2,zins,rent2/100)
    st.dataframe(df1_dates[['shortcut','vola','cprice','pprice']].round(2).T)

    #st.sidebar.write("# Option View")
    #opt1 = models.Option(aktie=sharename1,typ='C',basis=lastprice1,enddate=ddates.shortcut.iloc[5],aktkurs=lastprice1,vola=vola,zins=zins,div=rent1)
    #opt2 = models.Option(aktie=sharename1,typ='P',basis=lastprice1,enddate=ddates.shortcut.iloc[5],aktkurs=lastprice1,vola=vola,zins=zins,div=rent1)
    #ddf = pd.DataFrame([])
    #table_flag= st.checkbox('show Table')    
    #if table_flag:
    #    op_.show_table(opt1)
    #    op_.show_table(opt2)


    #fig.update_yaxes2(showgrid=True, gridwidth=1, gridcolor='DarkBlue')
    fig1 = op_.plot_options(sharename1,df1_dates,lastprice1,sharename2,df2_dates,lastprice2)
    st.plotly_chart(fig1)

    #fig2 = op_.plot_opt(opt2,ddates,lastdate2)
    #st.plotly_chart(fig2)

  with tab3:
    with open('README.md','r') as fr:
      txt = fr.read()
      st.write(txt)

if __name__ == '__main__':

  main()
