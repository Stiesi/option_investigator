
import streamlit as st
import pandas as pd
import numpy as np
import datetime
import option as op
import option.models as models
from scipy.special import erf #as erfun
import plotly.graph_objects as go
from plotly.subplots import make_subplots

       
def ndens(d): # Dichtefunktion der Standardnormalverteilung
          return np.exp(-0.5*d*d)/np.sqrt(2*np.pi)        
          
def zins_d2y(ertrag_in_laufzeit,invest,laufzeit_in_tagen):
    return (1+ertrag_in_laufzeit/invest)**(360/laufzeit_in_tagen)-1
        
def bs(S,K,r,sig,tau,phi=1,rd=0):   
    ''' 
        Optionspreis nach Black and Scholes
        
    # S Kurs
    # K Basis
    # r Zinssatz
    # sig  Voltilitaet (=Wurzel aus Standardabweichung)
    # tau  Zeitraum bis Ablauf
    # phi  1: Call, -1: Put
    # rd Dividendenrendite (bis zum Zahlungszeitpunkt)
    '''
    assert int(phi) in[-1,1]
    sig=np.clip(sig,1e-16,np.inf)
    sqrtau=np.sqrt(tau)
    sqr2 = np.sqrt(2)
    e_rd = np.exp(-rd*tau)
    e_r  = np.exp(-r*tau)
    #print 'tau',tau,'sig',sig,'K',K
    d1 = (np.log(S/K) + (r + 0.5*sig**2)*(tau))/(sig*sqrtau)
    d2 = d1 - sig*sqrtau
    N1 = 0.5*(1+erf(phi*d1/sqr2))
    N2 = 0.5*(1+erf(phi*d2/sqr2))
    Preis = phi*S*N1*e_rd - phi*K*e_r * N2
    nd1 = ndens(d1)
    Delta = phi*N1*e_rd               # 1.Ableitung nach Kurs S
    Gamma = e_rd*nd1/(sig*S*sqrtau)   # 2.Ableitung nach Kurs S
    Theta = phi*r*e_r*K*N2 + e_rd*S*(sig*nd1/(2*sqrtau) - phi* rd*N1)   # 1.Ableitung nach Zeit tau
    Vega  = sqrtau*e_rd*S*nd1                   # Ableitung nach Volatilitaet sig
    Rho   = phi * tau*np.exp(-r*tau)*K*N2       # Ableitung nach Zins (r)
    Rhod  = phi * tau*np.exp(-rd*tau)*S*N1      # Ableitung nach Dividende (rd)
    return Preis,Delta,Gamma,Theta,Vega,Rho,Rhod



def bs_apply(df,strike,price,zins,rent):
    df['cprice']=df.apply(lambda x,strike,price,zins,rent: 
                                        bs(strike,price,zins,x.vola*0.01,x.normtime,1,rent)[0],
                                        axis=1,strike=strike,price=price,zins=zins,rent=rent)
    df['pprice']=df.apply(lambda x,strike,price,zins,rent: 
                                        bs(strike,price,zins,x.vola*0.01,x.normtime,-1,rent)[0],
                                        axis=1,strike=strike,price=price,zins=zins,rent=rent)
    return df

def show_option(opt1):
    st.write(opt1.aktie)

def select_option(key,ddates,zins):
    sharename=st.text_input(f'Share Name {key}',value=f'My Company {key}',key=f'share-{key}')
    col1,col2 = st.columns((1,1))
    with col1:
        call_put=st.selectbox('Call / Put',options=['Call','Put'],key=f'CP-{key}')
    with col2:    
        div=st.number_input('Dividend per Year',value=1.,min_value=0.,key=f'dividend-{key}')

    col1a,col2a = st.columns((1,1))
    with col1a:     
        price_now=st.number_input('Share Price today',value=100., min_value=0.,format='%.2f',key=f'price_now-{key}')
        
    with col2a:     
        volatility = st.number_input('Volatility in %',value=15.,min_value=0.,step=1.,key=f'volatility-{key}')
    vola=volatility/100.

    myopt = models.Option(aktie=sharename,typ=call_put[0],basis=price_now,enddate=ddates.shortcut.iloc[5],aktkurs=price_now,vola=vola,zins=zins,div=div)
    return myopt

