import streamlit as st
#import os


#os.environ["eurex_margins"] = st.secrets['eurex_margins']
import src.test_eurex as te

sym_repo = te.SYMBOLS

#@st.cache_data
#def get_shares():
#    SYMBOLS=te.create_repos()  # names from pyticker, 2 dicts
#    #sym_eurex = te.get_eurex_products(SYMBOLS) # names from eurex (should be subset of pyticker) one list
#    #SYM_EUREX = {sym: SYMBOLS[sym] for sym in sym_eurex if sym in SYMBOLS.keys()}
#    
#    #name_eurex = {name:NAME_REPO[name] for key,name in SYM_EUREX.items() }
#    return SYMBOLS

@st.cache_data
def get_optionset(symbol):
    return te.get_options(symbol)

@st.cache_data(ttl=600,show_spinner='Getting History from yahoo')
def get_history(symbol):
    return te.get_history(symbol)

@st.cache_data(ttl=120)
def get_margins(option_set):
    resp =te.get_portfolio_margins(option_set)
    df = te.df_from_portfolio(resp)
    return df

@st.cache_data
def get_markets():
    return te.markets()


st.set_page_config(page_title="Option Investigator",    
                )


#sym_repo  = get_shares()
markets = get_markets()
market = st.sidebar.selectbox('Market',options=markets.keys(),index=0)
share_name = st.sidebar.selectbox('Share',options=(markets[market]).keys(),index=0) # shares of market

share = markets[market][share_name]  


symbol = sym_repo['reverseid'][share_name]
#share_name = sym_repo[symbol][0]['sec_name']
yahoo_symbol = te.get_yahoo_symb(symbol)

try:
    #st.write(share_name)
    st.write(symbol,yahoo_symbol)
except:
    st.write('nono')

history = te.get_history(yahoo_symbol)
last_price = history.iloc[-1].Close
st.markdown(f'Last Price:   **:blue[{last_price:.2f}]**')

option_set = get_optionset(symbol)
df = get_margins(option_set)  
mat_dates = df['maturity'].sort_values().unique()
date_len=len(mat_dates)



col1,col2,col3=st.columns((2,1,1))
with col1:
    tol_1 = st.number_input('Filter Strike around Market Price in [%]',min_value=1,max_value=99,value=10,step=1)
with col2: 
    mindate = st.selectbox('Minimum Maturity',mat_dates,index=0)
with col3: 
    maxdate = st.selectbox('Maximum Maturity',mat_dates,index=date_len-1)

#option_set = get_optionset(symbol,last_price,tolerance=tol_1/100.)

df_tol = te.df_filter_strike(df,last_price,tol_1/100)
# get margins of option_set
dff = te.df_filter_date(df_tol,mindate,maxdate).sort_values(by=['contract_date','exercise_price','call_put_flag'])
#dff.style.apply(te.color_CP, column=['call_put_flag'], axis=1)

#dff['ratio']=(dff['premium_margin']/100-dff.exercise_price)/last_price
st.dataframe(dff[['contract_date','call_put_flag','exercise_price','version_number','component_margin','premium_margin']].style.apply(te.color_CP, column=['call_put_flag'], axis=1),
             use_container_width=True,             
             column_config={
        #"product_id": "Symbol",        
        #"contract_date": st.column_config.NumberColumn(
        #    "Maturity",
        #    help="date",
        #    format="%d",
        #),
        "call_put_flag":st.column_config.TextColumn('C/P',width='small'),
        'exercise_price':st.column_config.NumberColumn(
            'Strike',format="%.2f"),
        'contract_date':st.column_config.NumberColumn(
            "MaturityDate",
            help="date",
            format="%d",
        ),
        'version_number':st.column_config.TextColumn(
            'Vers.',width="small"
        ),
        'component_margin':st.column_config.NumberColumn(
            'Comp_Marg',format="%.2f"),
        'premium_margin':st.column_config.NumberColumn(
            'Prem_Marg',format="%.2f"),
        },
        hide_index=True,
        )


