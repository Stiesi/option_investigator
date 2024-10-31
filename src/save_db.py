
# make a table out of share data
import json
import pandas as pd

import test_eurex as te

with open("Eurex_db.json") as fe:
    data = json.load(fe)

    #df = pd.read_json(fe)    
del data['reverseid']
#
sharelist = [v for k,v in data.items() if k ] # no empty key
df = pd.DataFrame(sharelist)
#print (df)
df.to_csv('Eurex.csv')
