#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
A layer that contains an image
"""
from layer import *
from imgTools import *


class ImageLayer(Layer):
	"""
	A layer that contains an image
	"""

	def __init__(self,docRoot,parent,xml):
		Layer.__init__(self,docRoot,parent,xml)

	@property
	def roi(self):
		"""
		the region of interest of a graphical image

		if there is none, figure it out
		"""
		ref=self._getProperty('roi')
		if ref!=None:
			img=self.docRoot.imageByRef(ref)
		else:
			img=interest(self.image)
		if img.size!=self.image.size:
			img.resize(self.image.size)
		return img

	@property
	def image(self):
		ref=self._getProperty('file')
		img=self.docRoot.imageByRef(ref)
		w=self._getProperty('w','auto')
		h=self._getProperty('h','auto')
		if (w not in ['0','auto']) and (h not in ['0','auto']):
			if w in ['0','auto']:
				w=img.width*(img.height/h)
			elif h in ['0','auto']:
				h=img.height*(img.width/w)
			img=img.resize((int(w),int(h)),Image.ANTIALIAS)
		if img!=None:
			img.immutable=True # mark this image so that compositor will not alter it
		return img

	@property
	def w(self):
		w=self._getProperty('w','auto')
		if w in ['0','auto']:
			w=self.image.size[0]
		else:
			w=float(w)
		return w
	@property
	def h(self):
		h=self._getProperty('h','auto')
		if h in ['0','auto']:
			h=self.image.size[1]
		else:
			h=float(h)
		return h


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
		print '  modifier.py [options]'
		print 'Options:'
		print '   NONE'