# test volatility
import pandas as pd
import numpy as np
#import matplotlib.pyplot as pl

def volatility_1(ser,ldays=10):
    y_vola=ser.pct_change().rolling(ldays).std()*(252**0.5)
    return y_vola

def volatility_2(ser,ldays=10):
    y_vola=ser.rolling(ldays).std()*(252**0.5)
    return y_vola

def cumstd(series):
   # needs minimum 5 numbers
   nrmin=5
   myvals = series.pct_change()
   #myvals = series
   data = [myvals.iloc[:i].std() for i in range(nrmin,len(myvals))]
   # add first value for first 2 entries
   return np.array([data[0]]*nrmin+data)*(252**0.5)    


num=100
xc = np.linspace(1,100,num=num)
yc = np.ones(num)*50.
yl = np.linspace(1,100,num=num)

ycv = yc + np.sin(2*np.pi * xc/10.) * 5.
ycr = yc + np.random.random(100)*5

ylv = yl + np.sin(2*np.pi * xc/10.) * 5.
ylr = yl + np.random.random(100)*5

df = pd.DataFrame({'day':xc,'kurs':ylv})
df['vola'] = cumstd(df.kurs)
#df.plot('yl','vola')
print(df)