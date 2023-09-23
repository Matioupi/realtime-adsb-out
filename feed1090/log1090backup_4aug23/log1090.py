import json
import requests
import time
import sys, select, os

DUMP1090_ENDPOINT = 'http://localhost:8080/data.json'
UFO_DATE = time.strftime('%Y-%m-%d_ufo')
JSON_FILE = time.strftime('%Y-%m-%d_1090ES.json')

def ufoPersist():
  if not os.path.exists(UFO_DATE):
    with open(UFO_DATE,'w') as ufof1:
      ufof1.write('1')
  with open(UFO_DATE,'r') as ufof2:
    ufo = ufof2.read()
  return int(ufo)
    
def liveThread():
  global DUMP1090_ENDPOINT
  ### LIVE FILE UPDATE ###
  # Load the flight data from dump1090 endpoint
  response = requests.get(DUMP1090_ENDPOINT)
  data = response.json()

  # Time string generation
  #timeString = time.strftime("{'date': '%Y-%m-%d %H-%M-%S'}])
  
  # (Over)write live file
  #with open('live1090.json','w') as liveFile:
    #liveFile.write(str(data))
    #print('Overwrite live1090: '+timeString+str(data))
  #liveFile.close()
  return data
  
def logThread(data, ufo, index):
  global JSON_FILE, UFO_DATE
  ### LOG DIR/FILE GENERATION ###
  # Skip logging if blank
  ds=str(data)
  if ds == '[]':
    print('Blank log, skipping...')
    return 0
  
  # Write string generation
  ds=ds[1:-1]
  print(ds)
  dsArray = ds.split()
  
  ### WRITE ARRAY OPERATIONS ###
  wc = 0
  for word in dsArray:
    if word == "{'hex':":
      lineWriter = time.strftime('\n"'+str(index)+'":'+'{"time":"%H-%M-%S",')
      index+=1
      del dsArray[wc]
      dsArray[wc]=lineWriter
    # UFO handling
    if word == "'flight':":
      if dsArray[wc+1] == "'',":
        dsArray[wc+1] = "'UFO"+str(ufo)+"',"
        ufo += 1
    wc+=1
  dsArray.append(',')
  ds=''.join(dsArray)
  ds=ds.strip()
  ds=ds.replace("'",'"')
  ds=ds.replace("flight","target")
  ds=ds.replace("track","heading")
  ds=ds.replace("lat","latitude")
  ds=ds.replace("lon","longitude")
  print(ds)
  # Return to default pwd
  os.chdir('/home/pi/log1090')
  # Write log file
  logFile = open(JSON_FILE,'a')
  logFile.write(ds)
  print('Write to log file: '+JSON_FILE)
  logFile.close()
  # Save UFO counter for persistence
  with open(UFO_DATE,'w') as ufof1:
    ufof1.write(str(ufo))
  return index

### MAIN LOOP ###
def main():
  i=0
  index=1
  while True:
    i+=1
    # Main thread refresh = 1 second
    time.sleep(1)
    os.chdir('/home/pi/log1090')
    ufo = ufoPersist()
    data = liveThread()
    # i%N, log interval will be N seconds
    if i%5==0 or i==1:
      index=logThread(data, ufo, index)
      index+=1

main()
