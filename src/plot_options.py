import pandas as pd

import numpy as np

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


def plot_margins(df,sharename='Aktie',last_price=100.):

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    df['mat_cat']= df.maturity.astype("string")
    fig.add_trace(go.Scatter(x=df.mat_cat,
                    y=df['rel_margin'], 
                    text=df['exercise_price'] ,
                    customdata=df['premium_margin'].values,
                    hovertemplate = 'Strike: %{text:.2f}<br>Date: %{x}<br>%Margin: %{y:.3f}<extra>Total Margin %{customdata}</extra>',
                    mode='markers',
                    #color='red',
                    marker=dict(color=df['exercise_price'],size=10,colorscale='Rainbow'),
                    #line=dict(color='lightblue') ,
                    name=sharename),
                  secondary_y=False,) 
    fig.update_layout(
          xaxis=dict(title='Maturity Date',
                     categoryorder='category ascending',
                     type='category',
                     #tickvals=df.mat_cat,
                     title_font=dict(size=15, family='Arial', color='black')
                     #ticktext=['%d'%x for x in df.maturity.sort_values().unique()],
                     ),
          yaxis=dict(side='left',
                     title='% Margin per contract (100)',
                     title_font=dict(size=15, family='Arial', color='blue')
                     ),
          #yaxis2=dict(side='right',title=f'Volatility in %'),
          #legend = dict(orientation = 'h', xanchor = "center", x = 0.5, y= 1),
          title=f'{sharename}'
          )

    return fig

if __name__=='__main__':
    file = r'test\option_ADS.csv'

    df = pd.read_csv(file)
    print(df)
    last_price=160.
    df['rel_strike']= df.exercise_price/last_price
    df['rel_margin']= df.premium_margin/(last_price*100) # contract size 100
    dfsub = df.loc[(df['deviation']<0.1)&(df['call_put_flag']=='P')].sort_values(by=['contract_date','exercise_price'])#,'call_put_flag'])
    st.plotly_chart(plot_margins(dfsub))
