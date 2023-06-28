""" Dynamically generates a randomized conical ship courses from initial values
shipCloneGen()
-------------------------------------------------------
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
import datetime
import os
from math import asin, atan2, cos, degrees, radians, sin

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
    
def shipCloneGen(ship_id, lat, lon, duration=60):
    dist = 0.007716667
    outputFile = open("ship="+ship_id+".csv", "a")
    outputFile.write("DATETIME,SHIP_ID,LAT,LON,HEADING")
    
    # WRITES 1 LINE PER FUNCTION
    for time from 0 to duration:
        # Write to logfile -> CSV format: DATETIME,SHIP_ID,LAT,LON,HEADING
        now=str(datetime.now())
        dist += 0.00
        bearing = random.uniform(0,360)
        lat,lon = get_point_at_distance(lat,lon,dist,bearing)
        outputFile.write("\n"+now,","+ship_id+","+str(lat)+","+str(lon))
        
def main():
    ship_id = "BIGSHIP"
    lat = 0
    lon = 0
    duration = 10
    

        
