#!/usr/bin/env python3
import re, os, glob, scipy, time, mrcfile
from watchdog.events import PatternMatchingEventHandler, FileCreatedEvent
from watchdog.observers import Observer
from pathlib import Path
from queue import Queue
from threading import Thread
import iceDetLive
import scipy.ndimage
import numpy as np
from PIL import Image
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

dir_path = os.getcwd()

def process_queue(q, intZero, iceHigh, iceLow, iceHighStr, iceLowStr, np_imBlue, np_imBlack, np_imRed):

    while True:
        if not q.empty():
            event = q.get()
 #           print("New file:{}".format (event.src_path))
            sqFile = event.src_path
            sqBase = Path(sqFile).stem
            if not "ice" in sqBase:
                while not os.path.exists(sqFile + '.mdoc'):
                    time.sleep(1)
                N = 3
                string = 'DataMode'
                strFilt = 'FilterSlitAndLoss'
                mdoc = open(sqFile + '.mdoc','r')
                listOfLines = mdoc.readlines()
                for i in listOfLines:
                    if string in i:
                        dataMode = int(i.split(' ')[N-1])
                    if strFilt in i:
                        slitWidth = int(i.split(' ')[N-1])
                if dataMode == 1 or dataMode == 6:
                    pass
                else:
                    print("Square image is not in integer mode.")
                    print("Terminating")
                    sys.exit()
                coEf = 322
                if slitWidth == 20:
                    coEf = 322

                if slitWidth == 40:
                    coEf = 395

                if slitWidth == 0:
                    coEf = 3329

                imaSquare = mrcfile.open(sqFile)
                iceIm = np.around(coEf * np.log(intZero / imaSquare.data)).astype(np.int16).clip(min=0)
                iceImGood = iceIm
                iceImGood[iceImGood > iceHigh ] = '0'
                iceImGood[iceImGood < iceLow ] = '0'
                iceImGood[iceImGood > 0 ] = '1'
                dilIm = scipy.ndimage.morphology.binary_dilation(iceImGood, structure=None, iterations=5, mask=None, output=None, border_value=0, origin=0, brute_force=False)
                dilImIn = dilIm.astype(np.int16)
                dilImIn8 = dilIm.astype(np.uint8)
                iceImGood8 = iceImGood.astype(np.uint8)
                ber = mrcfile.new(sqBase + "-ice-filt" + iceHighStr + "-" + iceLowStr + ".mrc", overwrite=True)
                ber.set_data(dilImIn)
                ber.close()
                iceImGood8T = np.repeat(iceImGood8[:, :, np.newaxis], 3, axis=2)
                coIceImGood8 = np.multiply(iceImGood8T, np_imBlue)
                #somehow if I don't regenetate the ice image the script doesn't work.
                iceIm = np.around(coEf * np.log(intZero / imaSquare.data)).astype(np.int16).clip(min=0)
                iceImThick = iceIm
                iceImThick[iceImThick <= iceHigh ] = '0'
                iceImThick[iceImThick > 0 ] = '1'
                iceImThick8 = iceImThick.astype(np.uint8)
                iceImThickT = np.repeat(iceImThick8[:, :, np.newaxis], 3, axis=2)
                coIceImThick = np.multiply(iceImThickT, np_imBlack)
                iceIm = np.around(coEf * np.log(intZero / imaSquare.data)).astype(np.int16).clip(min=0)
                iceImThin = iceIm
                iceImThin[iceImThin >= iceLow ] = '0'
                iceImThin[iceImThin > 0 ] = '1'
                iceImThin8 = iceImThin.astype(np.uint8)
                iceImThinT = np.repeat(iceImThin8[:, :, np.newaxis], 3, axis=2)
                coIceImThin = np.multiply(iceImThinT, np_imRed)
                mergeIm = coIceImThin + coIceImThick + coIceImGood8
                new_im = Image.fromarray(mergeIm)
                new_im.save(sqBase + "-ice-color" + iceHighStr + "-" + iceLowStr + ".png")
                print('Processed {}'.format(sqBase))

        time.sleep(1)


class FileWatchdog(PatternMatchingEventHandler):

    def __init__(self, queue):
        PatternMatchingEventHandler.__init__(self, patterns=['*.mrc'], ignore_directories=True, case_sensitive=False)
        self.queue = queue

    def process(self, event):
        self.queue.put(event)

    def on_created(self, event):
        if "Square-" in event.src_path:
            sqFile = event.src_path
            sqBase = Path(sqFile).stem
            if not "ice" in sqBase:
                self.process(event)


if __name__ == '__main__':
    ice = iceDetLive.iceImage()
    iceDataFile = dir_path + '/iceData.txt'
    np_imRed, np_imBlue, np_imBlack = ice.create_colors()
    while not os.path.exists(iceDataFile):
        time.sleep(1)
    if os.path.isfile(iceDataFile):
        intZero, iceHigh, iceLow, iceHighStr, iceLowStr = ice.read_params_fromSerialEM(iceDataFile)
    else:
        raise SystemExit("%s isn't a file! Exiting..." % iceDataFile)


    watchdog_queue = Queue()

    worker = Thread(target=process_queue, args=(watchdog_queue, intZero, iceHigh, iceLow, iceHighStr, iceLowStr, np_imBlue, np_imBlack, np_imRed))
    worker.setDaemon(True)
    worker.start()

    for file in glob.iglob(dir_path + '/Square-*.mrc'):
        fileBase = Path(file).stem
        if not os.path.exists(fileBase + "-ice-color" + iceHighStr + "-" + iceLowStr + ".png"):
            if not "ice" in fileBase:
                event = FileCreatedEvent(file)
                watchdog_queue.put(event)

    event_handler = FileWatchdog(watchdog_queue)
    observer = Observer()
    observer.schedule(event_handler, path=dir_path)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
