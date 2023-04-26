""" implementation of a trajectory simulation where the simulated aircraft
is following a preplanned trajectory

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

import datetime
import time

from AbstractTrajectorySimulatorBase import AbstractTrajectorySimulatorBase

class WaypointsTrajectorySimulator(AbstractTrajectorySimulatorBase):
    def __init__(self,mutex,broadcast_thread,aircraftinfos,waypoints_file):
        super().__init__(mutex,broadcast_thread, aircraftinfos,waypoints_file)
        self._starttime = datetime.datetime.now(datetime.timezone.utc)
        
        self._lat0 = aircraftinfos.lat_deg
        self._lon0 = aircraftinfos.lon_deg
        
    def refresh_delay(self):
        return 0.005
        
    def update_aircraftinfos(self):
        
        with open(self._waypoints_file, 'r') as wp:
	    # Line format: "<0:lat> <1:lon> <2:alt> <3:speed> <4:track angle> <5:iterate time>"
            for line in wp:
                posi = line.split()
                print("[!] Setting "+self._aircraftinfos.callsign+"'s data")
                print("    [:] Lat: "+posi[0]+" | Long: "+posi[1]+" | Alt: "+posi[2]+" | Speed: "+posi[3]+" | Trk Angle: "+posi[4]+" | ValidTime: "+posi[5])
                self._aircraftinfos.lat_deg = float(posi[0])
                self._aircraftinfos.lon_deg = float(posi[1])
                self._aircraftinfos.alt_msl_m  = float(posi[2])
                self._aircraftinfos.speed_mps = float(posi[3])
                self._aircraftinfos.track_angle_deg = float(posi[4]) #valid: 0.0-360.0
                time.sleep(int(posi[5])) #int, in seconds
