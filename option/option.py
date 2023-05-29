import streamlit as st
from pytickersymbols import PyTickerSymbols
import numpy as np
import pandas as pd

import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots


import yfinance as yf

from dateutil.relativedelta import relativedelta, FR

def get_option_expiration(refdate):
    '''
    paramters:
    ---------
    refdate str
        reference date for next 3rd friday
    or
    refdate date object
    
    returns:
    --------
    return next 3rd friday in month
    returns a datetime object
    '''    
    if isinstance(refdate, str):
        if '/' in refdate: # from 2020/04
            dt = datetime.datetime.strptime(refdate, '%Y/%m')
        else:
            dt = datetime.datetime.strptime(refdate, '%Y-%m-%d')
    else:
        dt=refdate
    option_expiration=dt + relativedelta(day=1, weekday=FR(3))
    if option_expiration < dt:
        option_expiration=option_expiration + relativedelta(months=+1,day=1, weekday=FR(3))
    return option_expiration

def option_periods(refdate, quarters=8):
    '''
    return future option time from date
    1, 2, 3  months
    1 quarters
    2 quarters
    3 quarters
    4 quarters
    #5 quarters
    6 quarters
    #7 quarters
    8 quarters ...
    
    returns:
        pandas DataFrame with option names and list of dates
    '''
    '''
    if isinstance(refdate, str):    
        dt = datetime.datetime.strptime(refdate, '%Y-%m-%d')
    else:
        dt=refdate
    list_names=[]
    list_dates=[]
    for month in [0,1,2]:
        m1=get_option_expiration(dt+relativedelta(months=+month))
        name = m1.strftime('%Y/%m')
        list_names.append(name)
        list_dates.append(m1)
        
        
    starting_month=m1.month%3
    q1 = m1+relativedelta(day=1,months=-starting_month)
    
    for i in range(3):
        q1=get_option_expiration(q1 + relativedelta(day=1,months=+3))
        name = q1.strftime('%Y/%m')        
        list_names.append(name)
        list_dates.append(q1)
    # next year only half year options 
    for i in range((quarters-4)//2):
        q1=get_option_expiration(q1 + relativedelta(day=1,months=+6))
        name = q1.strftime('%Y/%m')
        list_names.append(name)
        list_dates.append(q1)
    '''
    # new and shorter
    list_dates = _duedates(refdate)
    list_names = [q1.strftime('%Y/%m') for q1 in list_dates]

    df=pd.DataFrame({'shortcut':list_names,'duedate':list_dates})
    return df

def _duedates(refdate):
    dq={'q1':[(6,0),(9,0),(12,0),(6,1),(12,1),(6,2),(12,2),(12,3),(12,4)],
        'q2':[(9,0),(12,0),(3,1),(6,1),(12,1),(6,2),(12,2),(12,3),(12,4)],
        'q3':[(12,0),(3,1),(6,1),(9,1),(12,1),(6,2),(12,2),(12,3),(12,4)],
        'q4':[(3,1),(6,1),(9,1),(12,1),(6,2),(12,2),(6,3),(12,3),(12,4)]
        }
    if isinstance(refdate, str):    
        dt = datetime.datetime.strptime(refdate, '%Y-%m-%d')
    else:
        dt=refdate
    nextdue = get_option_expiration(dt)
    if dt.month < nextdue.month: # day is after due in actual month
        dt = dt.replace(day=1)+relativedelta(months=1) #  1st of next month
        
    
    # first 3 months
    ddates=[get_option_expiration(dt+relativedelta(months=+month)) for month in range(3)]
    quarter = (dt.month-1)//3 +1
    qstr = f'q{quarter}'
    for (mon,dyear) in dq[qstr]:
        dateq = datetime.datetime(day=1,month=mon,year=dt.year)+relativedelta(years=dyear)
        ddates.append(get_option_expiration(dateq).date()) # make time obj to date obj
    return ddates

@st.cache_data
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


def create_future(data):
    datap = data.set_index('prodates')
    datap.sort_index(inplace=True)
    #datap['vola']=datap['Close'].pct_change().rolling(avg).std()*(252**0.5)
    datap['vola']=cumstd(datap['Close'])*100
    datap['close_percent']=datap.Close/datap.Close.iloc[0]*100
    
    return datap

