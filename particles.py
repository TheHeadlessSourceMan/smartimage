#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This is a particles type layer
"""
import random
from layer import *


class Particles(Layer):
	"""
	This is a particles type layer
	"""

	def __init__(self,docRoot,parent,xml):
		Layer.__init__(self,docRoot,parent,xml)

	@property
	def randomize(self):
		"""
		randomize the particle locations
		"""
		randies={}
		for r in self._getProperty('randomize','').split(','):
			r=[kv.strip() for kv in r.split('=',1)]
			if r[1].find('|')>=0:
				r[1]=r[1].split('|')
			randies[r[0]]=r[1]
		return randies

	@property
	def dispersionMap(self):
		"""
		an image to define where particles can land
		"""
		self._getImageProperty('dispersionMap')

	@property
	def qty(self):
		"""
		how many particles to create
		"""
		return int(self._getProperty('qty','1'))

	def nextRandomSet(self):
		"""
		Returns the next set of randomize values
		"""
		values={}
		for k,v in self.randomize.items():
			if isinstance(v,list):
				v=random.choice(v)
			v=v.split('..',1)
			if v:
				v=uniform(float(v[0]),v[1])
			values[k]=v
		return values

	@property
	def image(self):
		for i in range(self.qty):
			variables=self.nextRandomSet()
			child=random.choice(self.children)
			# TODO: Need to re-set the local variables and draw each child layer
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
		print '  particles.py [options]'
		print 'Options:'
		print '   NONE'
