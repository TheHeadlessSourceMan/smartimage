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
	
	
def perPixel(fn,image,clamp=True):
	"""
	Call fn once per each pixel in the img.
	
	Since this is a looping thing, it can be rather slow.
	Your best bet is to construct your algorithm out of numpy's ufuncs.
	
	:param fn: the function to call for each pixel
	:param image: the image to operate upon
	:param clamp: call clampImage() once everything is all done
	
	:return: the adjusted image
	"""
	image=numpyArray(image)
	if type(fn)!=np.lib.function_base.vectorize:
		fn=np.vectorize(fn,signature='(m)->(k)')
	image=fn(image[:,:])
	if clamp:
		image=clampImage(image)
	return image
	
	
def temperatureToRgb(temperature):
	"""
	Get an RGB color corresponding to the given color temperature
	
	:param temperature: in Kelvin, between 1000 and 40000
	
	:return: an RGB color
	
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
	
	
def adjustTemperature(image,temperature):
	"""
	Adjust the color temperature of the image
	
	:param image: the image to apply the filter to (ONLY works with RGB!!!)
	:param temperature: in Kelvin, between 1000 and 40000
	
	:return: an image adjusted by the color temperature
	"""
	return colorize(image,temperatureToRgb(temperature),keepSaturation=1.0)
	
	
def _pointsToRanges(points):
	"""
	Given an array of points, returns floating point range tuples for
	all values between those points.
	
	For example:
		[0.15,0.8]
		returns
		[(-inf,0.15),(0.15,0.8),(0.8,inf)]
		
	Always returns a list of ranges, even if it is [(-inf,inf)]
	"""
	ret=[]
	last=np.NINF
	for p in points:
		ret.append((last,p))
	ret.append(last,np.Infinity)
	return ret
	
	
def toneSplit(image,atPoints=[0.15,0.85],absolute=False):
	"""
	Break an image into n+1 images at selected value points.
	
	The default points are to get images for tritone adjustment
	
	:param image: image to split
	:param atPoints: what grayscale values to split the image
	:param absolute: whether atPoints are absolute values or 
		percentages of the available space
		
	:return: given n atPoints, will return n+1 images
	"""
	ret=[]
	if not absolute:
		b=min(1.0,np.max(image))
		m=1/(max(0.0,np.min(image))-b)
	else:
		b=0
		m=1
	for range in _pointsToRanges(atPoints):
		ret.append(np.logical_and(image>=range[0]*m+b,image<range[1]*m+b),atPoints)
	return ret
	
	
def toneCombine(image,tones,toneAmounts=1.0):
	"""
	This is essentially just a compositor that re-layers any number of tones on top of an image
	
	:param image: The underlying image.
	:param tones: An array of images representing individual tones
	:param toneAmounts: A single value for all or an array representing individual tone amounts
	
	:return: the combined image
	"""
	import compositor
	if type(toneAmounts) in [int,float]:
		toneAmounts=[toneAmounts for i in range(len(tones))]
	numTones=len(tones)
	for i in range(numTones):
		tone=compositor.adjustOpacity(tones[i],toneAmounts[i])
		image=compositor.blend(tone,'normal',image)
	return image
	
	
def tritoneTint(image,tintColors,tintAmounts=1.0,atPoints=[0.15,0.85],absolute=False):
	"""
	A "standard" tritone color adjuster.
	
	Does a toneSplit, a tint on each image, then a toneCombine.
	"""
	tones=toneSplit(image,atPoints,absolute)
	if type(tintAmounts) in [int,float]:
		tintAmounts=[tintAmounts for i in range(len(tones))]
	for i in range(len(tones)):
		tones[i]=tint(tones[i],tintColors[i],tintAmounts[i])
	return toneCombine(image,tones)
	
	
def tint(image,tintColor,amount=1.0):
	"""
	Tint an image to the given color

	:param image: an image to tint
	:param tintColor: the color to tint to
	:param amount: percent to tint
	
	:return: the adjusted image
	"""
	image=rgb2hsvArray(image)
	tintColor=rgb2hsvArray(tintColor)
	image[:,:,0:1]=((1-amount)*image[:,:,0:1]+amount*tintColor[0:1])
	return hsv2rgbArray(image)
	
	
WRATTEN_TRANSMISSION_CURVES=[ # name:curvepoints
	]
def photoFilter(image,filter,density=1.0,preserveLuminosity=True):
	"""
	Apply a standard Wratten photo filter
	
	:param image: the image to apply the filter to
	:param filter: can be a transmittence curve or a wratten number
	:param density: is an amount value
	:param preserveLuminosity: keep the luminosity of the image the same
	
	:return: the adjusted image
	
	NOTES:
		https://web.archive.org/web/20091028192325/http://www.geocities.com/cokinfiltersystem/color_corection.htm
		https://books.googleusercontent.com/books/content?req=AKW5QacXkLUoH7zd0CQIewJCyxldxc_tf40twSNXMRNU6TCWIZBscU2dpQsIDYOPGunH1TcRk1tRcr8d2KypzXy8tmHP8R4hOccXQByB6C9mW-HDb_-94fiXZBumf16vVVrMsT95yWguceeIYM0kTejTVVJsPkS7LDaDIpVAOfkoms3XXgBZ8zVon5ZgpKLG1FR56flEtZ9bsGbDtECr0y8Pzm59tx5GqDh9CRGsqpIM4wowJ3lvsF3PTXI0M4dB_pePP7uYsUmS
	"""
	raise NotImplementedError()
	
	
def posterize(image):
	"""
	Posterize an image, that is, more or less to clamp each color to the nearest multiple of 1/4
	
	:param image: the image to posterize
	
	:return: the converted image
	"""
	image=numpyArray(image)
    return np.where(image<=0.25,0.20,np.where(image<=0.5,0.40,np.where(image<=0.75,0.60,0.80)))
	
	
def solarize(image):
	"""
	Solarize an image
	
	:param image: the image to solarize
	
	:return: the converted image
	"""
	image=numpyArray(image)
	image[image[:,:,0:2]<0.5]=1.0-image[:,:,0:2]
	return image
	

def sepia(image):
	"""
	Convert an image into sepia.
	
	:param image: the image to convert
	
	:return: the converted image
	
	NOTE: This can be done in more generic by combining filters ways.
	"""
	image=numpyArray(image)
    return [
		(image[:,:,0]*0.393)+(image[:,:,1]*0.769)+(image[:,:,2]*0.189),
		(image[:,:,0]*0.349)+(image[:,:,1]*0.686)+(image[:,:,2]*0.168),
		(image[:,:,0]*0.272)+(image[:,:,1]*0.534)+(image[:,:,2]*0.131)]

	
def exposure(image,amount):
	"""
	Adjust the relative photographic exposure level
	
	:param img: the image to apply the filter to
	:param amount: in the range -1.0 to 1.0 such that 0.0 is no change
	
	:return: the adjusted image
	
	Reference:
		https://stackoverflow.com/questions/12166117/what-is-the-math-behind-exposure-adjustment-on-photoshop
	"""
	if amount==0.0:
		return image
	image=rgb2hsvArray(image)
	v=image[:,:,2]*(2**amount)
	image[:,:,2]=v
	image=hsv2rgbArray(image)
	return image
	
	
def gammaAdjust(image,gamma,invert=True):
	"""
	:param image: the input image
	:param gamma: the gamma amount to adjust
	:param invert: is practically useless in that all it does is 1/gamma, 
		but it does remind us that gammas are usually stored 1/g
		
	:return: adjusted image
	
	See also:
		https://en.wikipedia.org/wiki/Gamma_correction#Methods_to_perform_display_gamma_correction_in_computing
		https://www.pyimagesearch.com/2015/10/05/opencv-gamma-correction/
	"""
	if invert:
		gamma=1/gamma
	return np.pow(numpyArray(image),gamma)
	
	
def equalize(image,amount=1.0,colorChannels=False):
	"""
	Equalize histogram of the image to balance its levels.
	
	:param img: the image to apply the filter to
	:param amount: in the range -1.0 to 1.0
	:param colorChannels: if True, balance each color channel.  
		If False, convert to HSV and balance the V.
	
	:return: the adjusted image
	
	NOTE: if you want to equalize a single channel, separate it out and it in as img
	
	See also:
		http://en.wikipedia.org/wiki/Histogram_equalization
		http://www.janeriksolem.net/2009/06/histogram-equalization-with-python-and.html
	"""
	image=numpyArray(image)
	if len(image.shape)<3:
		# we have multiple channels
		if colorChannels:
			image[:,:,0]=equalize(image[:,:,0],amount,False)
			image[:,:,1]=equalize(image[:,:,1],amount,False)
			image[:,:,2]=equalize(image[:,:,2],amount,False)
		else:
			image=rgb2hsvArray(image)
			image[:,:,2]=equalize(image[:,:,2],amount,False)
			image=hsv2rgbArray(image)
	else:
		# perform the equalization
		numBins=256
		imageNew=image.flatten()
		# get the histogram
		image_histogram,bins=np.histogram(imageNew,numBins,normed=True)
		cumulativeDistributionFunction=image_histogram.cumsum()
		cumulativeDistributionFunction=255*cumulativeDistributionFunction/cumulativeDistributionFunction[-1] # normalize
		# use linear interpolation of cumulativeDistributionFunction to find new pixel values
		imageNew=np.interp(imageNew,bins[:-1],cumulativeDistributionFunction)*amount+imageNew/amount
		image=imageNew.reshape(image.shape),cumulativeDistributionFunction
	return image
	
	
def colorize(image,color,keepSaturation=0.0):
	"""
	Colorize the image to a given color.  This can be used for things
	like sepia images.
	
	:param image: the image to apply the filter to
	:param color: the color to tint to
	:param keepSaturation: how much of the original saturation to keep (verses take from the given color)
	
	:return: colorized image
	
	Reference:
		http://www.tannerhelland.com/3552/colorize-image-vb6/
	"""
	image=rgb2hsvArray(image)
	color=rgb2hsvArray(strToColor(color))
	image[:,:,0]=color[0]
	if keepSaturation<1.0:
		if keepSaturation<=0.0:
			image[:,:,1]=color[1]
		else:
			color[1]=color[1]/keepSaturation
			image[:,:,1]=image[:,:,1]*keepSaturation+color[1]
	image=hsv2rgbArray(image)
	return image
	
	
def levels(image,shadows=0,midtones=0.5,higlights=1,clampBlack=0,clampWhite=1):
	"""
	Perform a levels color adjustment on the given image
	
	:param image: the image to apply the filter to
	:param shadows: new level to shift shadows to (higher values=more darks)
	:param midtones: new level to shift the mid-point to
	:param higlights: new level to shift highlights to (lower values=more darks)
	:param clampBlack: clamp the black pixels to this value
	:param clampBlack: clamp the white pixels to this value
	
	:return: adjusted image
	"""
	return curves(image,[[shadows,0],[midtones,0.5],[higlights,1]],clampBlack,clampWhite)	

	
def curves(image,controlPoints,clampBlack=0,clampWhite=1,degree=None,extrapolate=True):
	"""
	Perform a curves adjustment on an image
	
	:param image: evaluate the curve at these points can be pil image or numpy array
	:param controlPoints: set of [x,y] points that define the mapping
	:param clampBlack: clamp the black pixels to this value
	:param clampBlack: clamp the white pixels to this value
	:param degree: polynomial degree (if omitted, make it the same as the number of control points)
	:param extrapolate: go beyond the defined area of the curve to get values (oterwise returns NaN for outside values)
	
	:return: the adjusted image
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
				elif arg[0]=='--gamma':
					gamma=float(arg[1])
					image=gammaAdjust(image,gamma)
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
		print '   --gamma=gamma ................. adjust image gamma value'
		print '   --photoFilter=name,density,preserveLuminosity .... apply a photograhy filter'
		print '   --colorize=color[,keepSat] .... colorize the image, optionally keeping some amount of the original saturation'
		print '   --equalize[=amount[,colorCh]] . equalize the image\'s histogram (colorCh=T/F to equalize colors as well)'
		print '   --levels=low,mid,high,min,max . perfom a levels color adjustment (all values 0..1)'
		print '   --curves=[x,y][x,y][...] ...... perfom a curves color adjustment using the given points (all values 0..1)'