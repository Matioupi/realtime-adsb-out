""" This class holds the aircraft states from the ADS-B point of view

It is refreshed by the simulation thread (or sensor feed thread) and will
be used to provide broadcasted informations

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

#
#   This class overrides threading.Thread and provides service to broacast
#   ADS-B message though a HackRF device
#   message updates are performed from a separate thread which will
#   update/push messages thanks to the replace_message method
#   thread loop will pump and broacast updated message (soft realtime)
#
#   mutex protection mecanism is implemented in
#   replace_message() which is call from other thread
#   broadcast_one_message() which is called from this thread
#   in order to prevent concurrent access to broadcasted data buffers

import time, datetime, math
import threading

from CustomDecorators import *
from ADSBLowLevelEncoder import ADSBLowLevelEncoder
from pyhackrf import *
from ctypes import *

class hackrf_tx_context(Structure):
    _fields_ = [("buffer", POINTER(c_ubyte)),
                ("last_tx_pos", c_int),
                ("buffer_length", c_int) ]

def hackrfTXCB(hackrf_transfer):
    user_tx_context = cast(hackrf_transfer.contents.tx_ctx, POINTER(hackrf_tx_context))
    tx_buffer_length = hackrf_transfer.contents.valid_length
    left = user_tx_context.contents.buffer_length - user_tx_context.contents.last_tx_pos
    addr_dest = addressof(hackrf_transfer.contents.buffer.contents)
    addr_src = addressof(user_tx_context.contents.buffer.contents)

    if (left > tx_buffer_length):
        memmove(addr_dest,addr_src,tx_buffer_length)
        user_tx_context.contents.last_tx_pos += tx_buffer_length
        return 0
    else:
        memmove(addr_dest,addr_src,left)
        memset(addr_dest+left,0,tx_buffer_length-left)
        return -1

@Singleton
class HackRfBroadcastThread(threading.Thread):
    def __init__(self,airborne_position_refresh_period = 150000):
        super().__init__()
        self._mutex = threading.Lock()

        self._lowlevelencoder = ADSBLowLevelEncoder()

        self._messages_feed_threads = {}

        # Initialize pyHackRF library
        result = HackRF.initialize()
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :",result, ",", HackRF.getHackRfErrorCodeName(result))

        # Initialize HackRF instance (could pass board serial or index if specific board is needed)
        self._hackrf_broadcaster = HackRF()

        # HackRF Transmit Settings
        result = self._hackrf_broadcaster.open()
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :",result, ",", HackRF.getHackRfErrorCodeName(result))
            
        self._hackrf_broadcaster.setCrystalPPM(0)
        
        result = self._hackrf_broadcaster.setAntennaPowerMode(LibHackRfHwMode.HW_MODE_ON) # Antenna Power Mode ON or OFF
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :",result, ",", HackRF.getHackRfErrorCodeName(result))
           
        result = self._hackrf_broadcaster.setAmplifierMode(LibHackRfHwMode.HW_MODE_ON)	# LNA Amplifier ON or OFF
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :",result, ",", HackRF.getHackRfErrorCodeName(result))
            
        result = self._hackrf_broadcaster.setLNAGain(14)				# LNA Amplifier Gain
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :",result, ",", HackRF.getHackRfErrorCodeName(result))
                        
        # 2MHz sample rate to meet ADS-B spec of 0.5µs PPM symbol
        result = self._hackrf_broadcaster.setSampleRate(2000000)
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :",result, ",", HackRF.getHackRfErrorCodeName(result))
            
        result = self._hackrf_broadcaster.setBasebandFilterBandwidth(HackRF.computeBaseBandFilterBw(2000000))
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :",result, ",", HackRF.getHackRfErrorCodeName(result))
            
        #result = self.hackrf_broadcaster.setFrequency(868000000)			# 868MHz = Free frequency for over the air broadcast tests
        result = self._hackrf_broadcaster.setFrequency(1090000000)			# Actual 1090MHz frequency setting
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :",result, ",", HackRF.getHackRfErrorCodeName(result))
            
        result = self._hackrf_broadcaster.setTXVGAGain(47)				# TX VGA Gain (4 for wire feed + attenuators, 47 for wireless)
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :",result, ",", HackRF.getHackRfErrorCodeName(result))  
        
        self._tx_context = hackrf_tx_context()

        self._do_stop = False

    # HackRF lib and instance cleanup at object destruction time
    def __del__(self):
        result = self._hackrf_broadcaster.close()
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :",result, ",", HackRF.getHackRfErrorCodeName(result))

        result = HackRF.deinitialize()
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :",result, ",", HackRF.getHackRfErrorCodeName(result))

    def stop(self):
        self._do_stop = True

    def getMutex(self):
        return self._mutex

    # updates the next data to be broadcaster for a given message type
    #@Timed
    def replace_message(self,type,frame_even,frame_odd = []):

        # 1090ES Frame IQ modulating
        frame_IQ = self._lowlevelencoder.frame_1090es_ppm_modulate_IQ(frame_even, frame_odd)

        # this will usually be called from another thread, so mutex lock mechanism is used during update

        self._mutex.acquire()
        calling_thread = threading.current_thread()
        if calling_thread in self._messages_feed_threads:
            self._messages_feed_threads[calling_thread][type][0] = frame_IQ
        self._mutex.release()

    def register_track_simulation_thread(self,feeder_thread):
        if feeder_thread in self._messages_feed_threads:
            print(feeder_thread,"already registred as a feeder")
        else:
            self._messages_feed_threads[feeder_thread] = {}

            # key : "name of message" value : ["data to be broadcasted", datetime of last broadcast, delay_between 2 messages of this type]
            self._messages_feed_threads[feeder_thread]["identification"] = [None, None, feeder_thread.identitification_message_period_us]
            self._messages_feed_threads[feeder_thread]["register_6116"] = [None, None, feeder_thread.squawk_message_period_us]
            self._messages_feed_threads[feeder_thread]["airborne_position"] = [None, None, feeder_thread.position_message_period_us]
            self._messages_feed_threads[feeder_thread]["surface_position"] = [None, None, feeder_thread.position_message_period_us]
            self._messages_feed_threads[feeder_thread]["airborne_velocity"] = [None, None, feeder_thread.velocity_message_period_us]

    def broadcast_data(self,data):
        length = len(data)
        if length != 0:
            sleep_time = length*0.50e-6*(1.0+1e-6*self._hackrf_broadcaster.getCrystalPPM())
            self._tx_context.last_tx_pos = 0  
            self._mutex.acquire()
            self._tx_context.buffer_length = length
            self._tx_context.buffer = (c_ubyte*self._tx_context.buffer_length).from_buffer_copy(data)
            
            # TODO : need to evaluate if mutex protection is required during full broadcast or
            #        could be reduced to buffer filling (probably can be reduced)
            #        reduced version is when next line mutex.release() is uncommented and
            #        mutex release at the end of this method is commented

            self._mutex.release()

            result = self._hackrf_broadcaster.startTX(hackrfTXCB,self._tx_context)
            if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
                print("startTXError:",result, ",", HackRF.getHackRfErrorCodeName(result))
    
            while self._hackrf_broadcaster.isStreaming():
                time.sleep(sleep_time)

            result = self._hackrf_broadcaster.stopTX()
            if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
                print("stopTXError:",result, ",", HackRF.getHackRfErrorCodeName(result))

            #self._mutex.release() 

    def run(self):

        while not self._do_stop:
            #self._mutex.acquire()
            
            now = datetime.datetime.now(datetime.timezone.utc)
            plane_messages = bytearray()
            sleep_time = 10.0
            for thread_broadcast_schedule in self._messages_feed_threads.values():
                for v in thread_broadcast_schedule.values():
                    #now = datetime.datetime.now(datetime.timezone.utc)
                    v2_sec = v[2]*1e-6
                    if v[1] != None:
                        remaining = v2_sec - (now - v[1]).total_seconds()
                    else:
                        remaining = -float('inf')
                        sleep_time = 0.0
                    # Time throttling: messages are broadcasted only at provided time interval
                    # TODO : Implement UTC syncing mechanism (requires that the actual host clock is UTC synced) ?
                    #        which may be implemented to some accuracy level with ntp or GPS + PPS mechanisms in Python ?
                    if (v[0] != None and len(v[0]) > 0) and remaining <= 0.0:
                        plane_messages.extend(v[0])
                        v[1] = now
                    elif remaining > 0.0:
                        remaining = math.fmod(remaining,v2_sec)
                        if remaining < sleep_time:
                            sleep_time = remaining
                            
            #print("sleep_time1",sleep_time)
            bc_length = len(plane_messages)
            if (bc_length > 0):
                self.broadcast_data(plane_messages)

                elasped = (datetime.datetime.now(datetime.timezone.utc) - now).total_seconds()
                sleep_time -= elasped

                if sleep_time < 0.0:
                    sleep_time = 0.0
                elif sleep_time < 0.5:
                    sleep_time *= 0.1
                else:
                    sleep_time = 0.5

                time.sleep(0.1*sleep_time)
            else:
                time.sleep(0.000001)
            #self._mutex.release()

        # upon exit, reset _do_stop flag in case there is a new start
        self._do_stop = False
