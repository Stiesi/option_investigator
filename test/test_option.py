import ..option.option as opt
import pandas as pd
import numpy as np

def test_cumstd():
   x=pd.DataFrame(data=np.sin(np.linspace(0,10)*np.pi),columns=['x'])
   x['std'] = cumstd(x['x'])
   assert x.std.iloc[-1] approx 0.7
