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
from math import asin, atan2, cos, degrees, radians, sin
from AbstractTrajectorySimulatorBase import AbstractTrajectorySimulatorBase

REFRESH_RATE = 5

def get_point_at_distance(lat1, lon1, d, bearing, R=6371):
    """
    lat: initial latitude, in degrees
    lon: initial longitude, in degrees
    d: target distance from initial
    bearing: (true) heading in degrees
    R: optional radius of sphere, defaults to mean radius of earth
    Returns new lat/lon coordinate {d}km from initial, in degrees
    """
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    a = radians(bearing)
    lat2 = asin(sin(lat1) * cos(d/R) + cos(lat1) * sin(d/R) * cos(a))
    lon2 = lon1 + atan2(
       sin(a) * sin(d/R) * cos(lat1),
        cos(d/R) - sin(lat1) * sin(lat2)
    )
    return (degrees(lat2), degrees(lon2),)

class FlightPathSimulator(AbstractTrajectorySimulatorBase):
    def __init__(self,mutex,broadcast_thread,aircraftinfos):
        super().__init__(mutex,broadcast_thread,aircraftinfos)
        self._starttime = datetime.datetime.now(datetime.timezone.utc)
        
        self._lat0 = aircraftinfos.lat_deg
        self._lon0 = aircraftinfos.lon_deg

        self._max_alt_m = aircraftinfos.alt_msl_m
        self._max_speed_mps = aircraftinfos.speed_mps

    def refresh_delay(self):
        return REFRESH_RATE



    def update_aircraftinfos(self):
        
        dist_spd = ((self._max_speed_mps * 1.852)/3600)*REFRESH_RATE
        
        self._aircraftinfos.lat_deg, self._aircraftinfos.lon_deg = get_point_at_distance(self._aircraftinfos.lat_deg, self._aircraftinfos.lon_deg, dist_spd, self._aircraftinfos.track_angle_deg)

        #self._aircraftinfos.alt_msl_m = random.uniform(1.0,self._max_alt_m)
        self._aircraftinfos.speed_mps += random.uniform(-5,5)
        self._aircraftinfos.track_angle_deg += random.uniform(-4,4)
        
        print("[!] FLIGHT SIM\t\tCallsign: "+self._aircraftinfos.callsign)
        print("    [:] Lat: "+str(self._aircraftinfos.lat_deg)+" | Lon: "+str(self._aircraftinfos.lon_deg)+" | Alt: "+str(self._aircraftinfos.alt_msl_m)+" | Spd: "+str(self._aircraftinfos.speed_mps)+" | Trk Angle: "+str(self._aircraftinfos.track_angle_deg))
