#!/usr/bin/env python3
import re, os, glob, scipy
import scipy.ndimage
import numpy as np
import mrcfile as mrc
from pathlib import Path
from PIL import Image
import iceDet
ice = iceDet.iceImage()
path = os.getcwd() # get current path
ice.create_colors()
ice.read_params_fromSerialEM("iceData.txt")
for sqFile in glob.iglob(path + '/Square-*.mrc'):
	sqBase = Path(sqFile).stem
	ice.sqFile = sqFile
	ice.read_sqareMode()
	ice.read_square()
	ice.make_color_image(sqBase)
