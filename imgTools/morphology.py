#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Contains mathematical morphology routines (dilate, erode, etc)
"""
from imageRepr import *

	
def erode(img):
	a=np.asarray(img)
	def _erode(p):
		print p
		p[1,1]=1
		return p
	applyFunctionToPatch(_erode,a,(3,3))
	return Image.fromarray(a.astype('uint8'),img.mode)
	

def dilate(img,size=3):
	"""
	implement image dilation
	
	TODO: does not belong in this file!
	"""
	return scipy.ndimage.grey_dilation(img,size=(size,size))

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
		print '  morphology.py [options]'
		print 'Options:'
		print '   NONE'