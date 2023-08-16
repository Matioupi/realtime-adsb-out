import pandas as pd

lf = open('test_isaac.json','r+')
data = lf.readlines()
for i in data:
    print(i)
