#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This is a layer for creating repeating patterns
"""
from layer import *
from proceduralTextures import *


class Pattern(Layer):
	"""
	This is a layer for creating repeating patterns
	"""

	def __init__(self,docRoot,parent,xml):
		Layer.__init__(self,docRoot,parent,xml)

	@property
	def mortarThickness(self):
		"""
		how thick the mortar is
		"""
		return self._getProperty('mortarThickness','0')

	@property
	def repeat(self):
		"""
		an “x,y” value that can be:
			“once” - show only once (same as “top” or “left”)
			“all” - [default] repeat all the way across
			“stretch” - display once stretched to the maximum size
			“center” or “middle” - display once centererd in the size
			“top”,”left”,”right”, or “bottom” - display once at that particular edge
			“maintainAspect” - keep the same aspect ratio based on whatever the opposite value is
			“maximize”-a lone value, maximizes pattern just large enough that all screen is covered
			“minimize”- a lone value, makes the
			“bricks” - tessalate in a brick wall pattern
			“isometric“ - tessalate on an isometric triangle grid (for instance, like a honeycomb pattern)
		
		always returns [repeatX,repeatY]
		"""
		repeat=self._getProperty('repeat','all')
		repeat=repeat.replace(' ','').split(',',1)
		if len(repeat)<2:
			repeat.append(repeat[0])
		return repeat

	@property
	def image(self):
		raise NotImplementedError()


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
		print '  patternLayer.py [options]'
		print 'Options:'
		print '   NONE'