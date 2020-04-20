#!/usr/bin/env python3
import re
import numpy as np
import mrcfile
import os
import scipy
import scipy.ndimage
class IceDet:
    """Library to generate ice thickness image"""
    def __init__(self, sqFile, ):
        self.sqFile = sqFile

    def read_intzero(self, file):
        f = open(file,"r")
        intZero = f.readline()
        intZero = float(intZero.strip())
        return intZero

    def read_square(self):
        imaSquare = mrcfile.open(self.sqFile)
        return imaSquare

    def read_sqareMode(self):
        N = 3
        string = 'DataMode'
        mdoc = open(self.sqFile + '.mdoc','r')
        listOfLines = mdoc.readlines()
        for i in listOfLines:
            if string in i:
                dataMode = int(i.split(' ')[N-1])
        if dataMode == 1 or dataMode == 6:
            pass
        else:
            print("Square image is not in integer mode.")
            print("Terminating")
            sys.exit()

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
        zeroIma = mrc.open(vacIma)
        intZero = np.mean(zeroIma.data)
        return intZero
