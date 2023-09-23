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
import random
import string
from AbstractTrajectorySimulatorBase import AbstractTrajectorySimulatorBase

LAT_LON_SQUARE = 1.0000

class FixedTrajectorySimulator(AbstractTrajectorySimulatorBase):
	def __init__(self,mutex,broadcast_thread,aircraftinfos,waypoints_file,logfile):
		super().__init__(mutex,broadcast_thread,aircraftinfos,waypoints_file,logfile)

	def refresh_delay(self):
		return 0.5

	def update_aircraftinfos(self):
		chars = string.ascii_uppercase + string.digits
		self._icao = '0x'+''.join(random.sample(string.digits,6))
		self._aircraftinfos.callsign =  ''.join(random.sample(chars, 8))
		self._aircraftinfos.lat_deg += random.uniform(-LAT_LON_SQUARE,LAT_LON_SQUARE)
		self._aircraftinfos.lon_deg += random.uniform(-1.0000,1.0000)
		self._aircraftinfos.alt_msl_m += random.uniform(-self._aircraftinfos.alt_msl_m,self._aircraftinfos.alt_msl_m)
		self._aircraftinfos.speed_mps += random.uniform(-self._aircraftinfos.speed_mps,self._aircraftinfos.speed_mps)
		self._aircraftinfos.track_angle_deg += random.uniform(0,360)
    	
    	# Track angle 0-360 wrapping
		if self._aircraftinfos.track_angle_deg < 0:
			self._aircraftinfos.track_angle_deg += 360
		elif self._aircraftinfos.track_angle_deg > 360:
			self._aircraftinfos.track_angle_deg -= 360

		print("[!] FIXED TRAJECTORY\t\tICAO: "+self._icao+"\t\tCallsign: "+self._aircraftinfos.callsign)
		print("    [:] Lat: "+str(self._aircraftinfos.lat_deg)+" | Lon: "+str(self._aircraftinfos.lon_deg)+" | Alt: "+str(self._aircraftinfos.alt_msl_m)+" | Spd: "+str(self._aircraftinfos.speed_mps)+" | Trk Angle: "+str(self._aircraftinfos.track_angle_deg))
        
		# Write to logfile -> CSV format: DATETIME,CALLSIGN,LAT,LONG,ALT,SPD,TRKANGLE
		with open(self._logfile,"a") as fLog:
			now=str(datetime.now())
			fLog.write("\n"+now+","+self._aircraftinfos.callsign+","+str(self._aircraftinfos.lat_deg)+","+str(self._aircraftinfos.lon_deg)+","+str(self._aircraftinfos.alt_msl_m)+","+str(self._aircraftinfos.speed_mps)+","+str(self._aircraftinfos.track_angle_deg))
