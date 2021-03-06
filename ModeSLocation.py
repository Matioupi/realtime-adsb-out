import math
from CustomDecorators import *

class ModeSLocation:
    """This class does ModeS/ADSB Location calulations"""

    def __init__(self):
        self.latz = 15
    
##########################################################################

# Copyright 2010, 2012 Nick Foster
# # This file is part of gr-air-modes
# 
# gr-air-modes is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# gr-air-modes is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with gr-air-modes; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 
###############################################################
# Further work on fork
# Copyright (C) 2017 David Robinson
    def encode_alt_modes(self, alt, bit13):
        # need to better understand as the >50175 feet not working
        mbit = False
        qbit = True
        # For altitudes -1000<=X<=50175 feet, set bit 8 AKA the Q bit to true which means 25 feet resoulution
        # For >50175 set the qbit to False and use 100 feet resoultion
        if alt > 50175:
            qbit = False
            encalt = int((int(alt) + 1000) / 100)
        else:
            qbit = True
            encalt = int((int(alt) + 1000) / 25)

        if bit13 is True:
            tmp1 = (encalt & 0xfe0) << 2
            tmp2 = (encalt & 0x010) << 1

        else:
            tmp1 = (encalt & 0xff8) << 1
            tmp2 = 0

        return (encalt & 0x0F) | tmp1 | tmp2 | (mbit << 6) | (qbit << 4)



    def nz(self, ctype):
        """
        Number of geographic latitude zones between equator and a pole. It is set to NZ = 15 for Mode-S CPR encoding
        https://adsb-decode-guide.readthedocs.io/en/latest/content/cpr.html
        """
        return 4 * self.latz - ctype

    def dlat(self, ctype, surface):
        if surface == 1:
            tmp = 90.0
        else:
            tmp = 360.0

        nzcalc = self.nz(ctype)
        if nzcalc == 0:
            return tmp
        else:
            return tmp / nzcalc

    def nl(self, declat_in):
        if abs(declat_in) >= 87.0:
            return 1.0
        return math.floor( (2.0*math.pi) / math.acos(1.0- (1.0-math.cos(math.pi/(2.0*self.latz))) / math.cos( (math.pi/180.0)*abs(declat_in) )**2 ))

    def dlon(self, declat_in, ctype, surface):
        if surface:
            tmp = 90.0
        else:
            tmp = 360.0
        nlcalc = max(self.nl(declat_in)-ctype, 1)
        return tmp / nlcalc

    # encode CPR position
    # https://adsb-decode-guide.readthedocs.io/en/latest/content/cpr.html
    # compact position reporting
    #@Timed
    def cpr_encode(self, lat, lon, ctype, surface):
        if surface is True:
            scalar = 2.**19
        else:
            scalar = 2.**17

        #encode using 360 constant for segment size.
        dlati = self.dlat(ctype, False)
        yz = math.floor(scalar * ((lat % dlati)/dlati) + 0.5)
        rlat = dlati * ((yz / scalar) + math.floor(lat / dlati))
        
        #encode using 360 constant for segment size.
        dloni = self.dlon(lat, ctype, False)
        xz = math.floor(scalar * ((lon % dloni)/dloni) + 0.5)
        
        yz = int(yz) & (2**17-1)
        xz = int(xz) & (2**17-1)
        
        return (yz, xz) #lat, lon
