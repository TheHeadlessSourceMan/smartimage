#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This allows color correction (curves, levels, etc) of PIL images
"""
from PIL import Image
import numpy as np


class Curves(object):
	def __init__(self,points=None):
		"""
		:param points: percentage floats from 0..1 in the form [(cIn,cOut)] or [(cIn,cOut,cubic)]
		"""
		self._points=[[],[],[],[]] # in the form [[(rIn,rOut)],[(gIn,gOut)],[(bIn,bOut)],[(aIn,aOut)]]
		self.addPoints(points)
		
	def addPoints(self,points,channel='RGB'):
		"""
		:param points: percentage floats from 0..1 in the form [(cIn,cOut)] or [(cIn,cOut,cubic)]
		:prarm channel: can be 'R','G','B','RGB',or 'A'
		"""
		channel=channel.upper()
		if points==None:
			return
		if type(points)!=list:
			points=(points)
		for point in points:
			if channel=='RGB':
				self._points[0].append(point)
				self._points[1].append(point)
				self._points[2].append(point)
			elif channel=='R':
				self._points[0].append(point)
			elif channel=='G':
				self._points[1].append(point)
			elif channel=='B':
				self._points[2].append(point)
			elif channel=='A':
				self._points[3].append(point)
		for chan in self._points:
			chan.sort()
		
	def asExpression(self,arrayName='npImg'):
		"""
		convert these points to a numpy expression
		"""
		exprs=[]
		for i in range(len(self._points)):
			chan=self._points[i]
			last=(0,0)
			expr='@'
			for point in chan:
				if last[0]!=point[0] and last[1]!=point[1]:
					var=var='channels['+str(i)+']'
					var='channels['+str(i)+':'+str(last[0])+'>'+var+'&'+var+'>'+str(point[0])+']'
					a=str(last[1])
					b=str(point[1]/last[1]+last[1])
					if len(point)>2: # cubic curve
						c=str(point[2])
						currentCurve=a+'+'+b+'*'+var+'+'+c+'*np.pow('+var+',2)'
					else: # linear curve
						currentCurve=a+'+'+b+'*'+var
					expr=var
					#expr=expr.replace('@','np.where('+str(last[0])+'>'+var+'>'+str(point[0])+','+currentCurve+',@)')
				last=point
			expr=expr.replace('@','1.0')
			exprs.append(expr)
		ret='('+(','.join(exprs))+')'
		return ret
				
	def applyTo(self,image):
		exp=self.asExpression()
		print 'Applying:\n\t',exp
		if exp==None:
			final=image.copy()
		else:
			npImg=np.asarray(image)/255.0
			channels=npImg[:,:,:]
			npImg=eval(exp)
			npImg=np.clip(npImg*255.0,0.0,255.0)
			npImg=dstack(npImg)
			npImg=Image.fromarray(npImg.astype('uint8'),image.mode)
		return npImg

		
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
		import json,time
		curves=Curves()
		currentChannel='RGB'
		image=None
		for arg in sys.argv[1:]:
			if arg.startswith('-'):
				arg=[a.strip() for a in arg.split('=',1)]
				if arg[0] in ['-h','--help']:
					printhelp=True
				elif arg[0]=='--channel':
					currentChannel=arg[1]
				elif arg[0]=='--addPoints':
					points=json.loads(arg[1])
					curves.addPoints(points,currentChannel)
				elif arg[0]=='--show':
					out=curves.applyTo(image)
					out.show()
					time.sleep(1.0)
				elif arg[0]=='--save':
					out=curves.applyTo(image)
					out.save(arg[1])
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				image=Image.open(arg)
	if printhelp:
		print 'Usage:'
		print '  colorCorrect.py input.jpg [options]'
		print 'Options:'
		print "   --channel= .................. 'R','G','B','RGB',or 'A'"
		print '   --addPoints= ................ percentage floats from 0..1 in the form [(cIn,cOut)] or [(cIn,cOut,cubic)]'
		print '   --show ...................... display the output image'
		print '   --save=filename ............. save the output image'