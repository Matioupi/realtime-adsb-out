import pandas as pd
import time
from time import sleep

def json_reader():
        local_user = 'anton'
        dateString = time.strftime('%d-%m-%Y')
        filePath = f'''/home/{local_user}/ais/ais/static/adsb/{dateString}/feed1090.json'''
        try:
                sleep(2)
                df=pd.read_json(filePath)
                print(time.strftime('Timestamp: %H-%M-%S'))
                print('[*] NORMAL DATA')
                return True, df
        except Exception as e:
                print(time.strftime('Timestamp: %H-%M-%S'))
                print('[!]INVALID JSON')
                return False, None


while True:
        df=json_reader()
        if df[0]:
                print(df[1])
