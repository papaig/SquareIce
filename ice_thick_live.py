#!/usr/bin/env python3
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import re, os, glob, scipy
import scipy.ndimage
import numpy as np
import mrcfile as mrc
from pathlib import Path
from PIL import Image
import iceDetLive
path = os.getcwd() # get current path
ice = iceDetLive.iceImage()
event_handler = iceDetLive.Handler()
iceDataFile = path + '/iceData.txt'
while not os.path.exists(iceDataFile):
    time.sleep(1)
if os.path.isfile(iceDataFile):
    event_handler.intZero, event_handler.iceHigh, event_handler.iceLow, event_handler.iceHighStr, event_handler.iceLowStr = ice.read_params_fromSerialEM(iceDataFile)
else:
    raise SystemExit("%s isn't a file! Exiting..." % iceDataFile)

event_handler.np_imRed, event_handler.np_imBlue, event_handler.np_imBlack = ice.create_colors()
observer = Observer()
observer.schedule(event_handler, path='.', recursive=True)
observer.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
    observer.join()
