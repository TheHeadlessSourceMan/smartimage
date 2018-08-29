#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This is a layer of a solid color (same nomenclature as Adobe AfterEffects)
"""
from layer import *
from imgTools import *
import struct


class Solid(Layer):
	"""
	This is a layer of a solid color (same nomenclature as Adobe AfterEffects)
	"""

	def __init__(self,docRoot,parent,xml):
		Layer.__init__(self,docRoot,parent,xml)

	@property
	def color(self):
		return self._getProperty('color','#ff00ff')

	@property
	def rgba(self):
		"""
		always returns an rgba[], regardless of color being:
			#FFFFFF
			#FFFFFFFF
			rgb(128,12,23)
			rgba(234,33,23,0)
			
		If self.color is not specified, return [255,255,255,0]
		"""
		return strToColor(self.color,False,[255,255,255,0])

	@property
	def image(self):
		return Image.new('RGBA',(int(self.w),int(self.h)),tuple(self.rgba))


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
		print '  solid.py [options]'
		print 'Options:'
		print '   NONE'