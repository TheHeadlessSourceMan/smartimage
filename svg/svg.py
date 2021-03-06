#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Open and display SVG files (in PIL)
"""


class Svg(object):
	"""
	Open and display SVG files (in PIL)
	"""
	
	def __init__(self):
		pass


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
					print('ERR: unknown argument "'+arg[0]+'"')
			else:
				print('ERR: unknown argument "'+arg+'"')
	if printhelp:
		print('Usage:')
		print('  svg.py [options]')
		print('Options:')
		print('   NONE')