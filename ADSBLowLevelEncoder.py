""" This class is responsible for low level encoding of IQ sample

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
from CustomDecorators import *
import numpy

@Singleton
class ADSBLowLevelEncoder:

    def __init__(self):
        self._adsb_frame_preamble = [0xA1,0x40]
        self._adsb_frame_pause = [0]*4

        # Build a manchester encoding lookup table
        self._manchester_lookup = []
        for i in range(256):
            me = self.manchester_encode(i)
            self._manchester_lookup.append([127*val for pair in zip(me, me) for val in pair])

        # Build preamble and pause manchester encoded versions
        me_bits = numpy.unpackbits(numpy.asarray(self._adsb_frame_preamble, dtype=numpy.uint8))
        self._adsb_frame_preamble_IQ = [127*val for pair in zip(me_bits, me_bits) for val in pair]
        self._adsb_frame_pause_IQ = self._adsb_frame_pause*16

        self._len_pre_IQ = len(self._adsb_frame_preamble_IQ)
        self._len_pause_IQ = len(self._adsb_frame_pause_IQ)

###############################################################
# Further work on fork
# Copyright (C) 2017 David Robinson
    def extract_bit(self, byte, pos):
        """
        Extract a bit from a given byte using MS ordering.
        ie. B7 B6 B5 B4 B3 B2 B1 B0
        """
        return (byte >> pos) & 0x01

    def manchester_encode(self, byte):
        """
        Encode a byte using Manchester encoding. Returns an array of bits.
        Adds two start bits (1, 1) and one stop bit (0) to the array.
        """
        manchester_encoded = []

        # Encode byte
        for i in range(7, -1, -1):
            if self.extract_bit(byte, i):
                manchester_encoded.extend([1,0])
            else:
                manchester_encoded.extend([0,1])

        return manchester_encoded

    def frame_1090es_ppm_modulate_IQ(self, even, odd = []):
        """
        Args:
            even and odd: The data frames that need to be converted to PPM
        Returns:
            The bytearray of the IQ samples for PPM modulated data
        """

        length_even = len(even)
        length_odd  = len(odd)
      
        if (length_even != 0 and length_odd == 0):
            IQ = bytearray(32*length_even+2*self._len_pause_IQ+self._len_pre_IQ)
            pos = self._len_pause_IQ
            IQ[pos:pos+self._len_pre_IQ] = self._adsb_frame_preamble_IQ
            pos += self._len_pre_IQ

            tmp = []
            for b in even:
                tmp.extend(self._manchester_lookup[b])
            IQ[pos:pos+32*length_even] = tmp
            
            return IQ

        elif (length_even != 0 and length_odd != 0):
            IQ = bytearray(32*(length_even+length_odd)+2*self._len_pre_IQ+3*self._len_pause_IQ)
            pos = self._len_pause_IQ
            IQ[pos:pos+self._len_pre_IQ] = self._adsb_frame_preamble_IQ
            pos += self._len_pre_IQ

            tmp = []
            for b in even:
                tmp.extend(self._manchester_lookup[b])
            length_even_IQ = 32*length_even
            IQ[pos:pos+length_even_IQ] = tmp
            pos += length_even_IQ

            pos += self._len_pause_IQ

            IQ[pos:pos+self._len_pre_IQ] = self._adsb_frame_preamble_IQ
            pos += self._len_pre_IQ

            tmp = []
            for b in odd:
                tmp.extend(self._manchester_lookup[b])

            IQ[pos:pos+32*length_odd] = tmp
        
            return IQ

        else:

            return None
