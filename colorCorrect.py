#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This allows color correction (curves, levels, etc) of PIL images
"""
from PIL import Image
import numpy as np
from helper_routines import *
	

def fft(img,shift=False):
	import scipy.fftpack
	a=numpyArray(img)
	freq=scipy.fftpack.fft2(a)
	if shift:
		freq=scipy.fftpack.fftshift(freq)
	return freq

		
def ifft(freq):
	import scipy.fftpack
	a=scipy.fftpack.ifft2(freq)
	return pilImage(a)
	
	
def perPixel(fn,img,clamp=True):
	"""
	Call fn once per each pixel in the img.
	
	Since this is a looping thing, it can be rather slow.
	Your best bet is to construct your algorithm out of numpy's ufuncs.
	"""
	a=numpyArray(img)
	if type(fn)!=np.lib.function_base.vectorize:
		fn=np.vectorize(fn,signature='(m)->(k)')
	pixels=np.reshape(a,(-1,3))
	pixels=fn(pixels)
	a=np.reshape(pixels,a.shape)
	if clamp:
		a=clampImage(a)
	return a
	
	
def testPerPixel(img):
	rgbM=[1.0,0.50,1.0]
	rgbB=[0,0.5,0]
	def _coloradj(px):
		return px*rgbM+rgbB
	a=perPixel(_coloradj,img)
	return pilImage(a)
	
	
def levels(img,shadows=0,midtones=0.5,higlights=1,clampBlack=0,clampWhite=1):
	return curves(img,[[shadows,0],[midtones,0.5],[higlights,1]],clampBlack=0,clampWhite=1)

	
def curves(img,controlPoints,clampBlack=0,clampWhite=1,degree=None,extrapolate=True):
	"""
	:param img: evaluate the curve at these points can be pil image or numpy array
	:param controlPoints: set of [x,y] points that define the mapping
	:param clampBlack: clamp the black pixels to this value
	:param clampBlack: clamp the white pixels to this value
	:param degree: polynomial degree (if omitted, make it the same as the number of control points)
	:param extrapolate: go beyond the defined area of the curve to get values (oterwise returns NaN for outside values)
	:return mapped: the new points that correlate to the img points
	"""
	import scipy.interpolate
	img=numpyArray(img)
	count=len(controlPoints)
	if degree==None:
		degree=count-1
	else:
		degree=np.clip(degree,1,count-1)
	knots=np.clip(np.arange(count+degree+1)-degree,0,count-degree)
	spline=scipy.interpolate.BSpline(knots,controlPoints,degree)
	resultPoints=spline(img[:,:,:],extrapolate=extrapolate)[:,:,:,0] # for some reason it keeps the original point, which we need to strip off
	resultPoints=clampImage(resultPoints,clampBlack,clampWhite)
	return pilImage(resultPoints)

		
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
		import json,time
		currentChannel='RGB'
		image=None
		for arg in sys.argv[1:]:
			if arg.startswith('-'):
				arg=[a.strip() for a in arg.split('=',1)]
				if arg[0] in ['-h','--help']:
					printhelp=True
				elif arg[0]=='--channel':
					currentChannel=arg[1]
				elif arg[0]=='--show':
					image.show()
				elif arg[0]=='--save':
					image.save(arg[1])
				elif arg[0]=='--levels':
					if len(arg)>1:
						params=[float(v) for v in arg[1].split(',')]
					else:
						params=[]
					image=levels(image,*params)
				elif arg[0]=='--curves':
					points=[[float(xy) for xy in pt.split(',')[-2:]] for pt in arg[1][0:-1].replace('[','').split(']')]
					image=curves(image,points)
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				image=Image.open(arg)
	if printhelp:
		print 'Usage:'
		print '  colorCorrect.py input.jpg [options]'
		print 'Options:'
		print "   --channel=R ................... 'R','G','B','RGB',or 'A'"
		print '   --show ........................ display the output image'
		print '   --save=filename ............... save the output image'
		print '   --levels=low,mid,high,min,max . perfom a levels color adjustment (all values 0..1)'
		print '   --curves=[x,y][x,y][...] ...... perfom a curves color adjustment using the given points (all values 0..1)'