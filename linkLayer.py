#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This is a layer that links to another layer
"""
from layer import *


class Link(Layer):
	"""
	This is a layer that links to another layer
	"""

	def __init__(self,docRoot,parent,xml):
		Layer.__init__(self,docRoot,parent,xml)
		self._target=None

	@property
	def ref(self):
		return self.xml.attrib['ref']
	@ref.setter
	def ref(self,ref):
		self.xml.attrib['ref']=ref
		self.docRoot.dirty=True

	def _getProperty(self,name,default=None):
		if name in self.xml.attrib:
			val=self.xml.attrib[name]
		else:
			val=self.target._getProperty(name,default)
		return val

	@property
	def target(self):
		if self._target==None:
			self._target=self.parent.getLayer(self.ref)
			if self._target==None:
				raise Exception('ERR: broken link to layer '+str(self.ref))
		return self._target

	@property
	def image(self):
		img=self.target.image
		w=self._getProperty('w','auto')
		h=self._getProperty('h','auto')
		if (w not in ['0','auto']) and (h not in ['0','auto']):
			if w in ['0','auto']:
				w=img.width*(img.height/h)
			elif h in ['0','auto']:
				h=img.height*(img.width/w)
			img=img.resize((int(w),int(h)),Image.ANTIALIAS)
		img.immutable=True # mark this image so that compositor will not alter it
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