def find_future_duedates(future):
    # duedates of option need not to have a date entry in data (future)
    # die nächsten drei Monate
    #  +1 innerhalb des nächsten Jahres alle quartale
    #  +2 im Folgejahr die Halbjahre
    #  +3 und 4 die 12/0003 und 12/0004
    
    opdates = option_periods(future.index.min(),quarters=8)
    # find closest day (index)
    # all indices close to due dates
    ixdd = [abs((ddate-future.index).days).argmin() for ddate in opdates['duedate']]
    return future.iloc[ixdd].index



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

def get_current_rent(symbol):
    ticker = yf.Ticker(symbol)
    todays_data = ticker.history(period='2y')
    print(todays_data.keys())
    dividends = ticker.dividends
    ydiv = pd.DataFrame(dividends)
    div=ydiv.groupby(lambda x: x.year)['Dividends'].sum()
    if len(div)>0:
      lastdiv = div.max()
      lastdiv = div.iloc[-1]
    else:
      lastdiv=0
    try:
      tname=ticker.info['longName']
    except:
      tname=ticker
    return tname,todays_data['Close'].iloc[-1],lastdiv

# langfristige Rendite plot


def adjust(df):
  df['adjusted']=df.Close

  try:
    div=df['Dividends']
    divacc = div.cumsum()
    df['adjusted']+=divacc
  except:
    pass
  return df.adjusted

def longrent(df,tau_period=365):  
  last = df.iloc[-1]
  relativ_delta=last/(df)
  relativ_delta.dropna(inplace=True)
  ddays = ( relativ_delta.index[-1]-relativ_delta.index).days +1
  ndat=len(ddays)
  #ntt=np.arange(ndat)+1 # delta days since today
  #rentindicator= int_deltas / ntt
  #grow=np.exp(np.log(relativ_delta)/ntt[::-1]*253)-1
  #tauinv = 253/ntt[::-1]
  tauinv = tau_period/ddays
  grow=relativ_delta**(tauinv)-1 # percentage grow per period since date
  extra = grow.cumsum()/ddays*tau_period #???
  #print (extra[-10:])
  return grow,extra



def get_rent(symbol):

  data=yf.Ticker(symbol)# ^mdaxi
  #name =data.info.get('shortName',data.info.get('longName'))
  #print(data.info['shortName'])
  #print(name)
  hist=data.history(period='20y')
  if len(hist.Close)==0:
    print('No Data')
  else:

    try:
      if len(hist['Stock Splits'].loc[hist['Stock Splits']>0])>0:
        print('split exists')
    except:
      pass


    #div=hist['Dividends']
    #divacc = div.cumsum()
    if len(hist.Close)<2000:
      print(hist.iloc[0])
    hist['adjusted']=adjust(hist)#hist.Close+divacc

    window=200
    hist['sma20']=hist.adjusted.rolling(window=window).mean()
    grow,extra=longrent(hist.sma20)
    hist['grow']=grow*100
    hist['int']=extra
    #hist['grow'].iloc[:-window*3].plot()
    #hist['grow'].plot()
    #hist['int'].plot()
    print(hist['grow'].mean(),hist['grow'].std())
    hist['growroll']=hist['grow'].rolling(window=window*1).mean()
    #hist['growroll'].iloc[:-window*3].plot()
    #hist['growroll'].plot()
    return hist['grow'].mean(),hist['grow'].std()

def cumstd(series):
   # needs minimum 5 numbers
   nrmin=5
   myvals = series.pct_change()
   #myvals = series
   data = [myvals.iloc[:i].std() for i in range(nrmin,len(myvals))]
   # add first value for first 2 entries
   return np.array([data[0]]*nrmin+data)*(252**0.5)



