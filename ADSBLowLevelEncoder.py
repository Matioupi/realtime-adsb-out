from CustomDecorators import *
import numpy

@Singleton
class ADSBLowLevelEncoder:
    """
    Hamming and Manchester Encoding example

    Author: Joel Addison
    Date: March 2013

    Functions to do (7,4) hamming encoding and decoding, including error detection
    and correction.
    Manchester encoding and decoding is also included, and by default will use
    least bit ordering for the byte that is to be included in the array.
    """

    def __init__(self):
        self.adsb_frame_preamble = [0xA1,0x40]
        self.adsb_frame_pause = [0]*70
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
                manchester_encoded.extend([0,1])
            else:
                manchester_encoded.extend([1,0])

        return manchester_encoded

    def frame_1090es_ppm_modulate(self, even, odd = []):
        """
        Args:
            even and odd: The data frames that need to be converted to PPM
        Returns:
            The bytearray of the PPM data
        """
        ppm = [ ]

        length_even = len(even)
        length_odd  = len(odd)

        if (length_even != 0):
            ppm.extend(self.adsb_frame_pause)      # pause
            ppm.extend(self.adsb_frame_preamble)   # preamble
            
            for i in range(length_even):
                word16 = numpy.packbits(self.manchester_encode(~even[i]))
                ppm.extend(word16[0:2])
            
            ppm.extend(self.adsb_frame_pause)  # pause

        if (length_odd != 0):
            ppm.extend(self.adsb_frame_pause)        # pause
            ppm.extend(self.adsb_frame_preamble)     # preamble

            for i in range(length_odd):
                word16 = numpy.packbits(self.manchester_encode(~odd[i]))
                ppm.extend(word16[0:2])

            ppm.extend(self.adsb_frame_pause)  # pause
        
        return bytearray(ppm)

    def hackrf_raw_IQ_format(self, ppm):
        """
        Args:
            ppm: this is some data in ppm (pulse position modulation) which will be converted into
                 hackRF raw IQ sample format, ready to be broadcasted
            
        Returns:
            bytearray: containing the IQ data
        """
        signal = []
        bits = numpy.unpackbits(numpy.asarray(ppm, dtype=numpy.uint8))
        for bit in bits:
            if bit == 1:
                I = 127
                Q = 127
            else:
                I = 0
                Q = 0
            signal.append(I)
            signal.append(Q)

        return bytearray(signal)