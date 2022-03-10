from ModeSLocation import ModeSLocation
import math
import numpy
###############################################################
# Further work on fork
# Copyright (C) 2017 David Robinson
class ModeS:
    """This class handles the ModeS ADSB manipulation
    """
    
    def __init__(self,df,icao,ca):
        self.df = df        # as far as I understand specification, this should be :
                            # 17 if the broadcast source is an aircraft
                            # 18 if the broadcast source is some other ADSB facility (tower)

        self.icao = icao    # 24 bits icao registration code
        self.ca = ca        # capability see §3.1.2.5.2.2.1
                            # (will usually be 5 for level 2 transponder and airborne)

    def df_frame_start(self):
        """
        This will build the usual df frame start
        """        
        frame = []
        frame.append((self.df << 3) | self.ca)
        frame.append((self.icao >> 16) & 0xff)
        frame.append((self.icao >> 8) & 0xff)
        frame.append((self.icao) & 0xff)
        return frame

    def df_frame_append_crc(self,frame):
        frame_str = "{0:02x}{1:02x}{2:02x}{3:02x}{4:02x}{5:02x}{6:02x}{7:02x}{8:02x}{9:02x}{10:02x}".format(*frame[0:11])
        frame_crc = self.bin2int(self.modes_crc(frame_str + "000000", encode=True))
        frame.append((frame_crc >> 16) & 0xff)
        frame.append((frame_crc >> 8) & 0xff)
        frame.append((frame_crc) & 0xff)

    # Ref :
    # ICAO Annex 10 : Aeronautical Telecommunications
    # Volume IV : Surveillance and Collision Avoidance Systems
    # Figure C-1. Extended Squitter Airborne Position
    # "Register 05_16"

    def df_encode_airborne_position(self, lat, lon, alt, tc, ss, nicsb, timesync):
        """
        This will encode even and odd frames from airborne position extended squitter message
        tc = type code (§C2.3.1)
        ss = surveillance status : 0 = no condition information
                                   1 = permanent alert (emergency condition)
                                   2 = temporary alert (change in Mode A identity code other than emergency condition)
                                   3 = SPI condition
        nicsb = NIC supplement-B (§C.2.3.2.5)
        """

        location = ModeSLocation()
        enc_alt =	location.encode_alt_modes(alt, False)
        
        #encode that position
        (evenenclat, evenenclon) = location.cpr_encode(lat, lon, False, False)
        (oddenclat, oddenclon)   = location.cpr_encode(lat, lon, True, False)

        ff = 0
        df_frame_even_bytes = self.df_frame_start()
        # data
        df_frame_even_bytes.append((tc<<3) | (ss<<1) | nicsb)
        df_frame_even_bytes.append((enc_alt>>4) & 0xff)
        df_frame_even_bytes.append((enc_alt & 0xf) << 4 | (timesync<<3) | (ff<<2) | (evenenclat>>15))
        df_frame_even_bytes.append((evenenclat>>7) & 0xff)
        df_frame_even_bytes.append(((evenenclat & 0x7f) << 1) | (evenenclon>>16))
        df_frame_even_bytes.append((evenenclon>>8) & 0xff)
        df_frame_even_bytes.append((evenenclon   ) & 0xff)

        self.df_frame_append_crc(df_frame_even_bytes)

        ff = 1
        df_frame_odd_bytes = self.df_frame_start()
        # data
        df_frame_odd_bytes.append((tc<<3) | (ss<<1) | nicsb)
        df_frame_odd_bytes.append((enc_alt>>4) & 0xff)
        df_frame_odd_bytes.append((enc_alt & 0xf) << 4 | (timesync<<3) | (ff<<2) | (oddenclat>>15))
        df_frame_odd_bytes.append((oddenclat>>7) & 0xff)
        df_frame_odd_bytes.append(((oddenclat & 0x7f) << 1) | (oddenclon>>16))
        df_frame_odd_bytes.append((oddenclon>>8) & 0xff)
        df_frame_odd_bytes.append((oddenclon   ) & 0xff)

        self.df_frame_append_crc(df_frame_odd_bytes)

        return (df_frame_even_bytes, df_frame_odd_bytes)

    # Ref :
    # ICAO Annex 10 : Aeronautical Telecommunications
    # Volume IV : Surveillance and Collision Avoidance Systems
    # Figure C-1. Extended Squitter Surface Position
    # "Register 06_16"
    def df_encode_surface_position(self, lat, lon, alt, tc, ss, nicsb, timesync):
        # TODO
        exit(-1)

    # Ref :
    # ICAO Annex 10 : Aeronautical Telecommunications
    # Volume IV : Surveillance and Collision Avoidance Systems
    # Figure C-3. Extended Squitter Status
    # "Register 07_16"
    def df_encode_extended_squitter_status(self, trs = 0x0, ats = 0x0):
        df_frame = self.df_frame_start()

        df_frame.append((trs << 6) & 0x3 | (ats << 5) & 0x1)
        df_frame.extend([0]*6)

        self.df_frame_append_crc(df_frame)
        return df_frame
    
    #From https://github.com/jaywilhelm/ADSB-Out_Python on 2019-08-18
    def df_encode_ground_velocity(self, ground_velocity_kt, track_angle_deg, vertical_rate):
  
        #1-5    downlink format
        #6-8    CA capability
        #9-32   ICAO
        #33-88  DATA -> 33-87 w/ 33-37 TC
        #89-112 Parity
        track_angle_rad = numpy.deg2rad(track_angle_deg)

        V_EW = ground_velocity_kt*numpy.sin(track_angle_rad)
        V_NS = ground_velocity_kt*numpy.cos(track_angle_rad)

        if(V_EW >= 0):
            S_EW = 0
        else:
            S_EW = 1

        if(V_NS >= 0):
            S_NS = 0
        else:
            S_NS = 1

        V_EW = int(abs(V_EW))+1
        V_NS = int(abs(V_NS))+1

        S_Vr = 0
        Vr = int(vertical_rate)+1

        if(vertical_rate < 0):
            Vr = -Vr
            S_Vr = 1

        tc = 19     #33-37  1-5 type code
        st = 0x01   #38-40  6-8 subtype, 3 air, 1 ground speed
        ic = 0 #      #41     9 intent change flag
        resv_a = 0#1  #42     10
        NAC = 2#0     #43-45  11-13 velocity uncertainty
        #S_EW = 1#1    #46     14
        #V_EW = 97#9    #47-56  15-24
        #S_NS = 0#1    #57     25 north-south sign
        #V_NS = 379#0xA0 #58-67  26-35 160 north-south vel
        VrSrc = 1#0   #68     36 vertical rate source
        #S_Vr = 1#1    #69     37 vertical rate sign
        #Vr = 41#0x0E   #70-78  38-46 14 vertical rate
        RESV_B = 0  #79-80  47-48
        S_Dif = 0   #81     49 diff from baro alt, sign
        Dif = 0x1c#0x17  #82-88  50-66 23 diff from baro alt

        dfvel = self.df_frame_start()
        # data
        dfvel.append((tc << 3) | st)
        dfvel.append((ic << 7) | (resv_a << 6) | (NAC << 3) | (S_EW << 2) | ((V_EW >> 8) & 0x03))
        dfvel.append(0xFF & V_EW)
        dfvel.append((S_NS << 7) | ((V_NS >> 3))) #& 0x7F))
        dfvel.append(((V_NS << 5) & 0xE0) | (VrSrc << 4) | (S_Vr << 3) | ((Vr >> 6) & 0x03))        
        dfvel.append(((Vr  << 2) & 0xFC) | (RESV_B))
        dfvel.append((S_Dif << 7) | (Dif))

        self.df_frame_append_crc(dfvel)

        return dfvel

    #From https://github.com/jaywilhelm/ADSB-Out_Python on 2019-08-25
    # TODO the callsign must be 8
    def callsign_encode(self, csname):
        #Pad the callsign to be 8 characters
        csname = csname.ljust(8, '_')
        if len(csname) > 8 or len(csname) <= 0:
            print ("Name length error")
            return None
        csname = csname.upper()

        tc = 1  # §C.2.3.4
        ec = 1  # §C.2.3.4

        map = "#ABCDEFGHIJKLMNOPQRSTUVWXYZ#####_###############0123456789######"

        dfname = self.df_frame_start()
        # data
        dfname.append((tc << 3) | (ec))
        dfname.append((0xFC & (int(map.find(csname[0])) << 2)) | (0x03 & (int(map.find(csname[1])) >> 6)))
        dfname.append((0xF0 & (int(map.find(csname[1])) << 4)) | (0x0F & (int(map.find(csname[2])) >> 2)))
        dfname.append((0xF0 & (int(map.find(csname[2])) << 6)) | (0x3F & (int(map.find(csname[3])) >> 0)))
        dfname.append((0xFC & (int(map.find(csname[4])) << 2)) | (0x03 & (int(map.find(csname[5])) >> 4)))
        dfname.append((0xF0 & (int(map.find(csname[5])) << 4)) | (0x0F & (int(map.find(csname[6])) >> 2)))
        dfname.append((0xF0 & (int(map.find(csname[6])) << 6)) | (0x3F & (int(map.find(csname[7])) >> 0)))

        self.df_frame_append_crc(dfname)

        return dfname

    # Ref :
    # ICAO Annex 10 : Aeronautical Telecommunications
    # Volume IV : Surveillance and Collision Avoidance Systems
    # Figure C-8a. Extended Squitter Aircraft Status
    # "Register 61_16"

    def modaA_encode(self,modeA_4096_code = "7000", emergency_state = 0x0):
        frame = self.df_frame_start()
        # data
        format_tc = 28
        st = 0x01 # 0 : No information
                  # 1 : Emergency/Priority Status and Mode A Code
                  # 2 : TCAS/ACAS RA Broadcast -> Figure C-8b : fields have different meaning
                  # 3-7 : reserved
        frame.append((format_tc << 3) | st)

        # Encode Squawk
        # ABCD (A:0-7, B:0-7, C:0-7, D:0-7)
        # A = a4,a2,a1
        # B = b4,b2,b1
        # C = c4,c2,c1
        # D = d4,d2,d1
        # bits = c1,a1,c2,a2,c4,a4,0,b1,d1,b2,d2,b4,d4
        
        if isinstance(modeA_4096_code,int):
            squawk_str = '{:04d}'.format(modeA_4096_code)
        elif isinstance(modeA_4096_code,str):
            squawk_str = modeA_4096_code
        else:
            print("squawk must be provided as decimal int or 4 digits string")
            exit(-1)

        if (len(squawk_str) == 4):
            test_digits = True
            for i in range(4):
                test_digits = test_digits and (squawk_str[i] >= '0' and squawk_str[i] <= '7')
            if not test_digits:
                print("all 4 squawk digits must be in 0-7 range")
                exit(-1) 
        else:
            print("squawk must be 4 digits string")
            exit(-1)            

        a = "{0:03b}".format(int(squawk_str[0]))
        b = "{0:03b}".format(int(squawk_str[1]))
        c = "{0:03b}".format(int(squawk_str[2]))
        d = "{0:03b}".format(int(squawk_str[3]))

        a4 = int(a[0])
        a2 = int(a[1])
        a1 = int(a[2])

        b4 = int(b[0])
        b2 = int(b[1])
        b1 = int(b[2])

        c4 = int(c[0])
        c2 = int(c[1])
        c1 = int(c[2])

        d4 = int(d[0])
        d2 = int(d[1])
        d1 = int(d[2])

        squawk_bits = d4 | b4 << 1 | d2 << 2 | b2 << 3 | d1 << 4 | b1 << 5 | a4 << 7 | c4 << 8 | a2 << 9 | c2 << 10 | a1 << 11 | c1 << 12

        emergency = emergency_state

        if squawk_str == "7700":
            emergency = 0x1
        elif squawk_str == "7600":
            emergency = 0x4
        elif squawk_str == "7500":
            emergency = 0x5

        frame.append(emergency << 5 | squawk_bits >> 8)
        frame.append(squawk_bits & 0xFF)

        frame.extend([0]*4)

        self.df_frame_append_crc(frame)

        return frame

