import paramiko
import time
from icecream import ic
from subprocess import Popen, PIPE
import select
import os
import pandas as pd
#sshpass must be installed on host

pi_ip = '100.81.91.96'
pi_user = "pi"
pi_password = "raspberry"
local_user = 'anton'
dateString = time.strftime('%d-%m-%Y')

"""
def dump_start():
        global pi_ip, pi_user, pi_password
        
        try:
                pi_client = paramiko.client.SSHClient()
                pi_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                pi_client.connect(pi_ip, username=pi_user, password=pi_password, timeout=5)

                try:
                        ic('Launching dump1090...')
                        dump1090_launch = 'nice -n -20 ./dump1090/dump1090 --net &'
                        _stdin, _stdout,_stderr = pi_client.exec_command(dump1090_launch)
                        time.sleep(5)

                        ic('Killing all SSH stream data...')
                        kill_ssh_tail = "ps -aux | grep ConnectTimeout=5 | awk '{print $2}' | xargs kill -9"
                        Popen(kill_ssh_tail, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                        time.sleep(1)
                except Exception as e:
                        ic('ds1')
                        ic(e)
        except Exception as e:
                ic('ds2')
                ic(e)
"""

def fPrepend(filename, insert):
        with open(filename,'r') as f:
                save = f.read()
        with open(filename,'w') as f:
                f.write(insert)
                f.write(save)

def fix_log():
        global dateString, local_user
        try:
                fileName=f'''/home/{local_user}/ais/ais/static/adsb/{dateString}/feed1090.json'''
                with open(fileName,'r') as f:
                        if not f.read(1)=='{':
                                fPrepend(fileName,'{')
                with open(fileName,'a') as f:
                        f.seek(f.seek(0, os.SEEK_END) - 2)
                        f.truncate()
                        f.write('}}')
        except Exception as e:
                ic('flog')
                ic(e)

def log_start():
        global pi_ip, pi_user, pi_password
        
        try:
                pi_client = paramiko.client.SSHClient()
                pi_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                pi_client.connect(pi_ip, username=pi_user, password=pi_password, timeout=5)

                try:
                        ic('Launching log1090...')
                        log1090_launch = 'python ./log1090/log1090.py &'
                        _stdin, _stdout,_stderr = pi_client.exec_command(log1090_launch)
                        time.sleep(3)
                        
                        ic('Killing all SSH stream data...')
                        kill_ssh_tail = "ps -aux | grep ConnectTimeout=5 | awk '{print $2}' | xargs kill -9"
                        Popen(kill_ssh_tail, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                        time.sleep(1)
                except Exception as e:
                        ic('ls1')
                        ic(e)
        except Exception as e:
                ic('ls2')
                ic(e)

def log_sync():
        global pi_ip, pi_user, pi_password, local_user, dateString
        try:
                dirPath=f'''/home/{local_user}/ais/ais/static/adsb/{dateString}'''
                filePath=f'''/home/{local_user}/ais/ais/static/adsb/{dateString}/feed1090.json'''
                # Local log directory creation
                if not os.path.isdir(dirPath):
                        ic('Creating local log directory...')
                        mkdirStr = f'''mkdir -p /home/{local_user}/ais/ais/static/adsb/{dateString}'''
                        Popen(mkdirStr, shell=True, stdout=PIPE, stderr=PIPE, text=True)
                        time.sleep(2)
                # scp file to host        
                logPullString = time.strftime('%Y-%m-%d_1090ES.json')
                copyFile = f'''sshpass -p {pi_password} scp {pi_user}@{pi_ip}:/home/pi/log1090/{logPullString} /home/{local_user}/ais/ais/static/adsb/{dateString}/feed1090.json'''
                Popen(copyFile, shell=True, stdout=PIPE, stderr=PIPE, text=True)
                # JSON format fixing
                time.sleep(4)
                if os.path.isfile(filePath):
                        fix_log()
                SyncedAt = time.strftime('[%H-%M-%S] '+dateString)
                ic(SyncedAt)
        except Exception as e:
                ic('log')
                ic(e)

"""
import pandas as pd
import time
from time import sleep

def json_reader():
        local_user = 'anton'
        dateString = time.strftime('%d-%m-%Y')
        filePath = f'''/home/{local_user}/ais/ais/static/adsb/{dateString}/feed1090.json'''
        try:
                df=pd.read_json()
        except Exception as e:
                df=pd.read_json(filePath)
        print(time.strftime('Timestamp: %H-%M-%S'))
        print(df)
"""
def main():
        log_start()
        time.sleep(5)
        ic('Starting file sync loop...')
        while True:
                log_sync()
                time.sleep(8)
        
        
main()