def plot_shares(sharename,future,sharename2,future2):

    ixdd = find_future_duedates(future)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=future.index,
                    y=future['close_percent'], 
                    text=future2['Close'] ,
                    customdata=future2['dates'].values,
                    hovertemplate = 'Price: %{text:.2f}<br>Date: %{customdata}',#<extra>%{sharename2}</extra>                    
                    mode='lines',
                    line=dict(color='lightblue') ,
                    name=sharename),
                  secondary_y=False,) 
    fig.add_trace(go.Scatter(x=future.index,
                    y=future['vola'], 
                    #yaxis='y2',
                    mode='lines',
                    line=dict(color='steelblue') ,
                    name=f'{sharename[:5]}.. Volatility'),
                  secondary_y=True)     
    fig.add_trace(go.Scatter(x=ixdd,y=future.loc[ixdd]['vola'],
                             mode='markers',
                             name='DueDates',
                             marker=dict(size=15,symbol='diamond',color='steelblue',
                                         line=dict(width=2, color="DarkSlateGrey"))),
                             secondary_y=True)
    
    ############# second  ###
    fig.add_trace(go.Scatter(x=future2.index,
                    y=future2['close_percent'],                    
                    text=future2['Close'] ,
                    customdata=future2['dates'].values,
                    hovertemplate = 'Price: %{text:.2f}<br>Date: %{customdata}',#<extra>%{sharename2}</extra>
                    mode='lines',
                    line=dict(color='pink') ,
                    name=sharename2),
                  secondary_y=False,) 
    fig.add_trace(go.Scatter(x=future2.index,
                    y=future2['vola'],                    
                    #yaxis='y2',
                    mode='lines',
                    line=dict(color='red') ,
                    name=f'{sharename2[:5]}.. Volatility'),
                  secondary_y=True)     
    fig.add_trace(go.Scatter(x=ixdd,y=future2.loc[ixdd]['vola'],
                             mode='markers',
                             name=f'{sharename2[:5]} DueDates',
                             marker=dict(size=15,symbol='circle',color='red',
                                         line=dict(width=2, color="DarkSlateGrey"))),
                             secondary_y=True)
    fig.update_layout(
          #xaxis=dict(type='log'),
          yaxis=dict(side='left',title='relative Share Price in %'),
          yaxis2=dict(side='right',title=f'Volatility in %'),
          #legend = dict(orientation = 'h', xanchor = "center", x = 0.5, y= 1)
          )
    fig.update_layout(title='Volatility Review for %s: %.2f  and  %s: %.2f'%(sharename,
                            future.Close.iloc[0],
                            sharename2,
                            future2.Close.iloc[0]))#,width=1500,height=400)

    return fig



def plot_share_histogram(share_name,data,tildate,volatility=0):
    '''
    

    Parameters
    ----------
    share_name : TYPE string
        Name of share.
    data :DataFrame
        share data with Date, rdate and Close.
    tildate : date
        do plot until that date
    volatility: float
        plot lines for that value
    Returns
    -------
    None.

    '''

    avg=40
    #ix_last_date=data['revDate'].idxmax()
    #dtil=(tildate-data['revDate'].max()).days
    #print (data.revDate)
    #print(type(tildate   ))
    opt_dates=data.revDate.loc[data['revDate']<tildate]
    due_date=opt_dates.max() # approx. duedate

    #print('rev',data['revDate'].min())
    #print('opt',opt_dates.min())
    #opt_dates=data.revDate
    
    y=data['Close']
    latest_close=y.loc[data['tDate'].idxmax()]
    y_refl = 2*latest_close-y
    data_avg=y.rolling(avg,center=True).mean()
    data_avg_refl=2*latest_close-data_avg
    

    
    #optduedate=opt_dates.max()
    # do binning of data
    y_opt=y.loc[data['revDate']<tildate]
    y_refl_opt=y_refl.loc[data['revDate']<tildate]
    ldays=len(y_opt)
    binmax=max(y_opt.max(),y_refl_opt.max())
    binmin=min(y_opt.min(),y_refl_opt.min())
    bins=np.linspace(binmin,binmax,num=int(ldays/4)+1)
    reg_count,reg_bins=np.histogram(y,bins)
    rev_count,rev_bins=np.histogram(y_refl,bins)
    
    # volatility: 
    #https://stackoverflow.com/questions/43284304/how-to-compute-volatility-standard-deviation-in-rolling-window-in-pandas
    # window
    y_vola=y.pct_change().rolling(ldays).std()*(252**0.5)
    y_vola=y.rolling(ldays).std()*(252**0.5)
    
    #if volatility==0:        
    volatility_jj=y_vola.loc[data.revDate==due_date].values[0]
    if volatility==0:
        volatility=volatility_jj

