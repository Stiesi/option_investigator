import pandas as pd
import numpy as np
from scipy.special import erf #as erfun

#from option import option_periods,find_future_duedates
#import option_ as op_
#from option_ import bs
import datetime
from dateutil.relativedelta import relativedelta, FR


from ..main import get_share_data


## To Be Done

symbolyahoo1='BAS.DE'

future1,lastdate1,lastprice1,rent1=get_share_data(symbolyahoo1)

ddates = find_future_duedates(future1) # these are list of dates
dd_future = future1.loc[ddates]
ddate_obj = option_periods(lastdate1,quarters=8) # dataframe object

print(ddate_obj)
