""" This class holds the aircraft states from the ADS-B point of view

It is refreshed by the simulation thread (or sensor feed thread) and will
be used to provide broadcasted informations

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

import math

class AircraftInfos:
    def __init__(self,icao,callsign,squawk,
                      lat_deg,lon_deg,alt_msl_ft,speed_kph,vspeed_ftpmin,maxloadfactor,track_angle_deg,
                      timesync,capability,type_code,surveillance_status,nicsupb,on_surface):

        self._icao = int(icao,16)
        self._oldicao = self._icao
   
        self._callsign = callsign
        self._oldcallsign = self._callsign

        self._squawk = squawk
        self._oldsquawk = self._squawk

        self._lat_deg = float(lat_deg)
        self._oldlat_deg = self._lat_deg

        self._lon_deg = float(lon_deg)
        self._oldlon_deg = self._lon_deg

        self._alt_msl_m = float(alt_msl_ft)*0.3048
        self._oldalt_msl_m = self._alt_msl_m

        self._speed_mps = float(speed_kph)/3.6
        self._oldspeed_mps = self._speed_mps

        self._vspeed_mps = float(vspeed_ftpmin)*0.00508
        self._oldvspeed_mps = self._vspeed_mps

        self._maxloadfactor = float(maxloadfactor)
        self._oldmaxloadfactor = self._maxloadfactor

        self._track_angle_deg = math.fmod(float(track_angle_deg),360.0)
        self._oldtrack_angle_deg = self._track_angle_deg

        self._timesync = int(timesync)
        self._oldtimesync = self._timesync

        self._capability = int(capability)
        self._oldcapability = self._capability

        self._type_code = int(type_code)
        self._oldtype_code = self._type_code

        self._surveillance_status = int(surveillance_status)
        self._oldsurveillance_status = self._surveillance_status

        self._nicsupb = int(nicsupb)
        self._oldnicsupb = self._nicsupb

        self._on_surface = on_surface
        self._oldon_surface = self._on_surface

    ################################################
    @property
    def icao(self):
        return self._icao

    @icao.setter
    def icao(self,value):
        self._oldicao = self._icao
        self._icao = value
    
    @property
    def icao_changed(self):
        return self._icao != self._oldicao
    ################################################
    @property
    def callsign(self):
        return self._callsign

    @callsign.setter
    def callsign(self,value):
        self._oldcallsign = self._callsign
        self._callsign = value

    @property
    def callsign_changed(self):
        return self._callsign != self._oldcallsign
    ################################################
    @property
    def squawk(self):
        return self._squawk

    @squawk.setter
    def squawk(self,value):
        self._oldsquawk = self._squawk
        self._squawk = value

    @property
    def squawk_changed(self):
        return self._squawk != self._oldsquawk
    ################################################
    @property
    def lat_deg(self):
        return self._lat_deg

    @lat_deg.setter
    def lat_deg(self,value):
        self._oldlat_deg = self._lat_deg
        self._lat_deg = value

    @property
    def lat_changed(self):
        return self._lat_deg != self._oldlat_deg
    ################################################
    @property
    def lon_deg(self):
        return self._lon_deg

    @lon_deg.setter
    def lon_deg(self,value):
        self._oldlon_deg = self._lon_deg
        self._lon_deg = value

    @property
    def lon_changed(self):
        return self._lon_deg != self._oldlon_deg
    ################################################
    @property
    def alt_msl_m(self):
        return self._alt_msl_m

    @property
    def alt_msl_ft(self):
        return self._alt_msl_m / 0.3048

    @alt_msl_m.setter
    def alt_msl_m(self,value):
        self._oldalt_msl_m = self._alt_msl_m
        self._alt_msl_m = value

    @property
    def alt_msl_changed(self):
        return self._alt_msl_m != self._oldalt_msl_m
    ################################################
    @property
    def speed_mps(self):
        return self._speed_mps

    @property
    def speed_kt(self):
        return self._speed_mps*1.94384449244

    @speed_mps.setter
    def speed_mps(self,value):
        self._oldspeed_mps != self._speed_mps
        self._speed_mps = value

    @property
    def speed_changed(self):
        return self._speed_mps != self._oldspeed_mps
    ################################################
    @property
    def vspeed_mps(self):
        return self._vspeed_mps

    @property
    def vspeed_ftpmin(self):
        return self._vspeed_mps * 196.850393701

    @vspeed_mps.setter
    def vspeed_mps(self,value):
        self._oldvspeed_mps = self._vspeed_mps
        self._vspeed_mps = value

    @property
    def vspeed_changed(self):
        return self._vspeed_mps != self._oldvspeed_mps
    ################################################
    @property
    def maxloadfactor(self):
        return self._maxloadfactor

    @maxloadfactor.setter
    def maxloadfactor(self,value):
        self._oldmaxloadfactor = self._maxloadfactor
        self._maxloadfactor = value

    @property
    def maxloadfactor_changed(self):
        return self._maxloadfactor != self._oldmaxloadfactor
    ################################################
    @property
    def track_angle_deg(self):
        return self._track_angle_deg

    @track_angle_deg.setter
    def track_angle_deg(self,value):
        self._oldtrack_angle_deg = self._track_angle_deg
        self._track_angle_deg = value

    @property
    def track_angle_changed(self):
        return self._track_angle_deg != self._oldtrack_angle_deg
    ################################################
    @property
    def timesync(self):
        return self._timesync

    @timesync.setter
    def timesync(self,value):
        self._oldtimesync = self._timesync
        self._timesync = value

    @property
    def timesync_changed(self):
        return self._timesync != self._oldtimesync
    ################################################
    @property
    def capability(self):
        return self._capability

    @capability.setter
    def capability(self,value):
        self._oldcapability = self._capability
        self._capability = value

    @property
    def capability_changed(self):
        return self._capability != self._oldcapability
    ################################################
    @property
    def type_code(self):
        return self._type_code

    @type_code.setter
    def type_code(self,value):
        self._oldtype_code = self._type_code
        self._type_code = value

    @property
    def type_code_changed(self):
        return self._type_code != self._oldtype_code
    ################################################
    @property
    def surveillance_status(self):
        return self._surveillance_status

    @surveillance_status.setter
    def surveillance_status(self,value):
        self._oldsurveillance_status = self._surveillance_status
        self._surveillance_status = value

    @property
    def surveillance_status_changed(self):
        return self._surveillance_status != self._oldsurveillance_status
    ################################################
    @property
    def nicsupb(self):
        return self._nicsupb

    @nicsupb.setter
    def nicsupb(self,value):
        self._oldnicsupb = self._nicsupb
        self._nicsupb = value

    @property
    def nicsupb_changed(self):
        return self._nicsupb != self._oldnicsupb
    ################################################
    @property
    def on_surface(self):
        return self._on_surface

    @on_surface.setter
    def on_surface(self,value):
        self._oldon_surface = self._on_surface
        self._on_surface = value

    @property
    def on_surface_changed(self):
        return self._on_surface != self._oldon_surface