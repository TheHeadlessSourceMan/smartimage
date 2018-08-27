#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Tools for performing operations in different number domains, such as:
	gradient (derivative)
	polar
	frequency
"""
import numpy as np
from helper_routines import *


def gradient(img):
	"""
	get the derivitive/gradient from the image
		
	https://en.wikipedia.org/wiki/Image_gradient
	https://en.wikipedia.org/wiki/Gradient-domain_image_processing

	For possible uses, see:
		https://www.youtube.com/watch?v=70aLm2zv2ao
			Explaination of above: https://www.cv-foundation.org/openaccess/content_cvpr_2016/papers/Shibata_Gradient-Domain_Image_Reconstruction_CVPR_2016_paper.pdf
		http://www.ok.sc.e.titech.ac.jp/res/res.shtml
		http://grail.cs.washington.edu/projects/gradientshop/
		http://eric-yuan.me/poisson-blending/
		https://sandipanweb.wordpress.com/2017/10/03/some-variational-image-processing-possion-image-editing-and-its-applications/
	Or search for:
		"gradient-domain image processing"
		
	Alternative implementations:
		http://grail.cs.washington.edu/projects/gradientshop/
	"""
	return np.gradient(numpyArray(img))
	
	
def inverseGradient(g):
	"""
	return a gradient back into an image by solving poisson's equation
	
	See also:
		https://people.eecs.berkeley.edu/~demmel/cs267/lecture24/lecture24.html
		https://translate.google.com/translate?sl=auto&tl=en&js=y&prev=_t&hl=en&ie=UTF-8&u=https%3A%2F%2Fpebbie.wordpress.com%2F2012%2F04%2F04%2Fpython-poisson-image-editing%2F&edit-text=
	
	Implementations:
		I really need to use this! https://github.com/daleroberts/poisson/blob/master/poisson.py
	"""
	raise NotImplementedError()
	
	
def selectPoisson(img,location,tolerance):
	"""
	extract a portion of an image by solving poisson
	
	This is more advanced, but slower than selectByPoint()
	used mainly with hair and other soft edges.
	
	See also:
		https://web.archive.org/web/20060916151759/www.cs.virginia.edu/~gfx/courses/2006/DataDriven/bib/matting/sun04.pdf
	
	Implementations:
		https://github.com/MarcoForte/poisson-matting
	"""
	raise NotImplementedError()
	
	
def gradientPaste(overImage,pastedImage,location):
	"""
	Combine images using gradients for a more seamless fit.
	
	Examples:
		http://www.connellybarnes.com/work/class/2013/cs6501/proj2/
		https://en.wikipedia.org/wiki/Gradient-domain_image_processing
	"""
	raise NotImplementedError()
	
	
def kuwahara(img):
	"""
	apply a Kuwahara filter to the image to simplify it
	
	this is excellent for optimization, scaling, and painterly effects
	
	NOTE: this is probably beyond the scope of this project
	
	See also:
		http://www.kyprianidis.com/p/eg2011/
	
	for lots of sexy pics, check out this slideshow:
		https://www.slideshare.net/chiaminhsu/study-image-and-video-abstraction-by-multi-scale-anisotropic-kuwahara
	"""
	raise NotImplementedError()
	
	
def toFrequency(img):
	"""
	Convert an image to frequency domain
	
	NOTE: For those who want a visual introduction into frequency transforms,
	check out this video:
		https://www.youtube.com/watch?v=spUNpyF58BY
	"""
	if True:
		return np.fft.rfft2(img)
	else: # alternative implementation
		shift=False
		import scipy.fftpack
		a=numpyArray(img)
		freq=scipy.fftpack.fft2(a)
		if shift:
			freq=scipy.fftpack.fftshift(freq)
		return freq
	
	
def fromFrequency(img):
	"""
	Convert an image back from frequency domain
	"""
	if True:
		return np.fft.irfft2(img)
	else: # alternative implementation
		import scipy.fftpack
		a=scipy.fftpack.ifft2(freq)
		return a

	
def cartesian2polar(img, center=None, final_radius=None, initial_radius = None, phase_width = 3000):
	"""
	Comes from:
		https://stackoverflow.com/questions/9924135/fast-cartesian-to-polar-to-cartesian-in-python
	"""	
	from scipy.ndimage.interpolation import map_coordinates
	if center==None:
		center=(img.shape[0]/2,img.shape[1]/2)
	if final_radius==None:
		final_radius=max(img.shape[0],img.shape[1])/2
	if initial_radius is None:
		initial_radius = 0
	phase_width=img.shape[0]/2
	
	theta , R = np.meshgrid(np.linspace(0, 2*np.pi, phase_width), 
		np.arange(initial_radius, final_radius))
	Xcart  = R  * np.cos(theta) + center[0]
	Ycart  = R  * np.sin(theta) + center[1]
	Xcart = Xcart.astype(int)
	Ycart = Ycart.astype(int)
	
	if img.ndim ==3:
		polar_img = img[Ycart,Xcart,:]
		polar_img = np.reshape(polar_img,(final_radius-initial_radius,phase_width,img.shape[-1]))
	else:
		polar_img = img[Ycart,Xcart]
		polar_img = np.reshape(polar_img,(final_radius-initial_radius,phase_width))
	return polar_img
	
	
def cartesian2logpolar(img, center=None, final_radius=None, initial_radius = None, phase_width = 3000):
	"""
	See also:
		https://en.wikipedia.org/wiki/Log-polar_coordinates
	"""	
	from scipy.ndimage.interpolation import map_coordinates
	if center==None:
		center=(img.shape[0]/2,img.shape[1]/2)
	if final_radius==None:
		final_radius=max(img.shape[0],img.shape[1])/2
	if initial_radius is None:
		initial_radius = 0
	phase_width=img.shape[0]/2
	
	theta , R = np.meshgrid(np.linspace(0, 2*np.pi, phase_width), 
		np.arange(initial_radius, final_radius))
	Xcart  = numpy.exp(R)  * np.cos(theta) + center[0]
	Ycart  = numpy.exp(R)  * np.sin(theta) + center[1]
	Xcart = Xcart.astype(int)
	Ycart = Ycart.astype(int)
	
	if img.ndim ==3:
		polar_img = img[Ycart,Xcart,:]
		polar_img = np.reshape(polar_img,(final_radius-initial_radius,phase_width,img.shape[-1]))
	else:
		polar_img = img[Ycart,Xcart]
		polar_img = np.reshape(polar_img,(final_radius-initial_radius,phase_width))
	return polar_img	

	
	
def polar2cartesian(polar_data):
	"""
	From:
		https://stackoverflow.com/questions/2164570/reprojecting-polar-to-cartesian-grid
	"""
	
	from scipy.ndimage.interpolation import map_coordinates

	theta_step=1
	range_step=500
	x=np.arange(-100000, 100000, 1000)
	y=x
	order=3
	
	# "x" and "y" are numpy arrays with the desired cartesian coordinates
	# we make a meshgrid with them
	X, Y = np.meshgrid(x, y)

	# Now that we have the X and Y coordinates of each point in the output plane
	# we can calculate their corresponding theta and range
	Tc = np.degrees(np.arctan2(Y, X)).ravel()
	Rc = (np.sqrt(X**2 + Y**2)).ravel() # TODO: is np.hypot(X,Y) faster?

	# Negative angles are corrected
	Tc[Tc < 0] = 360 + Tc[Tc < 0]

	# Using the known theta and range steps, the coordinates are mapped to
	# those of the data grid
	Tc = Tc / theta_step
	Rc = Rc / range_step

	# An array of polar coordinates is created stacking the previous arrays
	#coords = np.vstack((Ac, Sc))
	coords = np.vstack((Tc, Rc))

	# To avoid holes in the 360º - 0º boundary, the last column of the data
	# copied in the begining
	polar_data = np.vstack((polar_data, polar_data[-1,:]))

	# The data is mapped to the new coordinates
	# Values outside range are substituted with nans
	cart_data = map_coordinates(polar_data, coords, order=order, mode='constant', cval=np.nan)

	# The data is reshaped and returned
	return(cart_data.reshape(len(Y), len(X)).T)

def logpolar2cartesian(polar_data):
	"""
	From:
		https://stackoverflow.com/questions/2164570/reprojecting-polar-to-cartesian-grid
	"""
	
	from scipy.ndimage.interpolation import map_coordinates

	theta_step=1
	range_step=500
	x=np.arange(-100000, 100000, 1000)
	y=x
	order=3
	
	# "x" and "y" are numpy arrays with the desired cartesian coordinates
	# we make a meshgrid with them
	X, Y = np.meshgrid(x, y)

	# Now that we have the X and Y coordinates of each point in the output plane
	# we can calculate their corresponding theta and range
	Tc = np.degrees(np.arctan2(Y, X)).ravel()
	Rc = np.ln(np.sqrt(X**2 + Y**2)).ravel()

	# Negative angles are corrected
	Tc[Tc < 0] = 360 + Tc[Tc < 0]

	# Using the known theta and range steps, the coordinates are mapped to
	# those of the data grid
	Tc = Tc / theta_step
	Rc = Rc / range_step

	# An array of polar coordinates is created stacking the previous arrays
	#coords = np.vstack((Ac, Sc))
	coords = np.vstack((Tc, Rc))

	# To avoid holes in the 360º - 0º boundary, the last column of the data
	# copied in the begining
	polar_data = np.vstack((polar_data, polar_data[-1,:]))

	# The data is mapped to the new coordinates
	# Values outside range are substituted with nans
	cart_data = map_coordinates(polar_data, coords, order=order, mode='constant', cval=np.nan)

	# The data is reshaped and returned
	return(cart_data.reshape(len(Y), len(X)).T)
	
	
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
		print '  numberSpaces.py [options]'
		print 'Options:'
		print '   NONE'