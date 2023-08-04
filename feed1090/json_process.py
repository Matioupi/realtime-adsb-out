import pandas as pd

lf = open('feed1090.json','r+')
data = lf.readlines()
for i in data:
    print(i)
