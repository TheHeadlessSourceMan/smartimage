#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This program is a test extension for debugging the extension mechanism.
"""
import lxml.etree

class Extension(object):
	"""
	This program is a test extension for debugging the extension mechanism.
	"""
	
	def __init__(self,smartimageObject,parentObject,xml):
		self.smartimageObject=smartimageObject
		self.parentObject=parentObject
		self.xml=xml
		
	@property
	def image(self):
		print self.__file__
		print '='*len(self.__file__)
		print lxml.etree.toString(xml)
		return None


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
		print '  com.smartimage.testExtension.py [options]'
		print 'Options:'
		print '   NONE'