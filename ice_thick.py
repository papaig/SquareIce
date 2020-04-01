#!/usr/bin/env python3
import re
import numpy as np
import mrcfile as mrc
import os
N = 3
string = "FilterSlitAndLoss"
mdoc = open("square_ice-test-WithFilter.mrc.mdoc",'r')
listOfLines = mdoc.readlines()
for i in listOfLines:
	if string in i:
		slitWidth = int(i.split(' ')[N-1])
imaNoFilt = mrc.open('square_ice-test-NoFilter.mrc')
imaWithFilt = mrc.open('square_ice-test-WithFilter.mrc')
coEf = 395
if slitWidth == 20:
	coEf = 435
	
if slitWidth == 15:
	coEf = 395

combIm = np.around(coEf * np.log(imaNoFilt.data / imaWithFilt.data)).astype(np.int16).clip(min=0)
#combIm[combIm == 0] = '1000' #not sure that this needs to be done
newFile = mrcfile.new("test-comb.mrc")
newFile.set_data(combIm)
newFile.close()
combIm[combIm >50 ] = '0'
combIm[combIm <30 ] = '0'
combIm[combIm >0 ] = '1'
ber = mrcfile.new("test-comb-filt50-30.mrc")
ber.set_data(combIm)
ber.close()
