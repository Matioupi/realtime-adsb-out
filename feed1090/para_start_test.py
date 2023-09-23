import paramiko
import time
from icecream import ic
from subprocess import Popen, PIPE
from threading import Thread
import select

pi_ip = '100.81.91.96'
pi_user = "pi"
pi_password = "raspberry"
local_user = 'anton'
dateString = time.strftime('%d-%m-%Y')

def dump_start():
	global pi_ip, pi_user, pi_password
	
	try:
		pi_client = paramiko.client.SSHClient()
		pi_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		pi_client.connect(pi_ip, username=pi_user, password=pi_password, timeout=5)

		try:
			ic('Launching dump1090...')
			dump1090_launch = "./dump1090/dump1090 --net"
			_stdin, _stdout,_stderr = pi_client.exec_command(dump1090_launch)
			time.sleep(5)

			ic('Killing all SSH stream data...')
			kill_ssh_tail = "ps -aux | grep ConnectTimeout=5 | awk '{print $2}' | xargs kill -9"
			Popen(kill_ssh_tail, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)

		except Exception as e:
			print(e)
	except Exception as e:
		print(e)

def log_start():
	global pi_ip, pi_user, pi_password
	
	try:
		pi_client = paramiko.client.SSHClient()
		pi_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		pi_client.connect(pi_ip, username=pi_user, password=pi_password, timeout=5)

		try:
			ic('Launching log1090...')
			log1090_launch = "python ./log1090/log1090.py"
			_stdin, _stdout,_stderr = pi_client.exec_command(log1090_launch)
			time.sleep(2)
			
			ic('Killing all SSH stream data...')
			kill_ssh_tail = "ps -aux | grep ConnectTimeout=5 | awk '{print $2}' | xargs kill -9"
			Popen(kill_ssh_tail, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
			time.sleep(1)
			
		except Exception as e:
			print(e)
	except Exception as e:
		print(e)

def log_sync():
	global pi_ip, pi_user, pi_password, dateString
	# before trying to to append, scp file over first
	try:
		copyFile = f'''sshpass -p {pi_password} scp {pi_user}@{pi_ip}:/home/pi/log1090/{dateString} /home/{local_user}/adsb-track-player/feed1090/{dateString}/feed1090.json'''
		Popen(copyFile, shell=True, stdout=PIPE, stderr=PIPE, text=True)
		syncUpdate = time.strftime('[%H-%M-%S] '+dateString+' synced')
		ic(syncUpdate)
	except Exception as e:
		ic(e)

def fix_log(dateString):
        filePath=f'''/home/{local_user}/adsb-track-player/feed1090/{dateString}/feed1090.json'''
        with open(filePath,'a') as jf:
                jf.write('}')

def main():
        global dateString
	D = Thread(target=dump_start)
	L = Thread(target=log_start)
	D.start()
	time.sleep(7)
	ic('Re-SSHing to pi...')
	L.start()
	time.sleep(7)
	ic('Starting file sync loop...')
	while True:
		log_sync()
		time.sleep(3)
		fix_log()
		time.sleep(7)
	
	
main()
