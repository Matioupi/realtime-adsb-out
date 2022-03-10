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
    def __init__(self,mutex,airborne_position_refresh_period = 150000):
        super().__init__()
        self._mutex = mutex

        self._lowlevelencoder = ADSBLowLevelEncoder()

        self._messages = {}
        # key : "name of message" value : ["data to be broadcasted", datetime of last broadcast, delay_between 2 messages of this type]
        self._messages["identification"] = [None, None, 10000000]    # max should be 15s
        self._messages["register_6116"] = [None, None, 800000]       # TODO : specs says that interval should be randomized between [0.7s;0.9s] and max is 1.0s
        self._messages["airborne_position"] = [None, None, airborne_position_refresh_period]   # max should be 0.2s
        self._messages["surface_position"] = [None, None, 150000]    # max should be 0.2s
        self._messages["airborne_velocity"] = [None, None, 1200000]  # max should be 1.3s

        # Initialize pyHackRF library
        result = HackRF.initialize()
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :",result, ",", HackRF.getHackRfErrorCodeName(result))

        # Initialize HackRF instance (could pass board serial or index if specific board is needed)
        self._hackrf_broadcaster = HackRF()

        # Do requiered settings
        # so far hard-coded e.g. gain and disabled amp are specific to hardware test setup
        # with hackrf feeding a flight aware dongle through cable + attenuators (-50dB)
        result = self._hackrf_broadcaster.open()
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :",result, ",", HackRF.getHackRfErrorCodeName(result))

        result = self._hackrf_broadcaster.setSampleRate(2000000)
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :",result, ",", HackRF.getHackRfErrorCodeName(result))

        result = self._hackrf_broadcaster.setBasebandFilterBandwidth(HackRF.computeBaseBandFilterBw(2000000))
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :",result, ",", HackRF.getHackRfErrorCodeName(result))

        #result = self.hackrf_broadcaster.setFrequency(868000000)   # free frequency for over the air brodcast tests
        result = self._hackrf_broadcaster.setFrequency(1090000000)   # do not use 1090MHz for actual over the air broadcasting
                                                                    # only if you use wire feed (you'll need attenuators in that case)
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :",result, ",", HackRF.getHackRfErrorCodeName(result))

        result = self._hackrf_broadcaster.setTXVGAGain(4)            # week gain (used for wire feed + attenuators)
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :",result, ",", HackRF.getHackRfErrorCodeName(result))

        result = self._hackrf_broadcaster.setAmplifierMode(LibHackRfHwMode.HW_MODE_OFF)
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :",result, ",", HackRF.getHackRfErrorCodeName(result))        

        self._tx_context = hackrf_tx_context()

        self._do_stop = False

    # do hackRF lib and instance cleanup at object destruction time
    def __del__(self):
        result = self._hackrf_broadcaster.close()
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :",result, ",", HackRF.getHackRfErrorCodeName(result))

        result = HackRF.deinitialize()
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :",result, ",", HackRF.getHackRfErrorCodeName(result))

    def stop(self):
        self._do_stop = True

    # updates the next data to be broadcaster for a given message type
    def replace_message(self,type,frame_even,frame_odd = []):
        frame_ppm = self._lowlevelencoder.frame_1090es_ppm_modulate(frame_even, frame_odd)
        frame_IQ = self._lowlevelencoder.hackrf_raw_IQ_format(frame_ppm)

        # this will usuallyy be called from another thread, so mutex lock mecanism is used during update
        self._mutex.acquire()
        self._messages[type][0] = frame_IQ
        self._mutex.release()

    def broadcast_one_message(self,data): 
        self._tx_context.last_tx_pos = 0  
        self._mutex.acquire()        
        self._tx_context.buffer_length = len(data)
        self._tx_context.buffer = (c_ubyte*self._tx_context.buffer_length).from_buffer_copy(data)
        # TODO : need to evaluate if mutex protection is requiered during full broadcast or
        #        could be reduced to buffer filling (probably can be reduced)
        #        reduced version is when next line mutex.release() is uncommented and
        #        mutex release at the end of this method is commented

        self._mutex.release()

        result = self._hackrf_broadcaster.startTX(hackrfTXCB,self._tx_context)

        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :",result, ",", HackRF.getHackRfErrorCodeName(result))

        while self._hackrf_broadcaster.isStreaming():
            time.sleep(0.00001)

        result = self._hackrf_broadcaster.stopTX()
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :",result, ",", HackRF.getHackRfErrorCodeName(result))
         
        #self.mutex.release() 

    def run(self):
        while not self._do_stop:
            for k,v in self._messages.items():
                now = datetime.datetime.now(datetime.timezone.utc)
                # Time throttling : messages are broadcasted only at provided time intervall
                # TODO : implement UTC syncing mecanism (requiered that the actual host clock is UTC synced)
                #        which can be implemented to some accuracy level with ntp or GPS + PPS mecanisms
                if (v[0] != None and len(v[0]) > 0) and (v[1] == None or (now - v[1]) >= datetime.timedelta(seconds=v[2] // 1000000,microseconds=v[2] % 1000000)):
                    self.broadcast_one_message(v[0])
                    v[1] = now
            time.sleep(0.0001)  # this loop will run at 10 kHz max

        # upon exit, reset _do_stop flag in case there is a new start
        self._do_stop = False