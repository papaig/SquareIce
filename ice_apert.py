#!/usr/bin/env python3
import re, os, glob
import numpy as np
import mrcfile as mrc
from pathlib import Path
N = 3
path = os.getcwd()
string = 'DataMode'
strFilt = 'FilterSlitAndLoss'
f = open("inZero.txt","r")
intZero = f.readline()
intZero = float(intZero.strip())
for sqFile in glob.iglob(path + '/Square-*.mrc'):
	sqBase = Path(sqFile).stem
#	sqFile = '1200-squares-20eV-overview.mrc'
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
	sqIma = mrc.open(sqFile)
	coEf = 322
	if slitWidth == 20:
		coEf = 322

	if slitWidth == 40:
		coEf = 395

	if slitWidth == 0:
		coEf = 3329

	iceIm = np.around(coEf * np.log(intZero / sqIma.data)).astype(np.int16).clip(min=0)
	#combIm[combIm == 0] = '1000' #not sure that this needs to be done
	newFile = mrc.new(sqBase + "-ice.mrc")
	newFile.set_data(iceIm)
	newFile.close()
	iceIm[iceIm >50 ] = '0'
	iceIm[iceIm <30 ] = '0'
	iceIm[iceIm >0 ] = '1'
	dilIm = scipy.ndimage.morphology.binary_dilation(iceIm, structure=None, iterations=5, mask=None, output=None, border_value=0, origin=0, brute_force=False)
	dilImIn = dilIm.astype(np.int16)
	ber = mrc.new(sqBase + "-ice-filt50-30.mrc")
	ber.set_data(dilImIn)
	ber.close()
