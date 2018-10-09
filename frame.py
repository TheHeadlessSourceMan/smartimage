#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This is a layer that represents a single frame in an animation or presentation
"""
from layer import *


class Frame(Layer):
	"""
	This is a layer that represents a single frame in an animation or presentation
	"""

	def __init__(self,docRoot,parent,xml):
		Layer.__init__(self,docRoot,parent,xml)

	@property
	def time(self):
		"""
		the time delay of this frame before advancing to the next one
		"""
		return self._getFloat('time',0.25)

	@property
	def wait(self):
		"""
		wait for user input to advance to the next frame
		"""
		return self._getBool('wait',False)


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