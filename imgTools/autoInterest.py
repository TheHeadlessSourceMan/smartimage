#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This automatically detects regions of interest in an image.
"""
import os
from PIL import Image, ImageOps, ImageChops, ImageEnhance, ImageDraw
try:
	# first try to use bohrium, since it could help us accelerate
	# https://bohrium.readthedocs.io/users/python/
	import bohrium as np
except ImportError:
	# if not, plain old numpy is good enough
	import numpy as np
try:
	import cv2
	has_opencv=True
except ImportError:
	has_opencv=False


def skin(image):
	"""
	use opencv to try and detect human skin in the image

	returns b&w image where white=interesting, black=uninteresting
	"""
	if not has_opencv:
		return None
	# Constants for finding range of skin color in YCrCb
	min_YCrCb = np.array([0,133,77],np.uint8)
	max_YCrCb = np.array([255,173,127],np.uint8)
	# Convert image to YCrCb
	imageYCrCb = cv2.cvtColor(np.array(image),cv2.COLOR_BGR2YCR_CB)
	# Find region with skin tone in YCrCb image
	skinRegion = cv2.inRange(imageYCrCb,min_YCrCb,max_YCrCb)
	# convert to image
	outImage=Image.fromarray(np.uint8(skinRegion))
	return outImage


def faces(image):
	"""
	use opencv to try and detect human faces - especially eyes in the image

	see also:
		https://docs.opencv.org/trunk/d7/d8b/tutorial_py_face_detection.html
		https://shahsparx.me/opencv-eye-detection-glasses-opencv/

	returns b&w image where white=interesting, black=uninteresting
	"""
	if not has_opencv:
		return None
	outImage=Image.new('L',image.size,0)
	draw=ImageDraw.Draw(outImage)
	basedir=os.path.abspath(__file__).rsplit(os.sep,1)[0]+os.sep+'cv_data'+os.sep+'haarcascades'+os.sep
	face_detector = cv2.CascadeClassifier(basedir+'haarcascade_frontalface_default.xml')
	eye_detector = cv2.CascadeClassifier(basedir+'haarcascade_eye.xml')
	np_image=np.array(image)
	gray = cv2.cvtColor(np_image, cv2.COLOR_BGR2GRAY)
	faces = face_detector.detectMultiScale(gray, 1.3, 5)
	for (x,y,w,h) in faces:
		draw.ellipse((x,y,x+w,y+h),fill=128)
		#cv2.rectangle(np_image, (x,y), (x+w,y+h), (255,0,0), 2) # is this line necessary?
		face_gray = gray[y:y+h, x:x+w]
		eyes = eye_detector.detectMultiScale(face_gray)
		for (ex,ey,ew,eh) in eyes:
			#eye_gray = gray[ey:ey+eh, ex:ex+ew]
			draw.ellipse((x+ex,y+ey,x+ex+ew,y+ey+eh),fill=255)
	return outImage


def highContrast(image):
	"""
	get interest based on very bright or very dark areas

	returns b&w image where white=interesting, black=uninteresting
	"""
	img=image.convert('L')
	img=ImageOps.equalize(img)
	mid=Image.new('L',img.size,128)
	img=ImageChops.add_modulo(img,mid)
	return ImageOps.equalize(img)


def interest(image):
	"""
	get regions of interest in the image

	returns b&w image where white=interesting, black=uninteresting
	"""
	program=[] # (weight, function)
	if not has_opencv:
		print 'WARN: Attempting auto-detection of regions of interest.'
		print '      This works A LOT better with OpenCV installed.'
		print '      try: pip install opencv-contrib-python'
		print '      or go here: https://sourceforge.net/projects/opencvlibrary/files/'
		program=[(1,highContrast)]
	else:
		program=[(1,faces),(0.5,skin),(0.05,highContrast)]
	outImage=Image.new('L',image.size,0)
	totalWeight=0
	for weight,_ in program:
		totalWeight+=weight
	for weight,fn in program:
		weight=weight*totalWeight
		if weight<0.01:
			#print "skipping",fn.__name__
			continue
		#print "calculating",fn.__name__
		im=fn(image)
		if weight<0.99:
			#print " - adjusting",fn.__name__,'to',weight
			contrastAdjustment=ImageEnhance.Brightness(im)
			contrastAdjustment.enhance(weight)
		outImage=ImageChops.add(outImage,im)
	return outImage


if __name__ == '__main__':
	import sys
	# Use the Psyco python accelerator if available
	# See:
	# 	http://psyco.sourceforge.net
	try:
		import psyco
		psyco.full() # accelerate this program
	except ImportError:
		pass
	printhelp=False
	if len(sys.argv)<2:
		printhelp=True
	else:
		for arg in sys.argv[1:]:
			if arg.startswith('-'):
				arg=[a.strip() for a in arg.split('=',1)]
				if arg[0] in ['-h','--help']:
					printhelp=True
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				print 'ERR: unknown argument "'+arg+'"'
	if printhelp:
		print 'Usage:'
		print '  autoInterest.py [options]'
		print 'Options:'
		print '   NONE'
