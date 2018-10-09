#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This is a number space conversion layer
"""
from layer import *


class NumberSpace(Layer):
	"""
	This is a number space conversion layer
	"""

	def __init__(self,docRoot,parent,xml):
		Layer.__init__(self,docRoot,parent,xml)

	@property
	def space(self):
		"""
		nunberspace to transform to/from
		"""
		return self._getProperty('space')

	@property
	def levels(self):
		"""
		the levels to use (if necessary for a given transformation)
		"""
		return self._getProperty('levels')

	@property
	def mode(self):
		"""
		the mode to use (if necessary for a given transformation)
		"""
		return self._getProperty('mode')

	@property
	def invert(self):
		"""
		perform the reverse transformation to get back to the original
		"""
		return self._getPropertyBool('invert')

	def _transform(self,img):
		"""
		transform the image into this numberspace
		"""
		space=self.space
		if space=='polar':
			if self.invert:
				ret=polar2cartesian(img)
			else:
				ret=cartesian2polar(img)
		elif space=='logpolar':
			if self.invert:
				ret=logpolar2cartesian(img)
			else:
				ret=cartesian2logpolar(img)
		elif space=='fft' or space=='fourier':
			if self.invert:
				ret=fromFrequency(img)
			else:
				ret=toFrequency(img)
		elif space=='gradient':
			if self.invert:
				ret=inverseGradient(img)
			else:
				ret=gradient(img)
		elif space=='laplace':
			if self.invert:
				ret=fromLaplacePyramid(img)
			else:
				ret=toLaplacePyramid(img)
		elif space=='dct':
			if self.invert:
				ret=fromCosine(img)
			else:
				ret=toCosine(img)
		elif space=='dst':
			if self.invert:
				ret=fromSine(img)
			else:
				ret=toSine(img)
		else:
			if self.invert:
				ret=fromWavelet(img,space,mode=self.mode)
			else:
				ret=toWavelet(img,space,mode=self.mode,level=None)
		return ret

	def renderImage(self,renderContext=None):
		"""
		WARNING: Do not modify the image without doing a .copy() first!
		"""
		opacity=self.opacity
		if opacity<=0.0 or not self.visible:
			return None
		image=self._transform(Layer.renderImage(self,renderContext).copy())
		if self.opacity<1.0:
			setOpacity(image,opacity)
		return image


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
		print '  numberspace.py [options]'
		print 'Options:'
		print '   NONE'
