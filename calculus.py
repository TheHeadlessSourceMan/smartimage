#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Tools for performing operations in derivative-land (gradients)

https://en.wikipedia.org/wiki/Gradient-domain_image_processing

For possible uses, see:
	https://www.youtube.com/watch?v=70aLm2zv2ao
		Explaination of above: https://www.cv-foundation.org/openaccess/content_cvpr_2016/papers/Shibata_Gradient-Domain_Image_Reconstruction_CVPR_2016_paper.pdf
	http://www.ok.sc.e.titech.ac.jp/res/res.shtml
Or search for:
	"gradient-domain image processing"
	
"""
import numpy as np
from helper_routines import *


def gradient(img):
	"""
	get the derivitive/gradient from the image
		
	Alternative implementations:
		http://grail.cs.washington.edu/projects/gradientshop/
	"""
	return np.gradient(numpyArray(img))
	
def inverseGradient(g):
	"""
	return a gradient back into an image by solving poisson's equation
	
	Implementations:
		I really need to use this! https://github.com/daleroberts/poisson/blob/master/poisson.py
	"""
	pass
	
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
	pass
	
def gradientPaste(overImage,pastedImage,location):
	"""
	Combine images using gradients for a more seamless fit.
	
	Examples:
		http://www.connellybarnes.com/work/class/2013/cs6501/proj2/
		https://en.wikipedia.org/wiki/Gradient-domain_image_processing
	"""
	
def kuwahara(img):
	"""
	apply a Kuwahara filter to the image to simplify it
	
	this is excellent for optimization, scaling, and painterly effects
	
	for lots of sexy pics, check out this slideshow:
		https://www.slideshare.net/chiaminhsu/study-image-and-video-abstraction-by-multi-scale-anisotropic-kuwahara
	"""
	pass



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
		print '  calculus.py [options]'
		print 'Options:'
		print '   NONE'