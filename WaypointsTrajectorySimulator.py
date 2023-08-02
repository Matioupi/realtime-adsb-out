""" Implementation of a trajectory simulation where the simulated aircraft
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
	def __init__(self,mutex,broadcast_thread,aircraftinfos,waypoints_file,logfile):
		super().__init__(mutex,broadcast_thread,aircraftinfos,waypoints_file,logfile)
		self._starttime = datetime.datetime.now(datetime.timezone.utc)
		self._lat0 = aircraftinfos.lat_deg
		self._lon0 = aircraftinfos.lon_deg
		self._logfile = logfile
		
	def refresh_delay(self):
		return 0.005
    
	def update_aircraftinfos(self):
		with open(self._waypoints_file, 'r') as wp:
		# waypoints CSV format: "<0:callsign>,<1:lat>,<2:lon>,<3:alt>,<4:speed>,<5:track angle>,<6:iterate time>"
			for line in wp:
				posi = line.split(",")
				print("[!] WAYPOINTS TRAJECTORY\tCallsign: "+self._aircraftinfos.callsign)
				print("    [:] Lat: "+posi[1]+" | Lon: "+posi[2]+" | Alt: "+posi[3]+" | Spd: "+posi[4]+" | Trk Angle: "+posi[5]+" | ValidTime: "+posi[6])
		
		# Write to logfile -> CSV format: DATETIME,CALLSIGN,LAT,LONG,ALT,SPD,TRKANGLE
		with open(self._logfile,"a") as fLog:
			now=str(datetime.now())
			fLog.write("\n"+now+","+self._aircraftinfos.callsign+","+str(self._aircraftinfos.lat_deg)+","+str(self._aircraftinfos.lon_deg)+","+str(self._aircraftinfos.alt_msl_m)+","+str(self._aircraftinfos.speed_mps)+","+str(self._aircraftinfos.track_angle_deg))
