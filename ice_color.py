#!/usr/bin/env python3
import re, os, glob, scipy
import scipy.ndimage
import numpy as np
import mrcfile as mrc
from pathlib import Path
from PIL import Image
N = 3  # mdoc place of value
K = 2
path = os.getcwd() # get current path
imRed = Image.new("RGB", (1744, 1694), "#C70000")
np_imRed = np.array(imRed)
imBlue = Image.new("RGB", (1744, 1694), "#0066FF")
np_imBlue = np.array(imBlue)
imBlack = Image.new("RGB", (1744, 1694), "#232B2B")
np_imBlack = np.array(imBlack)
string = 'DataMode'
strFilt = 'FilterSlitAndLoss'
with open("iceData.txt") as iceDoc:
	for line in iceDoc:
		if "VacuumIntensity" in line:
			intZero = float(line.split(' ')[K-1])
		if "ThickIceFilter" in line:
			iceHigh = int(line.split(' ')[K-1])
		if "ThinIceFilter" in line:
			iceLow = int(line.split(' ')[K-1])
iceHighStr = str(iceHigh)
iceLowStr = str(iceLow)
for sqFile in glob.iglob(path + '/Square-*.mrc'):
	sqBase = Path(sqFile).stem
	if not re.match('.*ice.*',sqBase):
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
		imaSquare = mrc.open(sqFile)
		coEf = 322
		if slitWidth == 20:
			coEf = 322

		if slitWidth == 40:
			coEf = 395

		if slitWidth == 0:
			coEf = 3329

		iceIm = np.around(coEf * np.log(intZero / imaSquare.data)).astype(np.int16).clip(min=0)
		iceImGood = iceIm
		iceImGood[iceImGood > iceHigh ] = '0'
		iceImGood[iceImGood < iceLow ] = '0'
		iceImGood[iceImGood > 0 ] = '1'
		dilIm = scipy.ndimage.morphology.binary_dilation(iceImGood, structure=None, iterations=5, mask=None, output=None, border_value=0, origin=0, brute_force=False)
		dilImIn = dilIm.astype(np.int16)
		dilImIn8 = dilIm.astype(np.uint8)
		iceImGood8 = iceImGood.astype(np.uint8)
		ber = mrc.new(sqBase + "-ice-filt" + iceHighStr + "-" + iceLowStr + ".mrc")
		ber.set_data(dilImIn)
		ber.close()
		iceImGood8T = np.repeat(iceImGood8[:, :, np.newaxis], 3, axis=2)
		coIceImGood8 = np.multiply(iceImGood8T, np_imBlue)
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
