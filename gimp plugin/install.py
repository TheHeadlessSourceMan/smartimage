#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This program installs the gimp extension
"""
import os,shutil,subprocess,stat


def install():
	LOCATIONS=[r'C:\Program Files\GIMP 2\lib\gimp\2.0\plug-ins',r'C:\Program Files (x86)\GIMP 2\lib\gimp\2.0\plug-ins']
	HERE=os.path.abspath(__file__).rsplit(os.sep,1)[0]+os.sep
	installed=False
	for loc in LOCATIONS:
		print(os.path.exists(loc),loc)
		if os.path.exists(loc):
			originalMode=os.stat(loc).st_mode
			os.chmod(loc,0o777)   
			for filename in os.listdir(HERE):
				if filename.endswith('.py') and filename!='install.py':
					print('copying "'+HERE+filename+'" to "'+loc+'"')
					shutil.copyfile(HERE+filename,loc)
					filename=loc+filename
					run=False
					for line in open(filename,'r'):
						if line.startswith('main'):
							run=True
					if run:
						out,_=subprocess.popen('python "'+filename+'"',stdout=subprocess.PIPE,stderr=subprocess.STDOUT).communicate()
						print(err.strip())
			os.chmod(loc,originalMode)   
			installed=True
	return installed
	

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
		pass#printhelp=True
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
		print('  install.py [options]')
		print('Options:')
		print('   NONE')
	else:
		if not install():
			print("ERR: No gimp installation found!")