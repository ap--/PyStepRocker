#!/usr/bin/env python

import time
from TMCM import StepRocker


rocker = StepRocker(24, port='/dev/ttyACM0')
rocker.set_important_parameters(maxspeed=1000,
                                maxaccel=10,
                                maxcurrent=50,
                                standbycurrent=10,
                                microstep_resolution=4)

rocker.rotate(10.)
time.sleep(10)
rocker.stop()


