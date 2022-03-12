# realtime ADS-B out

## Foreword

This project is inspired and reuse several parts of several other ADS-B / mode S projects amongst which:

- https://github.com/lyusupov/ADSB-Out
- https://github.com/nzkarit/ADSB-Out and https://github.com/pynstrom/adsb-out
- https://github.com/bistromath/gr-air-modes
- https://github.com/junzis/pyModeS

All those repositories are published under GNU General Public License v3.0. This is also the license chosen for this repository.
Please let me know if you have issues or require more explicit citations about reused source code.

## Project goals

The initial project goals are oriented towards:

- completing the set of broadcastable messages that have already been implemented "adsb-out" in referenced projects.
- fixing bugs / adding features in existing code.
- producing a software architecture that better suit my understanding/habits.
- beeing able to live feed HackRF through a libhackrf python wrapper layer, rather than generating an IQ sample files that would later be hackrf_transfer'd.

## HackRF python wrapper

HackRF python wrapper `pyhackrf.py` is included in this repository but is also proposed to be merged into hackRF main repository: https://github.com/greatscottgadgets/hackrf/pull/1058  
If the pull request get accepted, file `pyhackrf.py` will be removed from this repo.  
This repo only uses TX feature of the python wrapper, but RX is also possible (see examples in the PR)

At time of writting this guide, I also believe there is a regression in `libhackrf` which should be solved by PR: https://github.com/greatscottgadgets/hackrf/pull/1057  
This is still under review from greatscottgadgets maintainers but code in this repo is tested with the PR included.  
I have not tested it with older/officiel releases of hackrf drivers/dev lib versions.

## Software architecture

The workflow is divided between 3 execution threads:

- main thread wich performs all initializations and control user inputs (mainly start / stop simulation for now)
- hackrf broadcasting thread which pump encoded messages and send them over the air with a predefined schedule
- trajectory simulation thread which feed brodcasting thread with encoded messages matching a real time simulated trajectory

The message encoding is splitted into mode S "frame encoding" and "low level encoding" which handles PPM modulation and conversion to hackRF IQ sample format.  
Software source code structure tries to reflect those 2 different layers.

So far only "simple" simulated trajectories are available, but one can easily extend/fork behaviour to e.g. have a flight informations coming from a flight simulator (X-plane would be pretty well suited for that purpose through it's UDP aircraft state broadcast facility) or use actual sensors to feed live data.

## Usage and RF broadcast disclaimer

Usage can be demonstrated together with `dump1090-mutability` or `dump1090-fa` and associated webservers or text message views.

Repository source code is tuned for a 1090 MHz brodcast with **direct wire feed** to a receiver SDR dongle (no over the air broadcast).  
The hardware setup I'm using is pictured below. Please note the RF attenuators (-20dB and -30dB).  
The extra 1090MHz filter is probably not requiered as the flight aware dongle already features 1090 MHz filtering.
My HackRF is fitted with a 0.5 ppm TCXO

![test setup image](./test-setup.jpg "test setup")

The default hackrf settings in repo are :
- 1090 MHz
- LNA amplificator disabled
- TX gain 4dB
- Sample rate needs to be 2MHz as this matches the ADS-B specification where PPM symbols last for 0.5 µs.

Actual ADS-B brodcast frequency is 1090MHz which in most if not all places is a reserved band.  
Some critical **flight safety feature** do rely on actual ADS-B broadcasts.  
Unless you have special authorisations, **you should NEVER broadcast over the air at this frequency**.

If you can't use a wired RF feeding between hackRF and your SDR receiver for your test setup, you can easily modify source code in order to use a "fake" free frequency (e.g. 868MHz) and setup dump1090 accordingly to match this "fake" frequency by adding switch `--freq 868000000` to your usual `dump1090` command line. Increasing TX gain may be needed in that use case.

By the way, I believe that the fact that one with 200$ hardware would actually be able to broadcast at 1090MHz and produce some fake ADS-B aircraft tracks highlights a serious weakness in ADS-B design.  
Those forged broadcasts may be used to spoof ATC, trigger TCAS or other malicious behaviours.

## Command line examples

`./realtime-adsb-out.py --callsign 'FCKPUTIN' --alt 4500 --speed 600 --trajectorytype circle --maxloadfactor 1.03`

will generate a pseudo circular trajectory, flown at 4500 ft, 600 km/h and a load factor of 1.03.

![circle mode example image](./adsb-out-circle.png "circle mode example")

`./realtime-adsb-out.py --callsign 'FCKPUTIN' --alt 4500  --trajectorytype random`

will generate a random trajectory in a ~30s at specified (here default) speed around center lat / lon (default here too).  
track angle is randomized, speed is randomized, altitude is randomized. The default position frame broadcast period can be lowered in order to
produce a large numer of tracks in a given area

![random mode example image](./adsb-out-random.png "random mode example")

## Reference documentation

All reference documentation from the repositories mentionned in the foreword.

https://mode-s.org/

*ICAO Annex 10, Aeronautical Telecommunications, Volume IV - Surveillance Radar and Collision Avoidance Systems* which at time of writing can be retrieved here:
- english version https://www.bazl.admin.ch/bazl/en/home/specialists/regulations-and-guidelines/legislation-and-directives/anhaenge-zur-konvention-der-internationalen-zivilluftfahrtorgani.html
- french version https://www.bazl.admin.ch/bazl/fr/home/experts/reglementation-et-informations-de-base/bases-legales-et-directives/annexes-a-la-convention-de-l-organisation-internationale-de-l-av.html  

*ICAO doc 9871 edition 1* which can be retrieved here (There is an edition 2 of this document but all seems to be behing paywalls):
- [ICAO doc 9871 edition 1](http://www.aviationchief.com/uploads/9/2/0/9/92098238/icao_doc_9871_-_technical_provisions_for_mode_s_-_advanced_edition_1.pdf)  
  
A DEFCON 20 video on Youtube that already highlighted some ADS-B weaknesses (and at this time, there was no HackRF):
[DEFCON 20 (2012) - RenderMan - Hacker + Airplanes = No Good Can Come Of This](https://www.youtube.com/watch?v=mY2uiLfXmaI)
