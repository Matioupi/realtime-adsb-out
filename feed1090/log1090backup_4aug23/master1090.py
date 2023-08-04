import subprocess
from time import sleep
import log1090
import threading
import sys, select, os

### Launch dump1090 ###
def dump():
	print('Launching dump1090 --net --interactive...')
	subprocess.call(['lxterminal', '-e', '/home/pi/dump1090/dump1090 --net --interactive'])


### log1090 loop ###
def log():
	print('Launching log1090...')
	#subprocess.call(['lxterminal', '-e', 'python /home/pi/log1090/log1090.py'])
	print('Starting Log1090, press Enter to exit...')
	i=0
	p = select.poll()
	p.register(sys.stdin, 1)
	while True:
		print('Poll counter: '+str(i))
		i+=1
		#if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
		#  print('Enter detected, exiting...')
		#  break
		# Main thread refresh = 0.5 seconds
		sleep(0.5)
		data = log1090.liveThread()
		# i%N, log interval will be N/2 seconds (DEFAULT N=60, 30 seconds)
		if i%60==0 or i==1:
			log1090.logThread(data)


def main():
	D = threading.Thread(target=dump)
	L = threading.Thread(target=log)
	D.start()
	sleep(10)
	L.start()
	
main()



