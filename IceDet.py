#!/usr/bin/env python3
import re, os, glob, scipy
import scipy.ndimage
import numpy as np
import mrcfile
from pathlib import Path
from PIL import Image
class iceImage:
    """Library to generate ice thickness image"""
    def __init__(self):
        self.sqFile = []

    def read_params_fromSerialEM(self, dataFile):
        K = 2
        with open(dataFile) as iceDoc:
            for line in iceDoc:
                if "VacuumIntensity" in line:
                    self.intZero = float(line.split(' ')[K-1])
                if "ThickIceFilter" in line:
                    self.iceHigh = int(line.split(' ')[K-1])
                if "ThinIceFilter" in line:
                    self.iceLow = int(line.split(' ')[K-1])
        self.iceHighStr = str(self.iceHigh)
        self.iceLowStr = str(self.iceLow)
#        return intZero, iceHigh, iceLow, iceHighStr, iceLowStr

    def read_square(self):
        self.imaSquare = mrcfile.open(self.sqFile)
#        return imaSquare

    def read_sqareMode(self):
        N = 3
        string = 'DataMode'
        strFilt = 'FilterSlitAndLoss'
        mdoc = open(self.sqFile + '.mdoc','r')
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
        self.coEf = 322
        if slitWidth == 20:
            self.coEf = 322

        if slitWidth == 40:
            self.coEf = 395

        if slitWidth == 0:
            self.coEf = 3329
#        return coEf

    def create_colors(self):
        imRed = Image.new("RGB", (1744, 1694), "#C70000")
        self.np_imRed = np.array(imRed)
        imBlue = Image.new("RGB", (1744, 1694), "#0066FF")
        self.np_imBlue = np.array(imBlue)
        imBlack = Image.new("RGB", (1744, 1694), "#232B2B")
        self.np_imBlack = np.array(imBlack)

    def binArray(self, data, axis, binstep, binsize, func=np.nanmean):
        data = np.array(data)
        dims = np.array(data.shape)
        argdims = np.arange(data.ndim)
        argdims[0], argdims[axis]= argdims[axis], argdims[0]
        data = data.transpose(argdims)
        data = [func(np.take(data,np.arange(int(i*binstep),int(i*binstep+binsize)),0),0) for i in np.arange(dims[axis]//binstep)]
        data = np.array(data).transpose(argdims)
        return data

    def runAver(self, imaSquare, winsize):
        MeanIm = np.mean(imaSquare.data)
        sqMeaned = scipy.ndimage.uniform_filter(test1, size=winsize, mode='constant', cval=MeanIm)

    def intZero_from_mrc(self, vacIma):
        zeroIma = mrcfile.open(vacIma)
        intZero = np.mean(zeroIma.data)
        return intZero

    def make_color_image(self, sqBase):
        iceIm = np.around(self.coEf * np.log(self.intZero / self.imaSquare.data)).astype(np.int16).clip(min=0)
        iceImGood = iceIm
        iceImGood[iceImGood > self.iceHigh ] = '0'
        iceImGood[iceImGood < self.iceLow ] = '0'
        iceImGood[iceImGood > 0 ] = '1'
        dilIm = scipy.ndimage.morphology.binary_dilation(iceImGood, structure=None, iterations=5, mask=None, output=None, border_value=0, origin=0, brute_force=False)
        dilImIn = dilIm.astype(np.int16)
        dilImIn8 = dilIm.astype(np.uint8)
        iceImGood8 = iceImGood.astype(np.uint8)
        ber = mrcfile.new(sqBase + "-ice-filt" + self.iceHighStr + "-" + self.iceLowStr + ".mrc")
        ber.set_data(dilImIn)
        ber.close()
        iceImGood8T = np.repeat(iceImGood8[:, :, np.newaxis], 3, axis=2)
        coIceImGood8 = np.multiply(iceImGood8T, self.np_imBlue)
        #somehow if I don't regenetate the ice image the script doesn't work.
        iceIm = np.around(self.coEf * np.log(self.intZero / self.imaSquare.data)).astype(np.int16).clip(min=0)
        iceImThick = iceIm
        iceImThick[iceImThick <= self.iceHigh ] = '0'
        iceImThick[iceImThick > 0 ] = '1'
        iceImThick8 = iceImThick.astype(np.uint8)
        iceImThickT = np.repeat(iceImThick8[:, :, np.newaxis], 3, axis=2)
        coIceImThick = np.multiply(iceImThickT, self.np_imBlack)
        iceIm = np.around(self.coEf * np.log(self.intZero / self.imaSquare.data)).astype(np.int16).clip(min=0)
        iceImThin = iceIm
        iceImThin[iceImThin >= self.iceLow ] = '0'
        iceImThin[iceImThin > 0 ] = '1'
        iceImThin8 = iceImThin.astype(np.uint8)
        iceImThinT = np.repeat(iceImThin8[:, :, np.newaxis], 3, axis=2)
        coIceImThin = np.multiply(iceImThinT, self.np_imRed)
        mergeIm = coIceImThin + coIceImThick + coIceImGood8
        new_im = Image.fromarray(mergeIm)
        new_im.save(sqBase + "-ice-color" + self.iceHighStr + "-" + self.iceLowStr + ".png")
