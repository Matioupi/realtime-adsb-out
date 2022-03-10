""" simplest implementation of a trajectory simulation where the simulated
aircraft is flying a pseudo circle around center position at max load factor

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

import datetime, math
from AbstractTrajectorySimulatorBase import AbstractTrajectorySimulatorBase

class PseudoCircleTrajectorySimulator(AbstractTrajectorySimulatorBase):
    def __init__(self,mutex,broadcast_thread,aircrafinfos):
        super().__init__(mutex,broadcast_thread,aircrafinfos)
        self._starttime = datetime.datetime.now(datetime.timezone.utc)
        
        self._lasttime = self._starttime

        self._lat0 = aircrafinfos.lat_deg
        self._lon0 = aircrafinfos.lon_deg

    def refresh_delay(self):
        return 0.005

    def update_aircraftinfos(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        elapsed = (now - self._lasttime).total_seconds()
        turn_rate = self.getTurnRate()
        R = self.getTurnRadius()
        Rlat = (R/6371000.0)*(180.0/math.pi)
        ta = self._aircraftinfos.track_angle_deg - (turn_rate*elapsed)*(180.0/math.pi)
        ta = math.fmod(ta,360.0)
        self._aircraftinfos.track_angle_deg = ta
        self._aircraftinfos.lat_deg = self._lat0 - Rlat*math.sin(self._aircraftinfos.track_angle_deg*math.pi/180.0)
        self._aircraftinfos.lon_deg = self._lon0 + Rlat/math.cos(self._aircraftinfos.lat_deg*math.pi/180.0)*math.cos(self._aircraftinfos.track_angle_deg*math.pi/180.0)
        self._lasttime = now

    def getTurnRate(self):
        tr = (9.81/self._aircraftinfos.speed_mps)*math.sqrt(self._aircraftinfos.maxloadfactor**2.0 - 1.0)
        return tr

    def getTurnRadius(self):
        return self._aircraftinfos.speed_mps/self.getTurnRate()