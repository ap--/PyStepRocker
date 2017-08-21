#!/usr/bin/env python

import time
from TMCM import StepRocker


rocker = StepRocker(debug=True)
rocker.set_important_parameters(max_speed=1000,
                                max_accel=10,
                                max_current=50,
                                standbycurrent=10,
                                microstep_resolution=4)

rocker.get_globals()
rocker.get_parameters()

rocker.rotate(10., steps=24)
time.sleep(10)
rocker.stop()


