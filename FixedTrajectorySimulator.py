""" Simplest implementation of a trajectory simulation where the simulated
aircraft is steady at the provided position

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
from datetime import datetime

from AbstractTrajectorySimulatorBase import AbstractTrajectorySimulatorBase

class FixedTrajectorySimulator(AbstractTrajectorySimulatorBase):
    def __init__(self,mutex,broadcast_thread,aircraftinfos,waypoints_file,logfile):
        super().__init__(mutex,broadcast_thread,aircraftinfos,waypoints_file,logfile)

    def refresh_delay(self):
        return 0.5

    def update_aircraftinfos(self):
        print("[!] FIXED TRAJECTORY\t\tCallsign: "+self._aircraftinfos.callsign)
        print("    [:] Lat: "+str(self._aircraftinfos.lat_deg)+" | Lon: "+str(self._aircraftinfos.lon_deg)+" | Alt: "+str(self._aircraftinfos.alt_msl_m)+" | Spd: "+str(self._aircraftinfos.speed_mps)+" | Trk Angle: "+str(self._aircraftinfos.track_angle_deg))
        
        # Write to logfile -> CSV format: DATETIME,CALLSIGN,LAT,LONG,ALT,SPD,TRKANGLE
        with open(self._logfile,"a") as fLog:
            now=str(datetime.now())
            fLog.write("\n"+now+","+self._aircraftinfos.callsign+","+str(self._aircraftinfos.lat_deg)+","+str(self._aircraftinfos.lon_deg)+","+str(self._aircraftinfos.alt_msl_m)+","+str(self._aircraftinfos.speed_mps)+","+str(self._aircraftinfos.track_angle_deg))
