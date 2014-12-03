# -*- coding: utf-8 -*-
"""
Created on Sun Jun 01 20:18:56 2014

@author: Owner
"""
from glob import glob
from PIL import Image
import PIL.ImageOps

files = glob('*.gif')

for ifile in files:
    image = Image.open(ifile)
    image = PIL.ImageOps.invert(image.convert('RGB'))
    image.save('inverted/inv_' + ifile)