#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
A layer representing a smartimage extension
"""
from image import *


class ExtensionLayer(ImageLayer):
	"""
	A layer representing a smartimage extension
	"""

	def __init__(self,docRoot,parent,xml):
		ImageLayer.__init__(self,docRoot,parent,xml)

	@property
	def type(self):
		"""
		the type for the extension
		"""
		return self._getProperty('type')

	@property
	def extensionClass(self):
		"""
		get the external extension class or None
		"""
		extPkgName=self.type.replace('.','_')
		try:
			exec('import extensions.'+extPkgName)
			return eval('extensions.'+extPkgName+'Extension')
		except ImportError:
			pass

	@property
	def image(self):
		"""
		get the layer's image
		"""
		extensionClass=self.extensionClass
		if extensionClass is None:
			image=ImageLayer.image
		else:
			ext=extensionClass(self.docRoot,self,self.xml)
			image=ext.image
			self.docRoot.saveImage(image,self.file)
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
		print '  modifier.py [options]'
		print 'Options:'
		print '   NONE'