def show_table(opt):
    price_now = opt.aktkurs

    opt_price = np.array([price_now-1,price_now,price_now+1])
    data = np.array(opt.price(opt_price,-1))
    data1 = np.hstack((opt_price.reshape(-1,1),data.T))
    dfopt = pd.DataFrame(data=data1,columns=['share','option','delta','gamma','theta','vega','rho','rho_div'])
    #st.write(f'Option {opt1.aktie} Value of {ddates.shortcut.iloc[5]} at {price_now:.3f} today:   {today.strftime("%d.%m.%Y")}')
    st.write(f'{opt.aktie} Value of Option {opt.name} at {price_now:.3f} today:   {today.strftime("%d.%m.%Y")}')
    st.dataframe(dfopt.round(4))

def plot_options(sharename1,df1,price1,sharename2,df2,price2):
    norm_strikes = np.linspace(80,120,num=9)
    strikes1 = norm_strikes/100*price1
    df1['norm_coptprices'] = df1.cprice/price1*100
    df1['norm_poptprices'] = df1.pprice/price1*100
    df2['norm_coptprices'] = df2.cprice/price2*100
    df2['norm_poptprices'] = df2.pprice/price2*100
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df1.shortcut,
                    y=df1['cprice'], 
                    #text=future2['Close'] ,
                    #customdata=future2['dates'].values,
                    #hovertemplate = 'Price: %{text:.2f}<br>Date: %{customdata}',#<extra>%{sharename2}</extra>                    
                    mode='lines',
                    line=dict(color='lightblue') ,
                    name=f'Call {sharename1}'),
                  secondary_y=False,) 
    fig.add_trace(go.Scatter(x=df1.shortcut,
                    y=df1['pprice'], 
                    #text=future2['Close'] ,
                    #customdata=future2['dates'].values,
                    #hovertemplate = 'Price: %{text:.2f}<br>Date: %{customdata}',#<extra>%{sharename2}</extra>                    
                    mode='lines',
                    line=dict(color='steelblue') ,
                    name=f'Put {sharename1}'),
                  secondary_y=False,) 

    fig.add_trace(go.Scatter(x=df2.shortcut,
                    y=df2['cprice'], 
                    #text=future2['Close'] ,
                    #customdata=future2['dates'].values,
                    #hovertemplate = 'Price: %{text:.2f}<br>Date: %{customdata}',#<extra>%{sharename2}</extra>                    
                    mode='lines',
                    line=dict(color='pink') ,
                    name=f'Call {sharename2}'),
                  secondary_y=False,) 
    fig.add_trace(go.Scatter(x=df2.shortcut,
                    y=df2['pprice'], 
                    #text=future2['Close'] ,
                    #customdata=future2['dates'].values,
                    #hovertemplate = 'Price: %{text:.2f}<br>Date: %{customdata}',#<extra>%{sharename2}</extra>                    
                    mode='lines',
                    line=dict(color='red') ,
                    name=f'Put {sharename2}'),
                  secondary_y=False,) 
