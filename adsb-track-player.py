#!/usr/bin/env python3

""" This file hold the main function which read user inputs
initialize and launch the simulation

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

import sys, time, math, os
from os.path import exists
import threading, json
import traceback

from AircraftInfos import AircraftInfos
from FixedTrajectorySimulator import FixedTrajectorySimulator
from WaypointsTrajectorySimulator import WaypointsTrajectorySimulator
from FlightPathSimulator import FlightPathSimulator
from HackRfBroadcastThread import HackRfBroadcastThread

from getopt import getopt, GetoptError

def usage(msg=False):
    if msg:print(msg)
    print("[h] Usage: %s [options]\n" % sys.argv[0])
    print("-h | --help              Display help message")
    print("--scenario <opt>         Scenario mode, argument is scenario JSON filepath")
    print("                           	waypoints   : Include waypoints file(s) in script directory")
    print("--icao <opt>             Callsign in hex, default: 0x508035")
    print("--callsign <opt>         Callsign (8 chars max), Default: DEADBEEF")
    print("--squawk <opt>           4-digit 4096 code squawk, Default: 7000")
    print("--trajectorytype <opt>   Types of simulated trajectories:")
    print("                           	fixed       : fixed broadcast")
    print("                           	flightsim   : dynamically generated flight path")
    print("--numac <flightsim opt>      Number of aircraft to simulate, Default: 1")
    print("--duration <opt>             Duration to simulate aircrafts in seconds, Default: 60")
    print("                           	Default: fixed")
    print("--lat <opt>              Latitude for the plane in decimal degrees, Default: 1.3521")
    print("--long <opt>             Longitude for the plane in decimal degrees. Default: 103.8198")
    print("--altitude <opt>         Altitude in decimal feet, Default: 16500.0")
    print("--speed <opt>            Airspeed in decimal kph, Default: 500.0")
    print("--vspeed <opt>           Vertical speed en ft/min, positive UP, Default: 0")
    print("--maxloadfactor          Specify the max load factor for aircraft simulation, Default: 1.45")
    print("--trackangle <opt>       Track angle in decimal degrees, Default: 0")
    print("--timesync <opt>         0/1, 0 indicates time not synchronous with UTC, Default: 0")
    print("--capability <opt>       Capability, Default: 5")
    print("--typecode <opt>         ADS-B message type, Default: 11")
    print("--sstatus <opt>          Surveillance status, Default: 0")
    print("--nicsupplementb <opt>   NIC supplement-B, Default: 0")
    print("--surface                Aircraft located on ground, Default: False")
    print("--posrate <opt>          Position frame broadcast period in µs, Default: 150000")
    print("")
    #print("see usage.md for additionnal information")

    sys.exit(2)

############ TRACK SIMULATION GENERATION FUNCTION ############
def getTrackSimulationThread(trajectory_type,broadcast_thread,aircraftinfos,waypoints_file,logfile,duration):
    if trajectory_type == 'fixed':
        return FixedTrajectorySimulator(broadcast_thread.getMutex(),broadcast_thread,aircraftinfos,waypoints_file,logfile)  
    elif trajectory_type == 'waypoints':
        return WaypointsTrajectorySimulator(broadcast_thread.getMutex(),broadcast_thread,aircraftinfos,waypoints_file,logfile)
    elif trajectory_type == 'flightsim':
    	return FlightPathSimulator(broadcast_thread.getMutex(),broadcast_thread,aircraftinfos,waypoints_file,logfile,duration=120)
    else:
        return None

############ MAIN FUNCTION ############
def main():

    # Log file check
    logfile = '/home/anton/adsb-track-player/logfile.csv'
    if os.path.exists(logfile):
        if os.path.isfile(logfile):
            print("[*] logfile.csv found")
    else:
        print("[!] logfile not found, creating...")
        with open(logfile,"w") as fLog:
            fLog.write("DATETIME,CALLSIGN,LAT,LONG,ALT,SPD,TRKANGLE")
        
    # Default values
    icao_aa = '0x508035'
    callsign = 'DEADBEEF'
    squawk = '7000'
    alt_ft  = 16500.0
    lat_deg = 1.3521
    lon_deg = 103.8198
    speed_kph = 500.0
    vspeed_ftpmin = 0.0
    maxloadfactor = 1.45
    track_angle_deg = 0.0
    capability = 5
    type_code = 11
    surveillance_status = 0
    timesync = 0
    nicsup = 0
    on_surface = False
    trajectory_type = 'fixed'
    waypoints_file = None
    posrate = 150000
    scenariofile = None
    waypoints_file = None
    numac=1
    duration=None
    try:
        (opts, args) = getopt(sys.argv[1:], 'h', \
            ['help','scenario=','icao=','callsign=','squawk=','trajectorytype=','lat=','long=','altitude=','speed=','vspeed=','maxloadfactor=','trackangle=',
            'timesync=','capability=','typecode=','sstatus=','nicsupplementb=','surface','posrate=','numac='
            ])
    except GetoptError as err:
        usage("%s\n" % err)

    if len(opts) != 0:
        for (opt, arg) in opts:
            if opt in ('-h', '--help'):usage()
            elif opt in ('--scenario'):scenariofile = arg
            elif opt in ('--icao'):icao_aa = arg
            elif opt in ('--callsign'):callsign = arg
            elif opt in ('--squawk'):squawk = arg
            elif opt in ('--trajectorytype'):trajectory_type = arg
            elif opt in ('--lat'):lat_deg = float(arg)
            elif opt in ('--long'):lon_deg = float(arg)
            elif opt in ('--altitude'):alt_ft = float(arg)
            elif opt in ('--speed'):speed_kph = float(arg)
            elif opt in ('--vspeed'):vspeed_ftpmin = float(arg)
            elif opt in ('--maxloadfactor'):maxloadfactor = float(arg)
            elif opt in ('--trackangle'):track_angle_deg = float(arg)
            elif opt in ('--timesync'):timesync = int(arg)
            elif opt in ('--capability'):capability = int(arg)
            elif opt in ('--typecode'):type_code = int(arg)
            elif opt in ('--sstatus'):surveillance_status = int(arg)
            elif opt in ('--nicsupplementb'):nicsup = int(arg)
            elif opt in ('--surface'):on_surface = True
            elif opt in ('--posrate'):posrate = int(arg)
            elif opt in ('--numac'):numac = int(arg)
            elif opt in ('--duration'):duration = int(arg)
            else:usage("Unknown option %s\n" % opt)
    print ("\n==== ADS-B Track Player v0.4 | by six3oo | core by Matioupi ====\n")
    
    # Functional code
    track_simulators = []
    broadcast_thread = HackRfBroadcastThread(posrate) # posrate would usally be used with random mode to generate load of tracks

    # Scenario file presence check
    if scenariofile == None:
        print("[*] CLI mode")
        aircraftinfos = AircraftInfos(icao_aa,callsign,squawk, \
                                    lat_deg,lon_deg,alt_ft,speed_kph,vspeed_ftpmin,maxloadfactor,track_angle_deg, \
                                    timesync,capability,type_code,surveillance_status,nicsup,on_surface)
        # Multiple aircraft option
        if numac>1:
            print("[!] Generating "+str(numac)+" fuzzing aircraft")
        
        for i in range(numac):
        # TRACK SIMULATION CREATION
                track_simulation = getTrackSimulationThread(trajectory_type,broadcast_thread,aircraftinfos,waypoints_file,logfile,duration)
                track_simulators.append(track_simulation)
    
    # Scenario file parsing
    else:
        print("[*] JSON Scenario mode: "+os.path.abspath(scenariofile))
        with open(scenariofile,'r') as json_file:
            scenario = json.load(json_file)
        
        if exists("waypoints.csv"):
           waypoints_file = "waypoints.csv"                
           print("[!] Waypoints file detected: " +os.path.abspath(waypoints_file))
        
        for plane in scenario.values():
            plane_info = AircraftInfos.from_json(plane["filename"])
            # TRACK SIMULATION CREATION
            track_simulation = getTrackSimulationThread(plane["trajectory_type"],broadcast_thread,plane_info,waypoints_file,logfile,duration)
            track_simulators.append(track_simulation)

        print("[*] Scenario contains track simulations for "+str(len(track_simulators))+" plane(s):")
        for tsim in track_simulators:
            print("    [:] Callsign: "+tsim.aircraftinfos.callsign.ljust(9,' ')+"MSL altitude: "+"{:7.1f}".format(tsim.aircraftinfos.alt_msl_ft)+" ft\t| Thread: "+str(tsim))
            
    for tsim in track_simulators:
        broadcast_thread.register_track_simulation_thread(tsim)

    while(val:=input("[*] Type \'s + Enter\' to start ADS-B transmission, and type \'s + Enter\' again to stop: ") != 's'):
        time.sleep(0.05)

    # START all threads
    for tsim in track_simulators:
        tsim.start()

    broadcast_thread.start()
    # user input loop. Todo : implement other commands? (in that case don't forget to check if mutex protection is needed)
    while(val:=input("") != 's'):
        time.sleep(0.05)

    # STOP all threads
    for tsim in track_simulators:
        tsim.stop()
    
    broadcast_thread.stop()

    # wait for all threads to terminate
    for tsim in track_simulators:
        tsim.join()
    broadcast_thread.join()

    print("==== ADS-B transmission ended ====")

if __name__ == "__main__":
    main()
