""" Abstract base class for a trajectory simulation

This class provides basic services that will generate and feed broadcasting
thread with appropriate messages.

2 abstract methods need to be overriden in derived classes :
- refresh_delay which should return the simulation timestep in seconds
- update_aircraftinfos which is reponsible for animating the aircraftinfos
  object at each time step, thus making the simulation "alive"

mutex protection occurs when calling replace_message

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

import time
import abc
import threading

from ModeS import ModeS

class AbstractTrajectorySimulatorBase(threading.Thread,abc.ABC):
    def __init__(self,mutex,broadcast_thread,aircraftinfos):
        super().__init__()
        self._mutex = mutex
        self._broadcast_thread = broadcast_thread
        self._aircraftinfos = aircraftinfos

        self._modeSencoder = ModeS(df=17,icao=self._aircraftinfos.icao,ca=self._aircraftinfos.capability)

        self._do_stop = False
    
    # Thread core function
    def run(self):

        is_first_step = True
        while not self._do_stop:
            encoder_changed = False
            # check if modeS encoder needs update
            if self._aircraftinfos.icao_changed or self._aircraftinfos.capability_changed or is_first_step:
                self._modeSencoder.icao = self._aircraftinfos.icao
                self._modeSencoder.ca = self._aircraftinfos.capability
                encoder_changed = True

            if encoder_changed or self._aircraftinfos.callsign_changed:
                self.df_callsign = self._modeSencoder.callsign_encode(self._aircraftinfos.callsign)        
                self._broadcast_thread.replace_message("identification",self.df_callsign)

            if encoder_changed or self._aircraftinfos.squawk_changed:
                self.frame_6116 = self._modeSencoder.modaA_encode(self._aircraftinfos.squawk)
                self._broadcast_thread.replace_message("register_6116",self.frame_6116)

            # message generation only if needed
            if encoder_changed or self._aircraftinfos.on_surface_changed \
                or self._aircraftinfos.lat_changed or self._aircraftinfos.lon_changed or self._aircraftinfos.alt_msl_changed \
                or self._aircraftinfos.type_code_changed or self._aircraftinfos.surveillance_status_changed or self._aircraftinfos.nicsupb_changed \
                or self._aircraftinfos.timesync_changed:
                if not self._aircraftinfos.on_surface:
                    (self.df_pos_even, self.df_pos_odd) = self._modeSencoder.df_encode_airborne_position(self._aircraftinfos.lat_deg, self._aircraftinfos.lon_deg, self._aircraftinfos.alt_msl_ft, \
                        self._aircraftinfos.type_code, self._aircraftinfos.surveillance_status, self._aircraftinfos.nicsupb, self._aircraftinfos.timesync)
                    self._broadcast_thread.replace_message("airborne_position",self.df_pos_even,self.df_pos_odd)
                    self._broadcast_thread.replace_message("surface_position",[], [])                        
                else:
                    (self.df_pos_even, self.df_pos_odd) = self._modeSencoder.df_encode_surface_position(self._aircraftinfos.lat_deg, self._aircraftinfos.lon_deg, self._aircraftinfos.alt_msl_ft, \
                        self._aircraftinfos.type_code, self._aircraftinfos.surveillance_status, self._aircraftinfos.nicsupb, self._aircraftinfos.timesync)
                    self._broadcast_thread.replace_message("surface_position",self.df_pos_even,self.df_pos_odd)
                    self._broadcast_thread.replace_message("airborne_position",[], [])

            if encoder_changed or self._aircraftinfos.speed_changed or self._aircraftinfos.track_angle_changed or self._aircraftinfos.vspeed_changed:
                self.df_velocity = self._modeSencoder.df_encode_ground_velocity(self._aircraftinfos.speed_kt, self._aircraftinfos.track_angle_deg, self._aircraftinfos.vspeed_ftpmin) 
                self._broadcast_thread.replace_message("airborne_velocity",self.df_velocity)

            is_first_step = False
            self.update_aircraftinfos()         # update_aircraftinfos() : abstract method that need to be implemented i nderived classes
            time.sleep(self.refresh_delay())    # refresh_delay()        : abstract method that need to be implemented i nderived classes

        # upon exit, reset _do_stop flag in case there is a new start
        self._do_stop = False

    def stop(self):
        self._do_stop = True

    @abc.abstractmethod
    def refresh_delay(self):
        ...

    @abc.abstractmethod
    def update_aircraftinfos(self):
        ...