######################################################  rel prices
    fig.add_trace(go.Scatter(x=df1.shortcut,
                    y=df1['norm_coptprices'], 
                    #text=future2['Close'] ,
                    #customdata=future2['dates'].values,
                    #hovertemplate = 'Price: %{text:.2f}<br>Date: %{customdata}',#<extra>%{sharename2}</extra>                    
                    mode='lines',
                    line=dict(color='lightblue',dash='dash') ,
                    name=f'Call {sharename1}'),
                  secondary_y=True,) 
    fig.add_trace(go.Scatter(x=df1.shortcut,
                    y=df1['norm_poptprices'], 
                    #text=future2['Close'] ,
                    #customdata=future2['dates'].values,
                    #hovertemplate = 'Price: %{text:.2f}<br>Date: %{customdata}',#<extra>%{sharename2}</extra>                    
                    mode='lines',
                    line=dict(color='steelblue',dash='dash') ,
                    name=f'Put {sharename1}'),
                  secondary_y=True,) 

    fig.add_trace(go.Scatter(x=df2.shortcut,
                    y=df2['norm_coptprices'], 
                    #text=future2['Close'] ,
                    #customdata=future2['dates'].values,
                    #hovertemplate = 'Price: %{text:.2f}<br>Date: %{customdata}',#<extra>%{sharename2}</extra>                    
                    mode='lines',
                    line=dict(color='pink',dash='dash') ,
                    name=f'Call {sharename2}'),
                  secondary_y=True,) 
    fig.add_trace(go.Scatter(x=df2.shortcut,
                    y=df2['norm_poptprices'], 
                    #text=future2['Close'] ,
                    #customdata=future2['dates'].values,
                    #hovertemplate = 'Price: %{text:.2f}<br>Date: %{customdata}',#<extra>%{sharename2}</extra>                    
                    mode='lines',
                    line=dict(color='red',dash='dash') ,
                    name=f'Put {sharename2}'),
                  secondary_y=True,) 



    fig.update_layout(
          #xaxis=dict(type='log'),
          yaxis=dict(side='left',title='Option Price'),
          yaxis2=dict(side='right',title=f'relative Option Price in %'),
          #legend = dict(orientation = 'h', xanchor = "center", x = 0.5, y= 1)
          )
    fig.update_layout(title='Option Prices for %s  and  %s'%(sharename1,
                            
                            sharename2,
                            ))#,width=1500,height=400)

    return fig

def plot_opt(opt,ddates,today):
    price_now = opt.aktkurs
    # plot normalized prices and strikes to compare multiple options
    norm_time = (ddates.duedate -today).apply(lambda x: x.days/365.)

    #ltime = pd.DataFrame(data=norm_time,columns=['Time']) - today
    #price_now=100.
    if opt1.phi==1:
        norm_strikes = np.linspace(95,120,num=6)
    else:
        norm_strikes = np.linspace(80,105,num=6)

    strikes = norm_strikes/100*price_now
    #df_vals = pd.DataFrame(data=prices.T,columns=['prices','delta','gamma','theta','vega','rho','rho_div'])
    #df = df.join(df_vals)
    #st.dataframe(df_vola)

    layout = go.Layout(
        legend=dict(
            orientation="h",
            entrywidth=60,
            yanchor="top",
            y=1.02,
            xanchor="left",
            x=0
            ))
    fig = go.Figure(layout=layout)
    for strike in strikes:
        x = bs(price_now,strike,zins,opt.vola,norm_time.values,opt.phi,opt.r_div)
        opt_prices = np.array(x[0])
        norm_optprices = opt_prices/price_now*100
        fig.add_trace(go.Scatter(yaxis='y2',y=norm_optprices,x=ddates.duedate,showlegend=False,visible=True,mode='markers'))
        fig.add_trace(go.Scatter(y=opt_prices,x=ddates.duedate,name='%.2f : %.2f'%(strike,strike/price_now*100)))



    fig.update_layout(  title = f"Plot Option {opt.name} Price Distribution",
                        xaxis_title='Due Date',
                        yaxis  = dict(title = 'option price',side='left'),
                        yaxis2 = dict(title='option price in % of share',
                            overlaying='y',
                            side='right'))#)idth=1500,height=400
                        
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightBlue')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightBlue')
    return fig

if __name__=='__main__':
    today = datetime.date.today()
    ddates = op.option_periods(today,quarters=8)
    zinsp=st.number_input('Interest Rate in %',value=2.0,min_value=-10.,max_value=50.)
    zins=zinsp/100.


    st.sidebar.write("# Option View")
    col1,col2 = st.columns((1,1))
    with col1:
        opt1 = select_option('opt1')    
    with col2:
        opt2 = select_option('opt2')
    table_flag= st.checkbox('show Table')    
    if table_flag:
        show_table(opt1)
        show_table(opt2)


    #fig.update_yaxes2(showgrid=True, gridwidth=1, gridcolor='DarkBlue')
    fig1 = plot_opt(opt1)
    st.plotly_chart(fig1)

    fig2 = plot_opt(opt2)
    st.plotly_chart(fig2)