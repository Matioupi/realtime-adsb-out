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

import time

from AbstractTrajectorySimulatorBase import AbstractTrajectorySimulatorBase

class WaypointsTrajectorySimulator(AbstractTrajectorySimulatorBase):
    def __init__(self,mutex,broadcast_thread,aircrafts_info,waypoints_file):
        super().__init__(mutex,broadcast_thread)


    def refresh_delay(self):
        return 0.005


    # TODO : implement waypoint simulation...
    #def update_aircraftinfos(self):
    #    pass