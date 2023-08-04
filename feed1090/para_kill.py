
import paramiko
import time
from icecream import ic
from subprocess import Popen, PIPE
from threading import Thread

def dump_kill():
	pi_ip = '100.81.91.96'
	pi_user = "pi"
	pi_password = "raspberry"
	time.sleep(1)
	
	try:
		pi_client = paramiko.client.SSHClient()
		pi_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		pi_client.connect(pi_ip, username=pi_user, password=pi_password, timeout=5)

		try:
			ic('Killing dump1090...')
			dump1090_kill = "ps -aux | grep ./dump1090/dump1090 | awk '{print $2}' | xargs kill -9"
			_stdin, _stdout,_stderr = pi_client.exec_command(dump1090_kill)
			time.sleep(2)

			ic('Killing all SSH stream data...')
			kill_ssh_tail = "ps -aux | grep ConnectTimeout=5 | awk '{print $2}' | xargs kill -9"
			Popen(kill_ssh_tail, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
			ic('Complete.')
		except Exception as e:
			print(e)
	except Exception as e:
		print(e)

def log_kill():
	pi_ip = '100.81.91.96'
	pi_user = "pi"
	pi_password = "raspberry"
	time.sleep(1)
	
	try:
		pi_client = paramiko.client.SSHClient()
		pi_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		pi_client.connect(pi_ip, username=pi_user, password=pi_password, timeout=5)

		try:
			ic('Killing log1090...')
			log1090_kill = "ps -aux | grep log1090.py | awk '{print $2}' | xargs kill -9"
			_stdin, _stdout,_stderr = pi_client.exec_command(log1090_kill)
			time.sleep(2)
			ic('Killing all SSH stream data...')
			kill_ssh_tail = "ps -aux | grep ConnectTimeout=5 | awk '{print $2}' | xargs kill -9"
			Popen(kill_ssh_tail, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
			
		except Exception as e:
			print(e)
	except Exception as e:
		print(e)

def main():
	ic('Killing file sync loop...')
	kill_read = "ps -aux | grep para_start.py | awk '{print $2}' | xargs kill -9"
	Popen(kill_read, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
	ic('Killing file read SSH 1/3...')
	kill_ssh_tail = "ps -aux | grep ConnectTimeout=5 | awk '{print $2}' | xargs kill -9"
	Popen(kill_ssh_tail, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
	ic('Killing file read SSH 2/3...')
	kill_ssh_tail = "ps -aux | grep ConnectTimeout=5 | awk '{print $2}' | xargs kill -9"
	Popen(kill_ssh_tail, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
	ic('Killing file read SSH 3/3...')
	kill_ssh_tail = "ps -aux | grep ConnectTimeout=5 | awk '{print $2}' | xargs kill -9"
	Popen(kill_ssh_tail, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
	#D = Thread(target=dump_kill)
	L = Thread(target=log_kill)
	#D.start()
	#time.sleep(6)
	#ic('Re-SSHing to pi...')
	L.start()
	
main()
