#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This allows color correction (curves, levels, etc) of PIL images
"""
from PIL import Image
import numpy as np
from helper_routines import *
from selectionsAndPaths import strToColor
from math import *
	
"""
TODO: implement VSCO terminology

	auto/normalization (get things into a baseline that filters can operate upon)
	
	# hue
	highlightTint(amount,color=None)
	midtoneTint(amount,color=None)
	shadowTint(amount,color=None)
	tint
	colorTemperature
	warmth
	
	# saturation
	saturation
	
	# value
	highlightValue
	shadowValue
	exposure
	fade -- nothing more than a simple greying via the levels adjustment
	brightness
	contrast
	
	# other
	clarity -- an unsharp mask??
	Vingette
	Grain
	skin tone

	# outliers - do not implement
	pink(amount) ???
	dusty texture
"""
	

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
	img=numpyArray(img)
	if type(fn)!=np.lib.function_base.vectorize:
		fn=np.vectorize(fn,signature='(m)->(k)')
	img=fn(img[:,:])
	if clamp:
		img=clampImage(img)
	return img
	
	
def testPerPixel(img):
	rgbM=[1.0,0.50,1.0]
	rgbB=[0,0.5,0]
	def _coloradj(px):
		return px*rgbM+rgbB
	a=perPixel(_coloradj,img)
	return pilImage(a)
	
	
def temperatureToRgb(temperature):
	"""
	Get an RGB color corresponding to the given color temperature
	
	:param temperature: in Kelvin, between 1000 and 40000
	
	NOTES:
		The simple way:
		https://stackoverflow.com/questions/11884544/setting-color-temperature-for-a-given-image-like-in-photoshop
		But we use this for a closer approximation: (still not acceptable for scientific applications)
		http://www.tannerhelland.com/4435/convert-temperature-rgb-algorithm-code/
	"""
	color=[255,255,255]
	temperature=max(min(temperature,40000),1000)/100.0
	if temperature>66:
		color[0]=329.698727446*((temperature-60)**-0.1332047592)
	if temperature<=66:
		color[1]=99.4708025861*log(temperature)-161.1195681661
	else:
		color[1]=288.1221695283*((temperature-60)**-0.0755148492)
	if temperature>66:
		if temperature<=19:
			color[2]=0
		else:
			color[2]=138.5177312231*log(temperature-10)-305.0447927307
	color=[min(max(int(ch),0),255) for ch in color]
	return color
	
	
def adjustTemperature(img,temperature):
	"""
	Adjust the color temperature of the image
	
	:param img: the image to apply the filter to (ONLY works with RGB!!!)
	:param temperature: in Kelvin, between 1000 and 40000
	"""
	return colorize(img,temperatureToRgb(temperature),keepSaturation=1.0)

	
def photoFilter(img,filter,density=1.0,preserveLuminosity=True):
	"""
	Apply a standard Wratten photo filter
	
	:param img: the image to apply the filter to
	:param filter: an id value or a color
	:param density: is an amount value
	:param preserveLuminosity: keep the luminosity of the image the same
	
	NOTES:
		https://web.archive.org/web/20091028192325/http://www.geocities.com/cokinfiltersystem/color_corection.htm
		https://books.googleusercontent.com/books/content?req=AKW5QacXkLUoH7zd0CQIewJCyxldxc_tf40twSNXMRNU6TCWIZBscU2dpQsIDYOPGunH1TcRk1tRcr8d2KypzXy8tmHP8R4hOccXQByB6C9mW-HDb_-94fiXZBumf16vVVrMsT95yWguceeIYM0kTejTVVJsPkS7LDaDIpVAOfkoms3XXgBZ8zVon5ZgpKLG1FR56flEtZ9bsGbDtECr0y8Pzm59tx5GqDh9CRGsqpIM4wowJ3lvsF3PTXI0M4dB_pePP7uYsUmS
	"""
	raise NotImplementedError()
	
def exposure(img,amount):
	"""
	Adjust photographic exposure level
	
	:param img: the image to apply the filter to
	:param amount: in the range -1.0 to 1.0
	
	Reference:
		https://stackoverflow.com/questions/12166117/what-is-the-math-behind-exposure-adjustment-on-photoshop
	"""
	img=rgb2hsvArray(img)
	v=img[:,:,2]*(2**amount)
	img[:,:,2]=v
	img=hsv2rgbArray(img)
	return img
	
def equalize(img,amount=1.0,colorChannels=False):
	"""
	Equalize histogram of the image to balance its levels.
	
	:param img: the image to apply the filter to
	:param amount: in the range -1.0 to 1.0
	:param colorChannels: if True, balance each color channel.  
		If False, convert to HSV and balance the V.
	
	NOTE: if you want to equalize a single channel, separate it out and it in as img
	
	See also:
		http://en.wikipedia.org/wiki/Histogram_equalization
		http://www.janeriksolem.net/2009/06/histogram-equalization-with-python-and.html
	"""
	img=numpyArray(img)
	if len(img.shape)<3:
		# we have multiple channels
		if colorChannels:
			img[:,:,0]=equalize(img[:,:,0],amount,False)
			img[:,:,1]=equalize(img[:,:,1],amount,False)
			img[:,:,2]=equalize(img[:,:,2],amount,False)
		else:
			img=rgb2hsvArray(img)
			img[:,:,2]=equalize(img[:,:,2],amount,False)
			img=hsv2rgbArray(img)
	else:
		# perform the equalization
		numBins=256
		imgNew=img.flatten()
		# get the histogram
		image_histogram,bins=np.histogram(imgNew,numBins,normed=True)
		cdf=image_histogram.cumsum() # cumulative distribution function
		cdf=255*cdf/cdf[-1] # normalize
		# use linear interpolation of cdf to find new pixel values
		imgNew=np.interp(imgNew,bins[:-1],cdf)*amount+imgNew/amount
		img=imgNew.reshape(img.shape),cdf
	return img
	
def colorize(img,color,keepSaturation=0.0):
	"""
	Colorize the image to a given color.  This can be used for things
	like sepia images.
	
	:param img: the image to apply the filter to
	:param color: the color to tint to
	:param keepSaturation: how much of the original saturation to keep (verses take from the given color)
	
	Reference:
		http://www.tannerhelland.com/3552/colorize-image-vb6/
	"""
	img=rgb2hsvArray(img)
	color=rgb2hsvArray(strToColor(color))
	img[:,:,0]=color[0]
	if keepSaturation<1.0:
		if keepSaturation<=0.0:
			img[:,:,1]=color[1]
		else:
			color[1]=color[1]/keepSaturation
			img[:,:,1]=img[:,:,1]*keepSaturation+color[1]
	img=hsv2rgbArray(img)
	return img
	
	
def levels(img,shadows=0,midtones=0.5,higlights=1,clampBlack=0,clampWhite=1):
	"""
	Perform a levels color adjustment on the given image
	
	:param img: the image to apply the filter to
	:param shadows: new level to shift shadows to (higher values=more darks)
	:param midtones: new level to shift the mid-point to
	:param higlights: new level to shift highlights to (lower values=more darks)
	:param clampBlack: clamp the black pixels to this value
	:param clampBlack: clamp the white pixels to this value
	"""
	return curves(img,[[shadows,0],[midtones,0.5],[higlights,1]],clampBlack,clampWhite)	

	
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
	if len(img.shape)<3:
		resultPoints=spline(img[:,:],extrapolate=extrapolate)[:,:,0] # for some reason it keeps the original point, which we need to strip off
	else:
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
					pilImage(image).show()
				elif arg[0]=='--save':
					image.save(arg[1])
				elif arg[0]=='--adjustTemperature':
					t=float(arg[1])
					image=adjustTemperature(image,t)
				elif arg[0]=='--exposure':
					amt=float(arg[1])
					image=exposure(image,amt)
				elif arg[0]=='--photoFilter':
					density=1.0
					preserveLuminosity=True
					aa=arg[1].split(',')
					name=aa[0]
					if len(aa)>1:
						density=float(aa[1])
						if len(aa)>2:
							preserveLuminosity=aa[2][0] in ['Y','y','T','t','1']
					image=photoFilter(image,name,density,preserveLuminosity)
				elif arg[0]=='--colorize':
					keepSat=True
					aa=arg[1].split(',')
					name=aa[0]
					if len(aa)>1:
						keepSat=aa[1][0] in ['Y','y','T','t','1']
					image=colorize(image,name,keepSat)
				elif arg[0]=='--equalize':
					colorCh=True
					aa=arg[1].split(',')
					color=aa[0]
					if len(aa)>1:
						colorCh=aa[1][0] in ['Y','y','T','t','1']
					image=equalize(image,color,colorCh)
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
		print '   --adjustTemperature=t ......... adjust to the given color temperature (in kelvin)'
		print '   --exposure=amount ............. adjust image exposure'
		print '   --photoFilter=name,density,preserveLuminosity .... apply a photograhy filter'
		print '   --colorize=color[,keepSat] .... colorize the image, optionally keeping some amount of the original saturation'
		print '   --equalize[=amount[,colorCh]] . equalize the image\'s histogram (colorCh=T/F to equalize colors as well)'
		print '   --levels=low,mid,high,min,max . perfom a levels color adjustment (all values 0..1)'
		print '   --curves=[x,y][x,y][...] ...... perfom a curves color adjustment using the given points (all values 0..1)'