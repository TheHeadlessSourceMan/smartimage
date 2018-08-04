#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Defines color gradients and gives the ability to apply them.
"""

GRADIENT_BLACK_TO_WHITE=[(0.0,(0.0,0.0,0.0)),(1.0,(1.0,1.0,1.0))]
GRADIENT_CLEAR_TO_WHITE=[(0.0,(1.0,1.0,1.0,0.0)),(1.0,(1.0,1.0,1.0,1.0))]
GRADIENT_CLEAR_TO_BLACK=[(0.0,(0.0,0.0,0.0,0.0)),(1.0,(0.0,0.0,0.0,1.0))]
GRADIENT_RAINBOW=[(0.0,(1.0,0.0,0.0)),(0.2,(1.0,0.75,0.0)),(0.4,(1.0,1.0,0.0)),(0.6,(0.0,1.0,0.0)),(0.8,(0.0,0.0,1.0)),(1.0,(0.8,0.0,1.0))]


def colormap(img,colors=None):
	"""
	apply the colors to a grayscale image
	if a color image is provided, convert it (thus, acts like a "colorize" function)
	
	:param img:  a grayscale image
	:param colors:  [(decimalPercent,color),(...)] 
		if no colors are given, then [(0.0,black),(1.0,white)]
		if a single color and no percent is given, assume [(0.0,black),(0.5,theColor),(1.0,white)]
	
	:return: the resulting image
	"""
	img=grayscale(img)
	if not isFloat(img):
		img=img/255.0
	if type(colors)==type(None):
		colors=[(0.0,(0.0,0.0,0.0)),(1.0,(1.0,1.0,1.0))]
	elif type(colors[0]) not in [tuple,list,np.ndarray]:
		white=[]
		black=[]
		if type(colors) in [str,unicode]:
			colors=strToColor(colors)
		if isFloat(colors):
			imax=1.0
			imin=0.0
		else:
			imax=255
			imin=0
		for i in range(len(colors)):
			white.append(imax)
			black.append(imin)
		if len(colors) in [2,4]: # keep same alpha value
			black[-1]=colors[-1]
			white[-1]=white[-1]
		colors=[(0.0,black),(0.5,colors),(1.0,white)]
	else:
		colors.sort() # make sure we go from low to high
	# make sure colors are in the shape we need
	colors=[[matchColorToImage(color[0],img),np.array(strToColor(color[1]))] for color in colors]
	shape=(img.shape[0],img.shape[1],len(color[1]))
	img2=np.ndarray(shape)
	img=img[...,None]
	if True:
		lastColor=None
		for color in colors:
			if lastColor==None:
				img2+=color[1]
			else:
				percent=(img-lastColor[0])*lastColor[0]/color[0]
				img2=np.where(np.logical_and(img>lastColor[0],img<=color[0]),(color[1]*percent)+(lastColor[1]*(1-percent)),img2)
			lastColor=color
		img2=np.where(img>lastColor[0],lastColor[1],img2)
	else:
		def gradMap(c):
			lastColor=None
			for color in colors:
				if c<color[0]:
					if lastColor==None:
						return color[1]
					else:
						percent=(c-lastColor[0])/color[0]
						return (lastColor[1]*percent+color[1])/(2*percent)
				lastColor=color
			return lastColor[1]
		img2=perPixel(gradMap,img,clamp=False)
	return img2


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
		print '  gradients.py [options]'
		print 'Options:'
		print '   NONE'