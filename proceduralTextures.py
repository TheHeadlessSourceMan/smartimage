#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This allows for the creation of procedural textures
"""
from helper_routines import *
from PIL import Image,ImageDraw
import scipy.ndimage
import numpy as np


def perlinNoiseX(x,y,seed=0):
	"""
	Generate a black and white image consisting of perlinNoise (clouds)
	"""
	def lerp(a,b,x):
		"linear interpolation"
		return a + x * (b-a)
	def fade(t):
		"6t^5 - 15t^4 + 10t^3"
		return 6 * t**5 - 15 * t**4 + 10 * t**3
	def gradient(h,x,y):
		"grad converts h to the right gradient vector and return the dot product with (x,y)"
		vectors = np.array([[0,1],[0,-1],[1,0],[-1,0]])
		g = vectors[h%4]
		return g[:,:,0] * x + g[:,:,1] * y
	# permutation table
	np.random.seed(seed)
	p = np.arange(256,dtype=int)
	np.random.shuffle(p)
	p = np.stack([p,p]).flatten()
	# coordinates of the top-left
	xi = x.astype(int)
	yi = y.astype(int)
	# internal coordinates
	xf = x - xi
	yf = y - yi
	# fade factors
	u = fade(xf)
	v = fade(yf)
	# noise components
	n00 = gradient(p[p[xi]+yi],xf,yf)
	n01 = gradient(p[p[xi]+yi+1],xf,yf-1)
	n11 = gradient(p[p[xi+1]+yi+1],xf-1,yf-1)
	n10 = gradient(p[p[xi+1]+yi],xf-1,yf)
	# combine noises
	x1 = lerp(n00,n10,u)
	x2 = lerp(n01,n11,u)
	return lerp(x1,x2,v)
def callPerlinX():
	lin = np.linspace(0,5,256,endpoint=False)
	x,y = np.meshgrid(lin,lin)
	print x
	img=perlinNoise(x,y,seed=2)
	
	
def randomNoise(imgx,imgy):
	return np.random.rand(imgx,imgy)
	
def perlinNoiseY(imgx,imgy):
	import math,random
	image = Image.new("RGB", (imgx, imgy))
	draw = ImageDraw.Draw(image)
	pixels = image.load()
	octaves = int(math.log(max(imgx, imgy), 2.0))
	persistence = random.random()
	imgAr = [[0.0 for i in range(imgx)] for j in range(imgy)] # image array
	totAmp = 0.0
	for k in range(octaves):
		freq = 2 ** k
		amp = persistence ** k
		totAmp += amp
		# create an image from n by m grid of random numbers (w/ amplitude)
		# using Bilinear Interpolation
		n = freq + 1; m = freq + 1 # grid size
		ar = [[random.random() * amp for i in range(n)] for j in range(m)]
		nx = imgx / (n - 1.0); ny = imgy / (m - 1.0)
		for ky in range(imgy):
			for kx in range(imgx):
				i = int(kx / nx); j = int(ky / ny)
				dx0 = kx - i * nx; dx1 = nx - dx0
				dy0 = ky - j * ny; dy1 = ny - dy0
				z = ar[j][i] * dx1 * dy1
				z += ar[j][i + 1] * dx0 * dy1
				z += ar[j + 1][i] * dx1 * dy0
				z += ar[j + 1][i + 1] * dx0 * dy0
				z /= nx * ny
				imgAr[ky][kx] += z # add image layers together

	# paint image
	for ky in range(imgy):
		for kx in range(imgx):
			c = int(imgAr[ky][kx] / totAmp * 255)
			pixels[kx, ky] = (c, c, c)
	return image
	
def perlinNoise(w,h,octaves=None):
	import math
	if octaves==None:
		octaves=math.log(max(w,h), 2.0)
	ret=np.zeros((w,h))
	for n in range(1,octaves):
		k=n
		amp=1.0#/octaves/float(n)
		px=randomNoise(w/k,h/k)
		px=scipy.ndimage.zoom(px,(float(ret.shape[0])/px.shape[0],float(ret.shape[1])/px.shape[1]),order=2)
		px=np.clip(px,0.0,1.0) # unfortunately zoom function can cause values to go out of bounds :(
		ret=(ret+px*amp)/2.0 # average with existing
	ret=np.clip(ret,0.0,1.0)
	return ret
	
# TODO: don't know where to put this, but it looks important
#def f(points):
#		return np.sin(ret.index/w)
#ret=scipy.ndimage.generic_filter(ret,f,size=None,footprint=(1),output=None,mode='reflect',cval=0.0, origin=0, extra_arguments=(), extra_keywords=None)
	
	
def _sinwave(theta):
	0.5+0.5*math.sin(theta)
def _triwave(theta):
	b = 2*math.pi
	n = int(a / b)
	a -= n*b
	if a<0:
		a+=b
	return a/b
	
def cartesian2Polar(img,order=1):
	"""
	Transform img to its polar coordinate representation.

	order: int, default 1
		Specify the spline interpolation order. 
		High orders may be slow for large images.
	"""
	# max_radius is the length of the diagonal 
	# from a corner to the mid-point of img.
	max_radius = 0.5*np.linalg.norm( img.shape )

	def transform(coords):
		# Put coord[1] in the interval, [-pi, pi]
		theta = 2*np.pi*coords[1] / (img.shape[1] - 1.)

		# Then map it to the interval [0, max_radius].
		#radius = float(img.shape[0]-coords[0]) / img.shape[0] * max_radius
		radius = max_radius * coords[0] / img.shape[0]

		i = 0.5*img.shape[0] - radius*np.sin(theta)
		j = radius*np.cos(theta) + 0.5*img.shape[1]
		return i,j

	polar = scipy.ndimage.interpolation.geometric_transform(img, transform, order=order)

	rads = max_radius * np.linspace(0,1,img.shape[0])
	angs = np.linspace(0, 2*np.pi, img.shape[1])

	return polar, (rads, angs)
	
def waveImage(w,h,repeats=2,angle=0,wave='sine',radial=False):
	import math
	ret=np.zeros((h,w))
	if radial:
		raise NotImplementedError() # TODO
	else:
		twopi=2*math.pi
		thetas=np.arange(w)*float(repeats)/w*twopi
		if wave=='sine':
			ret[:,:]=0.5+0.5*np.sin(thetas)
		elif wave=='saw':
			n=np.round(thetas/twopi)
			thetas-=n*twopi
			ret[:,:]=np.where(thetas<0,thetas+twopi,thetas)/twopi
		elif wave=='triangle':
			ret[:,:]=1.0-2.0*np.abs(np.floor((thetas*(1.0/twopi))+0.5)-(thetas*(1.0/twopi)))
	return ret
	
def randCurve():
	import random
	return random.random()-random.random()
	
def randomScatter(img,distance):
	import random
	def scatPoint(point):
		return (point[0]+distance*randCurve(),point[1]+distance*randCurve())
	img=scipy.ndimage.geometric_transform(img,scatPoint,mode='nearest')
	return img
	
def displaceImage(img,displacementMap,distance=10,angle=45):
	import math
	#angle=angle/180*math.pi
	if len(displacementMap.shape)>2:
		# TODO: should probably do a proper grayscale conversion
		displacementMap=displacementMap[:,:,1]
	def dissp(point):
		delta=displacementMap[point[0],point[1]]*distance
		return (point[0]+delta*math.sin(angle),point[1]-delta*math.cos(angle))
	img=scipy.ndimage.geometric_transform(img,dissp,mode='nearest')
	return img
	
def normalize(img):
	img=img-np.min(img)
	img=img/np.max(img)
	return img
	
def combine(img1,img2):
	return (img1+img2)/2.0
	
def section(img,minVal=0.0,maxVal=1.0):
	return normalize(np.clip(img,minVal,maxVal))
	
# https://developer.blender.org/diffusion/B/browse/master/source/blender/render/intern/source/render_texture.c
img=waveImage(500,500)
img2=numpyArray(perlinNoiseY(500,500))[:,:,1]
img=section(img2,0.5,0.51)
#img=normalize()
img=displaceImage(img2,img,45,2)
#img=perlinNoise(500,500,10)	
pilImage(img).show()


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
		print '  proceduralTextures.py [options]'
		print 'Options:'
		print '   NONE'