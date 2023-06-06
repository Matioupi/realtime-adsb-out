""" simplest implementation of a trajectory simulation where the simulated
aircraft is randomly distributed inside a circle
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

import random
import datetime, math
from AbstractTrajectorySimulatorBase import AbstractTrajectorySimulatorBase

class FlightPathSimulator(AbstractTrajectorySimulatorBase):
    def __init__(self,mutex,broadcast_thread,aircrafinfos):
        super().__init__(mutex,broadcast_thread,aircrafinfos)
        self._starttime = datetime.datetime.now(datetime.timezone.utc)
        
        self._lat0 = aircrafinfos.lat_deg
        self._lon0 = aircrafinfos.lon_deg

        self._max_alt_m = aircrafinfos.alt_msl_m
        self._max_speed_mps = aircrafinfos.speed_mps

    def refresh_delay(self):
        return 0.005

    def update_aircraftinfos(self):
        
        d0 = self._max_speed_mps * 30.0
        Rlat = (d0/6371000.0)*(180.0/math.pi)
        Rlon = Rlat/math.cos(self._lat0*math.pi/180.0)
        self._aircraftinfos.track_angle_deg = random.uniform(0,360.0)
        self._aircraftinfos.lat_deg = self._lat0 - random.uniform(-Rlat,Rlat)
        self._aircraftinfos.lon_deg = self._lon0 + random.uniform(-Rlon,Rlon)

        self._aircraftinfos.alt_msl_m = random.uniform(1.0,self._max_alt_m)
        self._aircraftinfos.speed_mps = random.uniform(0.0,self._max_speed_mps)
