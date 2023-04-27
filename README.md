# ADS-B Track Player

## Foreword

This project is a highly modified fork of:

https://github.com/Matioupi/realtime-adsb-out

It is thus important to read the README of that project.

As such, it draws inspiration and some code from all repositories referenced in that original project:
    https://github.com/lyusupov/ADSB-Out
    https://github.com/nzkarit/ADSB-Out and https://github.com/pynstrom/adsb-out
    https://github.com/bistromath/gr-air-modes
    https://github.com/junzis/pyModeS

All referenced repositories are published under GNU General Public License v3.0. This is also the license chosen for this repository.
Please let me know if you have issues or require more explicit citations about reused source code.

## Software Architecture

As per the project 'realtime-adsb-out', the workflow is divided between 3 execution threads:

- Main thread wich performs all initializations and control user inputs (mainly start / stop simulation for now)
- HackRF broadcasting thread which pump encoded messages and send them over the air with a predefined schedule
- Trajectory simulation thread which feeds the broadcasting thread with encoded messages matching a real time simulated trajectory

The message encoding is split into Mode S "frame encoding" and "low level encoding" which handles PPM modulation and conversion to HackRF IQ sample format. The source code structure tries to reflect these two layers.

## Modifications from 'realtime-adsb-out'

- Waypoint trajectory simulation is implemented
- Circle and Random trajectory simulations have been removed
- Increased verbosity
- HackRF configured for wireless RF transmission (Default: 1090MHz)
[NOTE: It is illegal in most jurisdictions to transmit at 1090MHz!]

## Command Line Examples

#### *Command line switches can be displayed with*  

```
six3oo@computer:~/adsb-track-player$ ./adsb-track-player.py -h
Usage: ./adsb-track-player.py [options]

-h | --help              Display help message
--scenario <opt>         Scenario mode, argument is scenario JSON filepath
--icao <opt>             Callsign in hex, default: 0x508035
--callsign <opt>         Callsign (8 chars max), Default: DEADBEEF
--squawk <opt>           4-digit 4096 code squawk, Default: 7000
--trajectorytype <opt>   Types of simulated trajectories:
                           fixed       : steady aircraft
                           waypoints   : fly long flight path
                           Default:fixed
--lat <opt>              Latitude for the plane in decimal degrees, Default: 50.44994
--long <opt>             Longitude for the plane in decimal degrees. Default: 30.5211
--altitude <opt>         Altitude in decimal feet, Default: 1500.0
--speed <opt>            Airspeed in decimal kph, Default: 300.0
--vspeed <opt>           Vertical speed en ft/min, positive UP, Default: 0
--maxloadfactor          Specify the max load factor for aircraft simulation, Default: 1.45
--trackangle <opt>       Track angle in decimal degrees, Default: 0
--timesync <opt>         0/1, 0 indicates time not synchronous with UTC, Default: 0
--capability <opt>       Capability, Default: 5
--typecode <opt>         ADS-B message type, Default: 11
--sstatus <opt>          Surveillance status, Default: 0
--nicsupplementb <opt>   NIC supplement-B, Default: 0
--surface                Aircraft located on ground, Default: False
--posrate <opt>          Position frame broadcast period in µs, Default: 150000

```

#### *Single plane scenarios*  

`./adsb-track-player.py --callsign 'TEST' --alt 4500 --speed 600 --trajectorytype fixed --maxloadfactor 1.03`

will generate a fixed trajectory, flown at 4500 ft, 600 km/h and a load factor of 1.03.

#### *JSON scenarios with multiple planes*  

`./adsb-track-player.py --scenario ./examples/scenario.json`  
  
![4 planes scenario example](./images/adsb-out-scenario3.png "4 planes scenario example")

The maximum number of planes that can be simulated has not been evaluated yet. It will depends on the refresh rate of each message type, etc.
Tests have been performed on a laptop computer, but with not too many tracks, it should be possible to run on lighter platforms such as Raspberry Pi.  

## Reference Documentation

All reference documentation from the repositories mentioned in the foreword.
  
Ghost in the Air(Traffic): On insecurity of ADS-B protocol and practical attacks on ADS-B devices (Andrei Costin, Aurélien Francillon):
[publication PDF hosted at eurocom.fr](https://www.s3.eurecom.fr/docs/bh12us_costin.pdf)

A DEFCON 20 video on Youtube that already highlighted some ADS-B weaknesses (and at this time, there was no HackRF):
[DEFCON 20 (2012) - RenderMan - Hacker + Airplanes = No Good Can Come Of This](https://www.youtube.com/watch?v=mY2uiLfXmaI)
