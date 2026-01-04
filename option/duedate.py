import datetime
from dateutil.relativedelta import relativedelta, FR
import option

def duedates(refdate):
    if isinstance(refdate, str):    
        dt = datetime.datetime.strptime(refdate, '%Y-%m-%d')
    else:
        dt=refdate
    for month in range(3):
        m1=dt+relativedelta(months=+month)
        print (m1)
    firstquarter=(dt.month//3+1)*3
    #print(firstquarter)
    for q in range(4):
        quarter_month = (firstquarter+q*3)
        q1 = firstquarter+relativedelta(months=+quarter_month)
        print(q1)

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
    nextdue = option.get_option_expiration(dt)
    if dt.month < nextdue.month: # day is after due in actual month
        dt = dt.replace(day=1)+relativedelta(months=dt.month+1) #  1st of next month
        
    
    # first 3 months
    ddates=[option.get_option_expiration(dt+relativedelta(months=+month)) for month in range(3)]
    quarter = (dt.month-1)//3 +1
    qstr = f'q{quarter}'
    for (mon,dyear) in dq[qstr]:
        dateq = datetime.datetime(day=1,month=mon,year=dt.year+dyear)
        ddates.append(option.get_option_expiration(dateq))
    return ddates



start = '2023-01-01'
refdate = datetime.datetime.strptime(start,'%Y-%m-%d')
starts = [refdate+relativedelta(months=rd) for rd in range(12)]
for start in starts:
    print(start)
    print(_duedates(start))
    print()
