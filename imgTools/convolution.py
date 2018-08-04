#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Contains routines to convolve an image
"""
from imageRepr import *


CONVOLVE_MATTRICES={
	'emboss':[[-2,-1, 0],
	          [-1, 1, 1],
	          [ 0, 1, 2]],
	'edgeDetect':[[ 0, 1, 0],
	              [ 1,-4, 1],
	              [ 0, 1, 0]],
	'edgeEnhance':[[ 0, 0, 0],
	               [-1, 1, 0],
	               [ 0, 0, 0]],
	'blur':[[ 0, 0, 0, 0, 0],
	        [ 0, 1, 1, 1, 0],
	        [ 0, 1, 1, 1, 0],
	        [ 0, 1, 1, 1, 0],
	        [ 0, 0, 0, 0, 0]],
	'sharpen':[[ 0, 0, 0, 0, 0],
	           [ 0, 0,-1, 0, 0],
	           [ 0,-1, 5,-1, 0],
	           [ 0, 0,-1, 0, 0],
	           [ 0, 0, 0, 0, 0]],
}


def directionalBlur(img,size=15):
	oSize=img.shape
	kernel= np.zeros((size,size))
	kernel[int((size-1)/2), :] = np.ones(size)
	kernel= kernel / size
	img=scipy.signal.convolve(img,kernel)
	d=(img.shape[0]-oSize[0])/2,(img.shape[1]-oSize[1])/2
	img=img[d[0]:-d[0],d[1]:-d[1]]
	return img
	

def circularBlur(img):
	"""
	blur in a radial manner
	
	http://chemaguerra.com/circular-radial-blur/
	"""
	pass
	
def zoomBlur(img):
	"""
	blur in a zoom manner
	
	http://chemaguerra.com/circular-radial-blur/
	"""
	pass	

def streak(img,size=15):
	return img+directionalBlur(highlights(img,.95),size)
	
	
def convolve(img,matrix,add,divide,edge):
	size=len(matrix)
	border=size/2-1
	img=imageBorder(img,border,edge)
	k=ImageFilter.Kernel((size,size),matrix,scale=divide,offset=add)
	img=img.filter(k)

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
		print '  convolution.py [options]'
		print 'Options:'
		print '   NONE'