#    fig = go.Figure()
    fig = make_subplots(rows=1,cols=2,shared_yaxes=True,column_widths=[0.7, 0.3],
                        subplot_titles=['Chart and reflected','binning'],
                        specs=[[{'secondary_y':True},{}]])
    fig['layout']['xaxis1'].update(title='Date')       
    fig['layout']['xaxis2'].update(title='Counts')       
    fig['layout']['yaxis1'].update(title='Share Price')       
    fig['layout']['yaxis2'].update(title='Volatility')       
    fig['layout']['yaxis3'].update(title='Share Price')       

    fig.add_trace(go.Scatter(x=data['revDate'],
                    y=y,
                    mode='lines',
                    name='close'),row=1,col=1) 
    fig.add_trace(go.Scatter(x=data['revDate'],
                    y=y_refl,
                    mode='lines',
                    name='refl close'),row=1,col=1) 
    fig.add_trace(go.Scatter(x=data['revDate'],
                    y=data_avg,
                    mode='lines',
                    name='avg %d'%avg),row=1,col=1) 
    fig.add_trace(go.Scatter(x=data['revDate'],
                    y=data_avg_refl,
                    mode='lines',
                    name='refl avg %d'%avg),row=1,col=1) 
    
    fig.add_trace(go.Scatter(x=data['revDate'],
                    y=y_vola*100,
                    yaxis='y3',
                    mode='lines',
                    name='Volatility %d'%ldays),row=1,col=1) 

    fig.add_trace(go.Bar(x=reg_count,
                    y=reg_bins,
                    #mode='lines',
                    orientation='h',
                    name='Binning close'),row=1,col=2)
    fig.add_trace(go.Bar(x=rev_count,
                    y=rev_bins,
                    #mode='lines',
                    name='Binning refl',
                    orientation='h',
                    ),row=1,col=2)
    '''
    fig.add_annotation(
            go.layout.Annotation(
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.8,
            text="Close Mean, Dev. %.2f %.2f"%(y_opt.mean(),y_opt.std())),row=1,col=2)
    fig.add_annotation(
            go.layout.Annotation(
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.2,
            text="Reflect Mean, Dev. %.2f %.2f"%(y_refl_opt.mean(),y_refl_opt.std())),row=1,col=2)
    '''

    # fig.add_trace(go.Scatter(x=[opt_dates.min(),opt_dates.max()],
    #                 y=[(1+volatility)*latest_close,(1+volatility)*latest_close],
    #                 mode='lines',
    #                 name='vola %.2f'%volatility) )
    # fig.add_trace(go.Scatter(x=[opt_dates.min(),opt_dates.max()],
    #                 y=[(1-volatility)*latest_close,(1-volatility)*latest_close],
    #                 mode='lines',
    #                 name='vola %.2f'%volatility) )
    
    fig.add_shape(
        # filled Rectangle
        go.layout.Shape(
            type="rect",
            x0=opt_dates.min(),
            y0=(1-volatility)*latest_close,
            x1=opt_dates.max(),
            y1=(1+volatility)*latest_close,
            line=dict(
                color="RoyalBlue",
                width=2,
            ),
            fillcolor="LightSkyBlue",
            opacity=0.3,
        ),row=1,col=1)
    fig.add_shape(
        # filled Rectangle
        go.layout.Shape(
            type="rect",
            x0=opt_dates.min(),
            y0=(1-volatility_jj)*latest_close,
            x1=opt_dates.max(),
            y1=(1+volatility_jj)*latest_close,
            line=dict(
                color="Red",
                width=2,
            )
            #fillcolor="lightcyan",
            #opacity=0.2,
        ),row=1,col=1)
    # trick to make second axis work: 
    #https://stackoverflow.com/questions/40471026/subplots-with-two-y-axes-each-plotly-and-python-pandas
    fig['data'][4].update(yaxis='y'+str(2))
    fig.update_layout(title='%s  at %s      Volatility: %.2f %%'%(share_name,due_date.strftime('%d.%m.%y'),volatility*100),
                      barmode='stack',
                      legend=dict(
                x=1,
                y=1,
                #traceorder="normal",
                font=dict(
                    family="sans-serif",
                    size=12,
                    color="black"
                ),
                #bgcolor="LightSteelBlue",
                bgcolor="LightGrey",
                bordercolor="Black",
                borderwidth=2
            ),width=1200,height=600)
    #fig.write_html('%s.html'%(share_name))
    #fig.show()
    return fig
    
@st.cache_data
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
    repo[market]=share_repo(stocklist)  
  
  return repo

def _get_symbol(entry):
  
  try:  
    return [entry['symbol'],entry['symbols'][0]['yahoo'],entry['symbols'][0]['google'],entry['isins'][0]] 
  except:
     print (entry['symbols'])
     return None


def share_repo(my_iterator):
  sharedict = {entry['name']: _get_symbol(entry) for entry in my_iterator if (type(entry) is dict) and (entry['symbol'] is not None)}  
  return sharedict
