#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Run unit tests

See:
	http://pyunit.sourceforge.net/pyunit.html
"""
import unittest
import os,sys


TESTS=[
	'solid',
	'simple_rice',
	'text',
	'references',
	'link',
	'link_image_size',
	'mask_rice',
	'modifier_rice',
	'procedural_textures',
	'psychadellicGimpColors',
	'smartresize_picnic',
	'smartresize_rice',
	'template_picnic',
	'text_picnic',
	'rotation_whammy',
	'variable_context',
	'heartGimpPath',
	'collage',
]
		
		
__HERE__=os.path.abspath(__file__).rsplit(os.sep,1)[0]
def suite(tests=None):
	"""
	Combine unit tests into an entire suite
	"""
	if tests==None or len(tests)==0:
		tests=TESTS
	testSuite = unittest.TestSuite()
	for dirname in TESTS:#os.listdir(__HERE__):
		if os.path.isdir(dirname):
			fullDirname=__HERE__+os.sep+dirname
			if os.path.exists(fullDirname+os.sep+'test.py'):
				print 'Queueing test: '+dirname
				exec('import '+dirname)
				exec('testSuite.addTest('+dirname+'.testSuite())')
	return testSuite
		
		
def run(tests=None,output=None,verbosity=2,failfast=False):
	if output==None:
		output=sys.stdout
	else:
		output=open(output,'wb')
	runner=unittest.TextTestRunner(output,verbosity=verbosity,failfast=failfast)
	runner.run(suite(tests))
		
		
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
	save=None
	tests=[]
	if len(sys.argv)<2:
		pass#printhelp=True
	else:
		for arg in sys.argv[1:]:
			if arg.startswith('-'):
				arg=[a.strip() for a in arg.split('=',1)]
				if arg[0] in ['-h','--help']:
					printhelp=True
				elif arg[0]=='--save':
					save=arg[1]
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				tests.append(arg)
	if printhelp:
		print 'Usage:'
		print '  test.py [options] [tests]'
		print 'Options:'
		print '   --save=filename ............... save the test output to this file, rather than the console'
	else:
		run(tests,save)