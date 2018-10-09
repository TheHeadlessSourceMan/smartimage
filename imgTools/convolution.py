#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Contains routines to convolve an image
"""
try:
	# first try to use bohrium, since it could help us accelerate
	# https://bohrium.readthedocs.io/users/python/
	import bohrium as np
except ImportError:
	# if not, plain old numpy is good enough
	import numpy as np
import scipy
from scipy import ndimage
from imageRepr import *
from resizing import *


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
	'xblur':[[0,0,0],
			 [1,1,1],
			 [0,0,0]],
	'yblur':[[0,1,0],
			 [0,1,0],
			 [0,1,0]],
}


def directionalBlur(img,size=15):
	"""
	blur in a given direction

	https://www.packtpub.com/mapt/book/application_development/9781785283932/2/ch02lvl1sec21/motion-blur#!
	"""
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
	import numberSpaces
	polar=numberSpaces.cartesian2polar(img)
	polar=convolve(polar,'xblur')
	return numberSpaces.polar2cartesian(polar)


def zoomBlur(img):
	"""
	blur in a zoom manner

	http://chemaguerra.com/circular-radial-blur/
	"""
	import numberSpaces
	polar=numberSpaces.cartesian2polar(img)
	polar=convolve(polar,'yblur')
	return numberSpaces.polar2cartesian(polar)


def streak(img,size=15):
	"""
	The idea is to cause streaks in a given direction.

	TODO: not working
	"""
	return img+directionalBlur(highlights(img,.95),size)


def convolve(img,matrix,add=0,divide=1,edge='clamp'):
	"""
	run a given convolution matrix

	:param matrix: can be a numerical matrix or an entry in CONVOLVE_MATTRICES
	"""
	if isinstance(matrix,basestring):
		if matrix.find(',')>0:
			matrix=''.join(matrix.split())
			if matrix.startswith('[['):
				matrix=matrix[1:-1]
			matrix=[[float(col) for col in row.split(',')] for row in matrix[1:-1].replace('],','').split('[')]
		else:
			matrix=CONVOLVE_MATTRICES[matrix]
	size=len(matrix)
	border=size/2-1
	#img=imageBorder(img,border,edge)
	#k=ImageFilter.Kernel((size,size),matrix,scale=divide,offset=add)
	#img=img.filter(k)
	img=numpyArray(img)
	if len(img.shape)>2:
		ret=[]
		for ch in range(img.shape[2]):
			ret.append(ndimage.convolve(img[:,:,ch],matrix))
		img=np.dstack(ret)
	else:
		img=ndimage.convolve(img,matrix)
	return img


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
		img=None
		for arg in sys.argv[1:]:
			if arg.startswith('-'):
				arg=[a.strip() for a in arg.split('=',1)]
				if arg[0] in ['-h','--help']:
					printhelp=True
				elif arg[0]=='--save':
					pilImage(img).save(arg[1])
				elif arg[0]=='--show':
					pilImage(img).show()
				elif  arg[0]=='--convolve':
					img=convolve(img,arg[1])
				elif  arg[0]=='--circularBlur':
					img=circularBlur(img)
				elif  arg[0]=='--zoomBlur':
					img=zoomBlur(img)
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				img=arg
	if printhelp:
		print 'Usage:'
		print '  convolution.py image.jpg [options]'
		print 'Options:'
		print '   --convolve=matrix ......... matrix can be a name or a matrix of numbers'
		print '   --circularBlur=amount ..... blur around circular center point'
		print '   --zoomBlur=amount ......... blur outward from a circular center point'
		print '   --save=filename ....... save the current image'
		print '   --show ................ show the current image'
