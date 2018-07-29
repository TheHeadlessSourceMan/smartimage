#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Routines for the creation of procedural textures

TODO: see also:
	https://developer.blender.org/diffusion/B/browse/master/source/blender/render/intern/source/render_texture.c

"""
import scipy.ndimage,scipy.signal
import os,subprocess,time
from helper_routines import *
from PIL import Image,ImageDraw
import numpy as np
from math import *
import math
from colorCorrect import *
from selectionsAndPaths import *


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
	import random
	image = Image.new("RGB", (imgx, imgy))
	draw = ImageDraw.Draw(image)
	pixels = image.load()
	octaves = int(log(max(imgx, imgy), 2.0))
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
	if octaves==None:
		octaves=log(max(w,h), 2.0)
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
	0.5+0.5*sin(theta)
def _triwave(theta):
	b = 2*pi
	n = int(a / b)
	a -= n*b
	if a<0:
		a+=b
	return a/b
	
def cartesian2PolarX(img,order=1):
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
	ret=np.zeros((h,w))
	if radial:
		raise NotImplementedError() # TODO
	else:
		twopi=2*pi
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
	#angle=angle/180*pi
	img=numpyArray(img)
	displacementMap=numpyArray(displacementMap)
	if len(displacementMap.shape)>2:
		# TODO: should probably do a proper grayscale conversion
		displacementMap=displacementMap[:,:,1]
	def dissp(point):
		delta=displacementMap[point[0],point[1]]*distance
		return (point[0]+delta*sin(angle),point[1]-delta*cos(angle))
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
	
def warpCircle(img):
	"""
	wrap the image around a circle
	
	NOTE: only row 0 is used
	"""
	size=getSize(img)
	center=(size[0]/2,size[1]/2)
	def circ(point):
		r=sqrt((point[0]-center[0])**2+(point[1]-center[1])**2)
		return (0,r)
	return scipy.ndimage.geometric_transform(img,circ,mode='nearest')
	
def warpRotate(img,theta):
	"""
	wrap the image around a circle
	
	NOTE: only row 0 is used
	
	TODO: need to resize img larger to encoumpass rotated bounds
	"""
	originalSize=getSize(img)
	rot=scipy.ndimage.interpolation.rotate(img,theta)
	newSize=getSize(rot)
	bounds=[(newSize[0]-originalSize[0])/2,(newSize[1]-originalSize[1])/2,originalSize[0],originalSize[1]]
	return crop(rot,bounds)
	
def filmGrain(img,amount=None,iso=None):
	"""
	simulate film grain
	
	:param iso: try and mimic this film speed
	
	NOTES:
		https://hal.archives-ouvertes.fr/hal-01494123v2/document
		http://www.dctsystems.co.uk/Text/grain.pdf
	"""
	
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
		print img
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
	

GRADIENT_BLACK_TO_WHITE=[(0.0,(0.0,0.0,0.0)),(1.0,(1.0,1.0,1.0))]
GRADIENT_CLEAR_TO_WHITE=[(0.0,(1.0,1.0,1.0,0.0)),(1.0,(1.0,1.0,1.0,1.0))]
GRADIENT_CLEAR_TO_BLACK=[(0.0,(0.0,0.0,0.0,0.0)),(1.0,(0.0,0.0,0.0,1.0))]
GRADIENT_RAINBOW=[(0.0,(1.0,0.0,0.0)),(0.2,(1.0,0.75,0.0)),(0.4,(1.0,1.0,0.0)),(0.6,(0.0,1.0,0.0)),(0.8,(0.0,0.0,1.0)),(1.0,(0.8,0.0,1.0))]


def sinewave(src,(x,y),w=255):
	return np.sin(math.pi*x/w)
	
def ball(src,(x,y),w=255,h=255,cornerBased=False):
	center=(w/2,h/2)
	magnitude=np.sqrt(np.power(x-center[0],2)+np.power(y-center[1],2))
	if cornerBased:
		maxmag=math.sqrt(center[0]**2+center[1]**2)*2
	else:
		maxmag=max(center)*2
	val=np.cos(math.pi*magnitude/maxmag)
	return val
	
def cone(src,(x,y),w=255,h=255,cornerBased=False):
	center=(w/2,h/2)
	magnitude=np.sqrt(np.power(x-center[0],2)+np.power(y-center[1],2))
	if cornerBased:
		maxmag=math.sqrt(center[0]**2+center[1]**2)*2
	else:
		maxmag=max(center)*2
	val=1-magnitude/maxmag
	return val
	
def deltaC(size,center=None,magnitude=False):
	"""
	returns an array where every value is the distance from
	the center point.
	
	:param center: center point, if not specified, assume size/2
	:param magnitude: return a single magnitude value instead of [dx,dy]
	"""
	size=(int(size[0]),int(size[1]))
	if center==None:
		center=size[0]/2.0,size[1]/2.0
	if magnitude:
		img=np.ndarray((size[0],size[1]))
		for x in range(size[0]):
			for y in range(size[1]):
				img[x,y]=math.sqrt((x-center[0])**2+(y-center[1])**2)
	else:
		img=np.ndarray((size[0],size[1],2))
		for x in range(size[0]):
			for y in range(size[1]):
				img[x,y]=(x-center[0]),(y-center[1])
	return img
	
def normalize(img):
	"""
	squash the image to fit in range 0.0 to 1.0
	"""
	img=img-img.min()
	imax=img.max()
	if imax!=0:
		img=img/imax
	return img
	
def clock(size=(256,256),angle=0,sharpEdge=False):
	"""
	:param sharpEdge: if true, 100% black ends at 100% white for a difinitive angle -- otherwise gives more of a lighting effect
	"""
	points=np.ndarray(size)
	angle=0.75-angle/360.0
	dc=deltaC(size)
	img=np.arctan2(dc[:,:,0],dc[:,:,1])/math.pi
	img=(normalize(img)+angle)%1.0
	if not sharpEdge:
		img=deltaFromGray(img)
	return img
		
def deltaFromGray(img):
	"""
	returns an image differenced from gray
	"""
	return normalize(abs(img-0.5))
	
def distance(src):
	return scipy.ndimage.morphology.distance_transform_edt(src)

def valueRotate(img,amount=0.5):
	return np.mod(np.clip(img,0.0,1.0)+amount,1.0)
	
def flip90(src,(x,y)):
	return src[y,x]
	
def repeat(src,(x,y),n=2):
	src=src[x,y]*n%2
	if src<=1:
		return 1-src
	return src-1

def apply(fn,img=None,**params):
	"""
	apply a transformation to an image
	
	:param fn: a function that takes (x,y) and returns a value 0.0 to 1.0
	:param img: an image to apply the function to
	"""
	if type(img)==type(None):
		img=np.ndarray((256,256))
	newimg=np.ndarray(img.shape)
	for x in range(img.shape[0]):
		for y in range(img.shape[1]):
			newimg[x,y]=fn(img,(x,y),**params)
	return newimg
	
def preview(img):
	"""
	this is a utility to do image previews
	
	It was created because stinking photoshop always took over the pil Image.show()
	"""
	mode='pilShow'
	#mode='save'
	#mode='windowsPhotoViewer'
	# ------
	if mode=='pilShow':
		pilImage(img).show()
	elif mode=='save':
		path=os.path.abspath('tmp.png')
		img.save(path)
	elif mode=='windowsPhotoViewer':
		if False:
			for dllPath in [r'%ProgramFiles%\Windows Photo Viewer',r'%ProgramFiles%\Windows Photo Gallery']:
				if os.path.exists(dllPath):
					break			
			# %SystemRoot%\System32\rundll32.exe "%ProgramFiles%\Windows Photo Gallery\PhotoViewer.dll", ImageView_Fullscreen %1
			dllPath=r'C:\Program Files\Windows Photo Gallery'
			cmd=r'%SystemRoot%\System32\rundll32.exe "'+dllPath+r'\PhotoViewer.dll", ImageView_Fullscreen "'+path+'"'
			print cmd
			po=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			out,err=po.communicate()
			print out,err
		else:
			cmd=r'"C:\Program Files\Windows Photo Gallery\WindowsPhotoGallery.exe" "'+path+'"'
			print cmd
			po=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			out,err=po.communicate()
			print out,err
		time.sleep(2.5)
		os.remove(path)
	
def highlights(img,level=0.9):
	"""
	return a mask of all highlights
	"""
	return np.where(img<level,0,img)
	
def shadows(img,level=0.1):
	"""
	return a mask of all shadows
	"""
	return np.where(img>level,0,1-img)
	
def streak(img,size=15):
	return img+directionalBlur(highlights(img,.95),size)
	
def directionalBlur(img,size=15):
	oSize=img.shape
	kernel= np.zeros((size,size))
	kernel[int((size-1)/2), :] = np.ones(size)
	kernel= kernel / size
	img=scipy.signal.convolve(img,kernel)
	d=(img.shape[0]-oSize[0])/2,(img.shape[1]-oSize[1])/2
	img=img[d[0]:-d[0],d[1]:-d[1]]
	return img
	
def xypoints(img):
	"""
	get numpy array of x,y points for the image
	
	yeah, it may be a bad way to do this, yet here we are, Robert.
	"""
	xy=np.ndarray((img.shape[0],img.shape[1],2))
	for x in range(img.shape[0]):
		for y in range(img.shape[1]):
			xy[x,y]=[x,y]
	return xy
	
def voronoi(size=(256,256),npoints=30,mode='twoNearestDiff',invert=False):
	"""
	
	:param mode: 'simple','squared','twoNearestDiff','twoNearestMult'
	
	see also:
		http://blackpawn.com/texts/cellular/default.html
	"""
	size=(int(size[0]),int(size[1]))
	img=np.ndarray(size) 
	size=np.array(size)
	points=np.random.rand(npoints,2)*size # random points where voroni connections will appear
	xy=xypoints(img).reshape((-1,2)) # flattened list of xy points for every pixel
	dist=scipy.spatial.distance.cdist(xy,points) # for each pixel, determine distance to all voroni points
	if mode=='simple':
		img=np.min(dist,axis=1)
	elif mode=='squared':
		img=np.min(dist,axis=1)**2
	elif mode=='twoNearestDiff':
		#smallest=np.argsort(dist,axis=1)
		smallest=np.argpartition(dist,2,axis=1)[:,0:2] # faster because it stops sorting after 2
		img=dist[:,smallest[:,1]]-dist[:,smallest[:,0]]
	elif mode=='twoNearestMult':
		#smallest=np.argsort(dist,axis=1)
		smallest=np.argpartition(dist,2,axis=1)[:,0:2] # faster because it stops sorting after 2
		img=dist[:,smallest[:,1]]*dist[:,smallest[:,0]]
	# convert pixel list back into 2d array
	img=normalize(img.reshape((size[0],size[1])))
	if invert:
		img=1.0-img
	return img

def smoothNoise(size=(256,256),undersize=0.5):
	"""
	create smooth noise by starting with undersized random noise
	and then scaling it up
	"""
	noise=np.random.random((int(size[0]*undersize),int(size[0]*undersize)))
	if undersize!=0:
		noise=scipy.misc.imresize(noise,(int(size[0]),int(size[1])),interp='bilinear')/255.0
	return noise
	
def turbulence(size=(256,256),turbSize=None):
	"""
	Generate a turbulence noise
	
	:param turbSize: initial size of the turbulence default is max(w,h)/10
	"""
	if turbSize==None:
		turbSize=max(size)/10.0
	value=0.0
	img=np.ndarray((int(size[0]),int(size[1])))
	s=turbSize
	while s>=1.0:
		noise=smoothNoise(size,s/turbSize)/s
		img=img+noise
		s/=2.0
	return normalize(img)
	
def marble(size=(256,256),xPeriod=3.0,yPeriod=10.0,turbPower=0.8,turbSize=None):
	"""
	Generate a marble texture akin to blender and others
	
	:param xPeriod: defines repetition of marble lines in x direction
	:param yPeriod: defines repetition of marble lines in y direction
	:param turbPower: add twists and swirls (when turbPower==0  it becomes a normal sine pattern)
	:param turbSize: initial size of the turbulence default is max(w,h)/10
	
	NOTE:
		xPeriod and yPeriod together define the angle of the lines
		xPeriod and yPeriod both 0 then it becomes a normal clouds or turbulence pattern
		
	Optimized version of:
		https://lodev.org/cgtutor/randomnoise.html
	"""
	w,h=size
	turb=turbulence(size,turbSize)*turbPower
	# determine where the pixels will cycle
	cycleValue=np.ndarray((w,h))
	for y in range(h):
		for x in range(w):
			cycleValue[x,y]=(x*xPeriod/w)+(y*yPeriod/h)
	# add in the turbulence and then last of all, make it a sinewave
	img=np.abs(np.sin((cycleValue+turb)*math.pi))
	return img
	
def woodRings(size=(256,256),xyPeriod=12.0,turbPower=0.15,turbSize=32.0):
	"""
	Draw wood rings
	
	:param xyPeriod: number of rings
	:param turbPower: makes twists
	:param turbSize: # initial size of the turbulence
	
	Optimized version of:
		https://lodev.org/cgtutor/randomnoise.html
	"""
	w,h=size
	turb=turbulence(size,turbSize)*turbPower
	dc=normalize(deltaC(size,magnitude=True))
	img = np.abs(np.sin(xyPeriod * (dc+turb) * math.pi))
	return normalize(img)
	
def waveformTexture(size=(256,256),waveform="sine",frequency=(10,10),noise=0.2,noiseBasis="perlin",noiseOctaves=4,noiseSoften=0.0,direction=0,invert=False):
	size=(int(size[0]),int(size[1]))
	w,h=size
	noiseSize=max(size)/8 # TODO: pass this value in somehow
	turb=turbulence(size,noiseSize)*noise
	if direction=='circular':
		dc=normalize(deltaC(size,magnitude=True))
		xyPeriod=frequency[0]#(w/frequency[0]+h/frequency[1])/2.0
		img=np.abs(np.sin(xyPeriod*(dc+turb)*math.pi))
		invert=invert==False # flip invert to look more as expected
	else:
		xPeriod=frequency[0]/2.0
		yPeriod=frequency[1]/2.0
		# determine where the pixels will cycle
		cycleValue=np.ndarray((w,h))
		for y in range(h):
			for x in range(w):
				cycleValue[x,y]=(x*xPeriod/w)+(y*yPeriod/h)
		# add in the turbulence and then last of all, make it a sinewave
		img=np.abs(np.sin((cycleValue+turb)*math.pi))
	img=normalize(img)
	if invert:
		img=1.0-img
	return img

def clock2(size=(256,256),waveform="sine",frequency=(10,10),noise=0.2,noiseBasis="perlin",noiseOctaves=4,noiseSoften=0.0,direction=0,invert=False):
	noiseSize=max(size)/8 # TODO: pass this value in somehow
	turb=turbulence(size,noiseSize)*noise
	points=np.ndarray((int(size[0]),int(size[1])))
	angle=0.75-direction/360.0
	dc=deltaC(size)
	img=np.arctan2(dc[:,:,0],dc[:,:,1])/math.pi
	img=np.abs(np.sin((((normalize(img)+angle)%1.0)+turb)*math.pi))
	img=normalize(img)
	if invert:
		img=1.0-img
	return img
	
def x(img=(256,256),color=1):
	"""
	img can be an image array or size tuple
	"""
	if type(img)==tuple:
		size=img
		if type(color) in (float,int):
			img=np.ndarray((size[0],size[1]))
		else:
			img=np.ndarray((size[0],size[1],len(color)))
	else:
		size=img.shape[0:1]
	img=line(img,[0,0],[size[0]-1,size[1]-1])
	img=line(img,[0,size[1]-1],[size[0]-1,0])
	return img
	
def line(img,(x,y),(x2,y2),thick=1,color=1):
	"""
	comes from this neat implementation:
		https://stackoverflow.com/questions/31638651/how-can-i-draw-lines-into-numpy-arrays
	"""
	def trapez(y,y0,w):
		return np.clip(np.minimum(y+1+w/2-y0, -y+1+w/2+y0),0,1)

	def weighted_line(r0, c0, r1, c1, w, rmin=0, rmax=np.inf):
		# The algorithm below works fine if c1 >= c0 and c1-c0 >= abs(r1-r0).
		# If either of these cases are violated, do some switches.
		if abs(c1-c0) < abs(r1-r0):
			# Switch x and y, and switch again when returning.
			xx, yy, val = weighted_line(c0, r0, c1, r1, w, rmin=rmin, rmax=rmax)
			return (yy, xx, val)

		# At this point we know that the distance in columns (x) is greater
		# than that in rows (y). Possibly one more switch if c0 > c1.
		if c0 > c1:
			return weighted_line(r1, c1, r0, c0, w, rmin=rmin, rmax=rmax)

		# The following is now always < 1 in abs
		num=r1-r0
		denom=c1-c0
		slope = np.divide(num,denom,out=np.zeros_like(denom), where=denom!=0)

		# Adjust weight by the slope
		w *= np.sqrt(1+np.abs(slope)) / 2

		# We write y as a function of x, because the slope is always <= 1
		# (in absolute value)
		x = np.arange(c0, c1+1, dtype=float)
		y = x * slope + (c1*r0-c0*r1) / (c1-c0)

		# Now instead of 2 values for y, we have 2*np.ceil(w/2).
		# All values are 1 except the upmost and bottommost.
		thickness = np.ceil(w/2)
		yy = (np.floor(y).reshape(-1,1) + np.arange(-thickness-1,thickness+2).reshape(1,-1))
		xx = np.repeat(x, yy.shape[1])
		vals = trapez(yy, y.reshape(-1,1), w).flatten()

		yy = yy.flatten()

		# Exclude useless parts and those outside of the interval
		# to avoid parts outside of the picture
		mask = np.logical_and.reduce((yy >= rmin, yy < rmax, vals > 0))

		return (yy[mask].astype(int), xx[mask].astype(int), vals[mask])
	def naive_line(r0, c0, r1, c1):
		# The algorithm below works fine if c1 >= c0 and c1-c0 >= abs(r1-r0).
		# If either of these cases are violated, do some switches.
		if abs(c1-c0) < abs(r1-r0):
			# Switch x and y, and switch again when returning.
			xx, yy, val = naive_line(c0, r0, c1, r1)
			return (yy, xx, val)

		# At this point we know that the distance in columns (x) is greater
		# than that in rows (y). Possibly one more switch if c0 > c1.
		if c0 > c1:
			return naive_line(r1, c1, r0, c0)

		# We write y as a function of x, because the slope is always <= 1
		# (in absolute value)
		x = np.arange(c0, c1+1, dtype=float)
		y = x * (r1-r0) / (c1-c0) + (c1*r0-c0*r1) / (c1-c0)

		valbot = np.floor(y)-y+1
		valtop = y-np.floor(y)
		return (np.concatenate((np.floor(y), np.floor(y)+1)).astype(int), np.concatenate((x,x)).astype(int),np.concatenate((valbot, valtop)))
	if thick==1:
		rows, cols, weights=naive_line(x,y,x2,y2)
	else:
		rows, cols, weights=weighted_line(x,y,x2,y2,thick,rmin=0,rmax=max(img.shape[0],img.shape[1]))
	w = weights.reshape([-1, 1])            # reshape anti-alias weights
	if len(img.shape)>2:
		img[rows, cols, 0:3] = (
			np.multiply((1 - w) * np.ones([1, 3]),img[rows, cols, 0:3]) +
			w * np.array([color])
		)
	else:
		img[rows, cols] = (
			np.multiply(
				(1 - w) * np.ones([1, ]),
				img[rows, cols]) +
			w * 
			color
		)[0]

	return img
	
def dilate(img,size=3):
	return scipy.ndimage.grey_dilation(img,size=(size,size))
	
def circularBlur(img):
	"""
	http://chemaguerra.com/circular-radial-blur/
	"""
	pass
	
def zoomBlur(img):
	"""
	http://chemaguerra.com/circular-radial-blur/
	"""
	pass
	
	
if __name__ == '__main__':
	img=woodRings()
	img=streak(img)
	#img=apply(flip90,img)
	#img=x()
	#img=dilate(img)
	img=np.clip(img,0.0,1.0)
	img=Image.fromarray(np.uint8(img*255))
	#img1=waveImage(500,500)
	#img1=warpRotate(img1,-45)
	#img1=warpCircle(img1)
	#img2=numpyArray(perlinNoiseY(500,500))[:,:,1]
	#img2=normalize(img2)
	#img2=levels(img2,0.0,0.5,1.0,0.2,0.8)
	#img=displaceImage(img1,img2,45,2)
	#img=levels(img,0.0,0.25,0.5)
	#img=img1
	#img=img2
	#img=colormap(img,GRADIENT_RAINBOW)
	#img=colormap(img,"#ff0000")
	preview(img)