###############################################################
# Copyright (C) 2015 Junzi Sun (TU Delft)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################

# the polynominal generattor code for CRC
        
    def modes_crc(self, msg, encode=False):
        """Mode-S Cyclic Redundancy Check
        Detect if bit error occurs in the Mode-S message
        Args:
            msg (string): 28 bytes hexadecimal message string
            encode (bool): True to encode the date only and return the checksum
        Returns:
            string: message checksum, or partity bits (encoder)
        """

        GENERATOR = "1111111111111010000001001" # polynomial coefficients
        
        msgbin = list(self.hex2bin(msg))

        if encode:
            msgbin[-24:] = ['0'] * 24

        # loop all bits, except last 24 piraty bits
        for i in range(len(msgbin)-24):
            # if 1, perform modulo 2 multiplication,
            if msgbin[i] == '1':
                for j in range(len(GENERATOR)):
                    # modulo 2 multiplication = XOR
                    msgbin[i+j] = str((int(msgbin[i+j]) ^ int(GENERATOR[j])))

        # last 24 bits
        reminder = ''.join(msgbin[-24:])
        return reminder

    def hex2bin(self, hexstr):
        """Convert a hexdecimal string to binary string, with zero fillings. """
        scale = 16
        num_of_bits = len(hexstr) * math.log(scale, 2)
        binstr = bin(int(hexstr, scale))[2:].zfill(int(num_of_bits))
        return binstr

    def bin2int(self, binstr):
        """Convert a binary string to integer. """
        return int(binstr, 2)
