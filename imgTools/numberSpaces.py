#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Tools for performing operations in different number domains, such as:
	gradient (derivative)
	polar
	frequency
"""
try:
	# first try to use bohrium, since it could help us accelerate
	# https://bohrium.readthedocs.io/users/python/
	import bohrium as np
except ImportError:
	# if not, plain old numpy is good enough
	import numpy as np
import scipy
try:
	import pywt
except ImportError,e:
	print "ERR: Missing PyWavelet."
	print "Install with:\n\tpip install PyWavelet\nOr go to:\n\thttps://pywavelets.readthedocs.io"
	raise e
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


def toCosine(img):
	"""
	Run a cosine transform on an image

	See also:
		https://en.wikipedia.org/wiki/Discrete_cosine_transform
	"""
	return scipy.fftpack.dctn(img)
def fromCosine(img):
	"""
	Convert from a cosine transform back into an image
	"""
	return scipy.fftpack.idctn(img)

def toSine(img):
	"""
	Run a sine transform on an image
	"""
	return scipy.fftpack.dstn(img)
def fromSine(img):
	"""
	Convert from a sine transform back into an image
	"""
	return scipy.fftpack.idstn(img)

def toLaplacianPyramid(img,levels):
	"""
	create a laplacian pyramid from an image

	See also:
		https://en.wikipedia.org/wiki/Pyramid_(image_processing)
	"""
	return lapl_pyramid(gauss_pyramid(img,levels))
def fromLaplacianPyramid(img):
	"""
	convert from laplacian pytamid to flat image
	"""
	return collapse(img)


def generating_kernel(a):
	"""
	generate a 5x5 kernel

	Comes from:
		https://compvisionlab.wordpress.com/2013/05/13/image-blending-using-pyramid/
	"""
	w_1d = np.array([0.25 - a/2.0, 0.25, a, 0.25, 0.25 - a/2.0])
	return np.outer(w_1d, w_1d)


def ireduce(image):
	"""
	reduce image by 1/2

	Comes from:
		https://compvisionlab.wordpress.com/2013/05/13/image-blending-using-pyramid/
	"""
	out = None
	kernel = generating_kernel(0.4)
	outimage = scipy.signal.convolve2d(image,kernel,'same')
	out = outimage[::2,::2]
	return out


def iexpand(image):
	"""
	expand image by factor of 2

	Comes from:
		https://compvisionlab.wordpress.com/2013/05/13/image-blending-using-pyramid/
	"""
	out = None
	kernel = generating_kernel(0.4)
	outimage = np.zeros((image.shape[0]*2, image.shape[1]*2), dtype=np.float64)
	outimage[::2,::2]=image[:,:]
	out = 4*scipy.signal.convolve2d(outimage,kernel,'same')
	return out


def gauss_pyramid(image, levels):
	"""
	create a gaussain pyramid of a given image

	Comes from:
		https://compvisionlab.wordpress.com/2013/05/13/image-blending-using-pyramid/
	"""
	output = []
	output.append(image)
	tmp = image
	for _ in range(0,levels):
		tmp = ireduce(tmp)
		output.append(tmp)
	return output


def lapl_pyramid(gauss_pyr):
	"""
	build a laplacian pyramid

	Comes from:
		https://compvisionlab.wordpress.com/2013/05/13/image-blending-using-pyramid/
	"""
	output = []
	k = len(gauss_pyr)
	for i in range(0,k-1):
		gu = gauss_pyr[i]
		egu = iexpand(gauss_pyr[i+1])
		if egu.shape[0] > gu.shape[0]:
			egu = np.delete(egu,(-1),axis=0)
		if egu.shape[1] > gu.shape[1]:
			egu = np.delete(egu,(-1),axis=1)
		output.append(gu - egu)
	output.append(gauss_pyr.pop())
	return output

def blend(lapl_pyr_white, lapl_pyr_black, gauss_pyr_mask):
	"""
	Blend the two laplacian pyramids by weighting them according to the mask.

	Comes from:
		https://compvisionlab.wordpress.com/2013/05/13/image-blending-using-pyramid/
	"""
	blended_pyr = []
	k= len(gauss_pyr_mask)
	for i in range(0,k):
		p1= gauss_pyr_mask[i]*lapl_pyr_white[i]
		p2=(1 - gauss_pyr_mask[i])*lapl_pyr_black[i]
		blended_pyr.append(p1 + p2)
	return blended_pyr

def collapse(lapl_pyr):
	"""
	Reconstruct the image based on its laplacian pyramid.

	Comes from:
		https://compvisionlab.wordpress.com/2013/05/13/image-blending-using-pyramid/
	"""
	output = None
	output = np.zeros((lapl_pyr[0].shape[0],lapl_pyr[0].shape[1]), dtype=np.float64)
	for i in range(len(lapl_pyr)-1,0,-1):
		lap = iexpand(lapl_pyr[i])
		lapb = lapl_pyr[i-1]
		if lap.shape[0] > lapb.shape[0]:
			lap = np.delete(lap,(-1),axis=0)
		if lap.shape[1] > lapb.shape[1]:
			lap = np.delete(lap,(-1),axis=1)
		tmp = lap + lapb
		lapl_pyr.pop()
		lapl_pyr.pop()
		lapl_pyr.append(tmp)
		output = tmp
	return output


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
		a=scipy.fftpack.ifft2(img)
		return a


def cartesian2polar(img, center=None, final_radius=None, initial_radius = None, phase_width = 3000):
	"""
	Comes from:
		https://stackoverflow.com/questions/9924135/fast-cartesian-to-polar-to-cartesian-in-python
	"""
	from scipy.ndimage.interpolation import map_coordinates
	img=numpyArray(img)
	if center is None:
		center=(img.shape[0]/2,img.shape[1]/2)
	if final_radius is None:
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
	if center is None:
		center=(img.shape[0]/2,img.shape[1]/2)
	if final_radius is None:
		final_radius=max(img.shape[0],img.shape[1])/2
	if initial_radius is None:
		initial_radius = 0
	phase_width=img.shape[0]/2

	theta , R = np.meshgrid(np.linspace(0, 2*np.pi, phase_width),
		np.arange(initial_radius, final_radius))
	Xcart  = np.exp(R)  * np.cos(theta) + center[0]
	Ycart  = np.exp(R)  * np.sin(theta) + center[1]
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


def _wavelet(wavelet='haar'):
	"""
	:param wavelet: any common, named wavelet, including
			'Haar' (default)
			'Daubechies'
			'Symlet'
			'Coiflet'
			'Biorthogonal'
			'ReverseBiorthogonal'
			'DiscreteMeyer'
			'Gaussian'
			'MexicanHat'
			'Morlet'
			'ComplexGaussian'
			'Shannon'
			'FrequencyBSpline'
			'ComplexMorlet'
		or a custom [ [lowpass_decomposition],
			[highpass_decomposition],
			[lowpass_reconstruction],
			[highpass_reconstruction] ]
		where each is a pair of floating point values

		NOTE: Coefficients for the hundreds of built-in wavelets can be found at:
			http://wavelets.pybytes.com/
	"""
	nameMap={
		'haar':'haar',
		'daubechies':'db1',
		'symlet':'sym1',
		'coiflet':'coif1',
		'biorthogonal':'bior1.1',
		'reversebiorthogonal':'rbio1.1',
		'discretemeyer':'dmey',
		'gaussian':'gaus1',
		'mexicanhat':'mexh',
		'morlet':'morl',
		'complexgaussian':'cgau1',
		'shannon':'shan',
		'frequencybspline':'fbsp',
		'complexmorlet':'cmor'
		}
	#print pywt.wavelist()
	if isinstance(wavelet,list):
		return pywt.Wavelet(name="myLilWavelet",filter_bank=wavelet)
	return nameMap[wavelet.lower().replace(' ','').replace('_','')]


def toWavelet(img,wavelet='haar',mode='symmetric',level=None):
	"""
	:param img: any supported image type to transform into wavelet space
	:param wavelet: any common, named wavelet, including
			'Haar' (default)
			'Daubechies'
			'Symlet'
			'Coiflet'
			'Biorthogonal'
			'ReverseBiorthogonal'
			'DiscreteMeyer'
			'Gaussian'
			'MexicanHat'
			'Morlet'
			'ComplexGaussian'
			'Shannon'
			'FrequencyBSpline'
			'ComplexMorlet'
		or a custom [ [lowpass_decomposition],
			[highpass_decomposition],
			[lowpass_reconstruction],
			[highpass_reconstruction] ]
		where each is a pair of floating point values
	:param mode: str or 2-tuple of str, optional
		Signal extension mode, see Modes (default: "symmetric"). This can also be a tuple containing a mode to apply along each axis in axes.
	:param level: int, optional
		Decomposition level (must be >= 0). If level is None (default) then it will be calculated using the dwt_max_level function.

	See also:
		https://pywavelets.readthedocs.io/en/latest/ref/index.html
	"""
	if mode is None:
		mode='symmetric'
	img=numpyArray(img)
	colorMode=imageMode(img)
	if len(colorMode)==1:
		return pywt.wavedec2(img,_wavelet(wavelet),mode,level)
	ret=[]
	for ch in range(len(colorMode)):
		ret.append(np.array(pywt.wavedec2(img[:,:,ch],_wavelet(wavelet),mode,level)))
	ret=np.dstack(ret)
	return ret


def fromWavelet(wavImg,wavelet='haar',mode='symmetric'):
	"""
	:param wavImg: a wavelet image to transform back into image space
	:param wavelet: any common, named wavelet, including
			'Haar' (default)
			'Daubechies'
			'Symlet'
			'Coiflet'
			'Biorthogonal'
			'ReverseBiorthogonal'
			'DiscreteMeyer'
			'Gaussian'
			'MexicanHat'
			'Morlet'
			'ComplexGaussian'
			'Shannon'
			'FrequencyBSpline'
			'ComplexMorlet'
		or a custom [ [lowpass_decomposition],
			[highpass_decomposition],
			[lowpass_reconstruction],
			[highpass_reconstruction] ]
		where each is a pair of floating point values
	:param mode: str or 2-tuple of str, optional
		Signal extension mode, see Modes (default: �symmetric�). This can also be a tuple containing a mode to apply along each axis in axes.

	See also:
		https://pywavelets.readthedocs.io/en/latest/ref/index.html
	"""
	return pywt.waverec2(wavImg,_wavelet(wavelet),mode)


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
		lastFilename=None
		img=None
		for arg in sys.argv[1:]:
			if arg.startswith('-'):
				arg=[a.strip() for a in arg.split('=',1)]
				if arg[0] in ['-h','--help']:
					printhelp=True
				elif arg[0]=='--toWavelet':
					if len(arg)>1:
						img=toWavelet(img,arg[1])
					else:
						img=toWavelet(img)
				elif arg[0]=='--fromWavelet':
					if len(arg)>1:
						img=fromWavelet(img,arg[1])
					else:
						img=fromWavelet(img)
				elif arg[0]=='--show':
					preview(img)
				elif arg[0]=='--save':
					if len(arg)>1:
						lastFilename=arg[1]
					pilImage(img).save(lastFilename)
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				lastFilename=arg
				img=arg
	if printhelp:
		print 'Usage:'
		print '  numberSpaces.py img.jpg [options]'
		print 'Options:'
		print '   --toWavelet[=wavelet] ....... where value can be things like haar or mortlet'
		print '   --fromWavelet[=wavelet] ..... where value can be things like haar or mortlet'
		print '   --show ...................... show the image'
		print '   --save[=filename] ........... save the image (default is to save over the last filename)'