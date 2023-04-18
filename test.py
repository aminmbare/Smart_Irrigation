import json
import datetime 
a = {'test':[{'a':1},{'b':2},{'c':3}]}
for i in a['test']:
    i['a'] = 4
    
print(a)