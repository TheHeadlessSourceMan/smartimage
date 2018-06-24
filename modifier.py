#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This is a modifier layer such as blur, sharpen, posterize, etc
"""
from layer import *
from blendModes import *
from PIL import ImageFilter, ImageOps, ImageEnhance
import numpy as np


def imageBorder(img,thickness,edge="#ffffff00"):
	"""
	edge can be:
		mirror - reflect the pixels leading up to the border
		repeat - repeat the image over again (useful with repeating textures)
		clamp - streak last pixels out to edge
		[background color]
	"""
	if edge=='mirror':
		newImage=Image.new(img.mode,(img.size[0]+thickness*2,img.size[1]+thickness*2))
		# top
		fill=ImageOps.flip(img.crop((0,0,img.width,thickness)))
		newImage.paste(fill,(thickness,0))
		# bottom
		fill=ImageOps.flip(img.crop((0,img.height-thickness,img.width,img.height)))
		newImage.paste(fill,(thickness,img.height+thickness))
		# left
		fill=ImageOps.mirror(img.crop((0,0,thickness,img.height)))
		newImage.paste(fill,(0,thickness))
		# right
		fill=ImageOps.mirror(img.crop((img.width-thickness,0,img.width,img.height)))
		newImage.paste(fill,(img.width+thickness,thickness))
		# top-left corner
		fill=ImageOps.mirror(ImageOps.flip(img.crop((0,0,thickness,thickness))))
		newImage.paste(fill,(0,0))
		# top-right corner
		fill=ImageOps.mirror(ImageOps.flip(img.crop((img.width-thickness,0,img.width,thickness))))
		newImage.paste(fill,(img.width+thickness,0))
		# bottom-left corner
		fill=ImageOps.mirror(ImageOps.flip(img.crop((0,img.height-thickness,thickness,img.height))))
		newImage.paste(fill,(0,img.height+thickness))
		# bottom-right corner
		fill=ImageOps.mirror(ImageOps.flip(img.crop((img.width-thickness,img.height-thickness,img.width,img.height))))
		newImage.paste(fill,(img.width+thickness,img.height+thickness))
	elif edge=='repeat':
		newImage=Image.new(img.mode,(img.size[0]+thickness*2,img.size[1]+thickness*2))
		# top
		fill=img.crop((0,0,img.width,thickness))
		newImage.paste(fill,(thickness,img.height+thickness))
		# bottom
		fill=img.crop((0,img.height-thickness,img.width,img.height))
		newImage.paste(fill,(thickness,0))
		# left
		fill=img.crop((0,0,thickness,img.height))
		newImage.paste(fill,(img.width+thickness,thickness))
		# right
		fill=img.crop((img.width-thickness,0,img.width,img.height))
		newImage.paste(fill,(0,thickness))
		# top-left corner
		fill=img.crop((0,0,thickness,thickness))
		newImage.paste(fill,(img.width+thickness,img.height+thickness))
		# top-right corner
		fill=img.crop((img.width-thickness,0,img.width,thickness))
		newImage.paste(fill,(0,img.height+thickness))
		# bottom-left corner
		fill=img.crop((0,img.height-thickness,thickness,img.height))
		newImage.paste(fill,(img.width+thickness,0))
		# bottom-right corner
		fill=img.crop((img.width-thickness,img.height-thickness,img.width,img.height))
		newImage.paste(fill,(0,0))
	elif edge=='clamp':
		newImage=Image.new(img.mode,(img.size[0]+thickness*2,img.size[1]+thickness*2))
		# top
		fill=img.crop((0,0,img.width,1)).resize((img.width,thickness),resample=Image.NEAREST)
		newImage.paste(fill,(thickness,0))
		# bottom
		fill=img.crop((0,img.height-1,img.width,img.height)).resize((img.width,thickness),resample=Image.NEAREST)
		newImage.paste(fill,(thickness,img.height+thickness))
		# left
		fill=img.crop((0,0,1,img.height)).resize((thickness,img.height),resample=Image.NEAREST)
		newImage.paste(fill,(0,thickness))
		# right
		fill=img.crop((img.width-1,0,img.width,img.height)).resize((thickness,img.height),resample=Image.NEAREST)
		newImage.paste(fill,(img.width+thickness,thickness))
		# TODO: corners
		# top-left corner
		fill=img.crop((0,0,1,1)).resize((thickness,thickness),resample=Image.NEAREST)
		newImage.paste(fill,(0,0))
		# top-right corner
		fill=img.crop((img.width-1,0,img.width,1)).resize((thickness,thickness),resample=Image.NEAREST)
		newImage.paste(fill,(img.width+thickness,0))
		# bottom-left corner
		fill=img.crop((0,img.height-1,1,img.height)).resize((thickness,thickness),resample=Image.NEAREST)
		newImage.paste(fill,(0,img.height+thickness))
		# bottom-right corner
		fill=img.crop((img.width-1,img.height-1,img.width,img.height)).resize((thickness,thickness),resample=Image.NEAREST)
		newImage.paste(fill,(img.width+thickness,img.height+thickness))
	else:
		newImage=Image.new(img.mode,(img.size[0]+thickness*2,img.size[1]+thickness*2),edge)
	# splat the original image in the middle
	if True:
		if newImage.mode.endswith('A'):
			newImage.alpha_composite(img,dest=(thickness,thickness))
		else:
			newImage.paste(img,(thickness,thickness))
	return newImage


CONVOLVE_MATTRICES={
	'emboss':[[-2,-1, 0],
	          [-1, 1, 1],
	          [ 0, 1, 2]],
	'edgeDetect':[[ 0, 1, 0],
	              [ 1,-4, 1],
	              [ 0, 1, 0]],
	'edgeEnhance':[[ 0, 0, 0],
	               [-1, 1, 0],
	               [ 0, 0, 0]],
	'blur':[[ 0, 0, 0, 0, 0],
	        [ 0, 1, 1, 1, 0],
	        [ 0, 1, 1, 1, 0],
	        [ 0, 1, 1, 1, 0],
	        [ 0, 0, 0, 0, 0]],
	'sharpen':[[ 0, 0, 0, 0, 0],
	           [ 0, 0,-1, 0, 0],
	           [ 0,-1, 5,-1, 0],
	           [ 0, 0,-1, 0, 0],
	           [ 0, 0, 0, 0, 0]],
}
	
	
def convolve(img,matrix,add,divide,edge):
	size=len(matrix)
	border=size/2-1
	img=imageBorder(img,border,edge)
	k=ImageFilter.Kernel((size,size),matrix,scale=divide,offset=add)
	img=img.filter(k)


def distort(img,points,r=1):
	"""
	morph an image to fit the given points
	"""
	data=((f[0],f[1]) for f,t in points)
	img.transform(size,Image.MESH,data)


def rgb2hsvImage(img):
	import compositor
	rgb=np.asarray(img)
	final=compositor.rgb_to_hsv(rgb)
	return Image.fromarray(final.astype('uint8'),'RGB')
	
def rgb2cmykImage(img):
	import compositor
	rgb=np.asarray(img)
	final=compositor.rgb_to_cmyk(rgb)
	return Image.fromarray(final.astype('uint8'),'RGBA')
	
def getChannel(img,channel):
	"""
	get a channel as a new image.
	Returns a grayscale image, or None
	
	supports R,G,B,A,H,S,V
	"""
	if channel=='R':
		if img.mode.startswith('RGB'):
			ch=img.split()[0]
		else:
			ch=None
	elif channel=='G':
		if img.mode.startswith('RGB'):
			ch=img.split()[1]
		else:
			ch=None
	elif channel=='B':
		if img.mode.startswith('RGB'):
			ch=img.split()[2]
		else:
			ch=None
	elif channel=='A':
		if img.mode.endswith('A'):
			ch=img.split()[-1]
		else:
			ch=None
	elif channel=='H':
		img=rgb2hsvImage(img)
		ch=img.split()[0]
	elif channel=='S':
		img=rgb2hsvImage(img)
		ch=img.split()[1]
	elif channel=='V':
		img=rgb2hsvImage(img)
		ch=img.split()[2]
	elif channel=='C':
		img=rgb2cmykImage(img)
		ch=img.split()[0]
	elif channel=='M':
		img=rgb2cmykImage(img)
		ch=img.split()[1]
	elif channel=='Y':
		img=rgb2cmykImage(img)
		ch=img.split()[2]
	elif channel=='K':
		img=rgb2cmykImage(img)
		ch=img.split()[3]
	else:
		raise Exception('Unknown channel: '+channel)
	return ch
	
	
def getHistogram(img,channel='V',invert=False):
	"""
	Gets a histogram for the given image
	
	channel can be V,R,G,B,A, or RGB
		if single channel, returns a simple black and white image
		if RGB, returns all three layered together in a color image
	"""
	import PIL.ImageDraw
	if len(channel)==1:
		size=(255,255)
		if invert:
			bg=0
			fg=255
		else:
			fg=0
			bg=255
		ch=getChannel(img,channel)
		out=Image.new("L",size,bg)
		draw=PIL.ImageDraw.Draw(out) 
		hist=ch.histogram()
		histMax=max(hist)
		yScale=float(size[1])/histMax
		for i in range(len(hist)):
			val=hist[i]
			if val>0:
				draw.line((i,size[1],i,size[1]-(val*yScale)),fill=fg)        
	elif channel=='RGB':
		out=PIL.Image.merge('RGB',(
			getHistogram(img,'R',invert==False),
			getHistogram(img,'G',invert==False),
			getHistogram(img,'B',invert==False)
			))   
	else:
		raise Exception('not a valid channel')
	return out
	

def applyHistogram(hist,img,channels='RGB'):
	pass
	
def rolling_window(a, shape):  # rolling window for 2D array
    s = (a.shape[0] - shape[0] + 1,) + (a.shape[1] - shape[1] + 1,) + shape
    strides = a.strides + a.strides
    return np.lib.stride_tricks.as_strided(a, shape=s, strides=strides)
	
	
def applyFunctionToPatch(fn,a,patchSize=(3,3)):
	# get all patchSize mattrices possible by sliding a patchSize window across the array
	w=rolling_window(a,patchSize)
	v=np.vectorize(fn,signature='(m,n)->(k,l)')
	if False:
		marginX=(patchSize[0]-1)/2
		marginY=(patchSize[1]-1)/2
		a2=np.array([])
		for x in range(marginX,a.shape[0]-marginX):
			for y in range(marginY,a.shape[1]-marginY):
				v(a[x-marginX:x+marginX+1,y-marginY:y+marginY+1])
	w.flags.writeable=True
	r=v(w)
	return r
	
def erode(img):
	a=np.asarray(img)
	def _erode(p):
		print p
		p[1,1]=1
		return p
	applyFunctionToPatch(_erode,a,(3,3))
	return Image.fromarray(a.astype('uint8'),img.mode)


class Modifier(Layer):
	"""
	This is a modifier layer such as blur, sharpen, posterize, etc
	"""

	def __init__(self,docRoot,parent,xml):
		Layer.__init__(self,docRoot,parent,xml)

	@property
	def type(self):
		"""
		supported types:
			brightness,contrast,rotate
		"""
		return self._getProperty('type','?')

	@property
	def amount(self):
		"""
		supported types:
			brightness,contrast,rotate,sharpen,unsharp_mask
		"""
		return _getPropertyPercent('amount',1.0)

	@property
	def edge(self):
		"""
		treatment for edges
			options: mirror,repeat,clamp,[color]

		useful for:
			convolve, expand_border, others?
		"""
		return _getProperty('edge','mirror')

	@property
	def add(self):
		"""
		add a constant to the convolved value
		useful, for instance, in shifting negative emboss values

		useful for:
			convolve
		"""
		return float(_getProperty('add',0))

	@property
	def divide(self):
		"""
		divide the convolved value by a constant

		useful for:
			convolve
		"""
		divide=float(_getProperty('divide',0))
		if divide==0:
			divide=None
		return divide

	@property
	def matrix(self):
		"""
		a 3x3 or 5x5 convolution matrix

		useful for:
			convolve
		"""
		ret=[]
		property=_getProperty('matrix','[[0,0,0],[0,1,0],[0,0,0]]').replace(' ','')
		if property.startswith('[['):
			matrix=property[1:-1]
		else:
			matrix=property
		matrix=matrix.split('[')[1:]
		size=None
		for row in matrix:
			row=row.split(']',1)[0].split(',')
			if (size==None and len(row) not in [5,3]) or size!=len(row):
				size=len(row)
				raise Exception('Convolution matrix "'+property+'" is not 3x3 or 5x5!')
			ret.append([float(v) for v in row])
		if len(ret)!=size:
			raise Exception('Convolution matrix "'+property+'" is not 3x3 or 5x5!')
		return ret

	@property
	def channels(self):
		"""
		only apply the effect to the given channels

		useful for:
			convolve,others?
		"""
		return _getProperty('channels','rgba').lower()

	@property
	def modifierOpacity(self):
		"""
		the opacity of the modifier alone, for instance drop shadows
		"""
		return self._getPropertyPercent('modifierOpacity',1.0)

	@property
	def blurRadius(self):
		"""
		supported types:
			gaussian_blur,box_blur,shadow,unsharp_mask
		"""
		return float(self._getProperty('blurRadius',0))

	@property
	def threshold(self):
		"""
		supported types:
			unsharp_mask
		"""
		return float(self._getProperty('threshold',0))

	def roi(self,image):
		type=self.type
		# only certain transforms change the region of interest
		if self.type in ['shadow','blur','flip','mirror']:
			image=self.transform(image)
		return image

	def _transform(self,img):
		"""
		For a list of more transformations available, see:
			http://pillow.readthedocs.io/en/latest/reference/ImageFilter.html
		"""
		type=self.type
		if type=='shadow':
			offsX=10
			offsY=10
			blurRadius=self.blurRadius
			shadow=img.copy()
			control=ImageEnhance.Brightness(shadow)
			shadow=control.enhance(0)
			final=Image.new("RGBA",(img.width+abs(offsX),img.height+abs(offsX)))
			final.putalpha(int(self.modifierOpacity*255))
			final.alpha_composite(shadow,dest=(int(max(offsX-blurRadius,0)),int(max(offsY-blurRadius,0))))
			if blurRadius>0:
				final=final.filter(ImageFilter.GaussianBlur(radius=blurRadius))
			final.alpha_composite(img,dest=(max(-offsX,0),max(-offsY,0)))
			img=final
		elif type=='convolve':
			matrix=self.matrix()
			ImageFilter.Kernel((len(matrix),len(matrix)),matrix,scale=self.divide,offset=self.add)
		elif type=='autocrop':
			# the idea is you cut off as many rows from each side that are all alpha=0
			raise NotImplementedError()
		elif type=='brightness':
			control=ImageEnhance.Brightness(img)
			control.amount=self.amount
		elif type=='contrast':
			control=ImageEnhance.Contrast(img)
			control.amount=self.amount
		elif type=='saturation':
			control=ImageEnhance.Color(img)
			control.amount=self.amount
		elif type=='blur':
			img=img.filter(ImageFilter.BLUR)#,self.amount)
		elif type=='gaussian_blur':
			blurRadius=self.blurRadius
			if blurRadius>0:
				img=img.filter(ImageFilter.GaussianBlur(radius=blurRadius))
		elif type=='box_blur':
			blurRadius=self.blurRadius
			if blurRadius>0:
				img.filter(ImageFilter.BoxBlur(radius=blurRadius))
		elif type=='unsharp_mask':
			ImageFilter.UnsharpMask(radius=self.blurRadius,percent=self.amount*100,threshold=self.threshold)
		elif type=='contour':
			img=img.filter(ImageFilter.CONTOUR,self.amount)
		elif type=='detail':
			img=img.filter(ImageFilter.DETAIL,self.amount)
		elif type=='edge_enhance':
			img=img.filter(ImageFilter.EDGE_ENHANCE,self.amount)
		elif type=='edge_enhance_more':
			img=img.filter(ImageFilter.EDGE_ENHANCE_MORE,self.amount)
		elif type=='emboss':
			img=img.filter(ImageFilter.EMBOSS,self.amount)
		elif type=='edge_detect':
			img=img.filter(ImageFilter.FIND_EDGES,self.amount)
		elif type=='smooth':
			img=img.filter(ImageFilter.SMOOTH,self.amount)
		elif type=='smooth_more':
			img=img.filter(ImageFilter.SMOOTH_MORE,self.amount)
		elif type=='sharpen':
			img=img.filter(ImageFilter.SHARPEN,self.amount)
		elif type=='invert':
			img=ImageOps.invert(img)
		elif type=='flip':
			img=ImageOps.flip(img)
		elif type=='mirror':
			img=ImageOps.mirror(img)
		elif type=='posterize':
			img=ImageOps.posterize(img)
		elif type=='solarize':
			img=ImageOps.solarize(img)
		else:
			raise NotImplementedError('Unknown modifier "'+type+'"')
		return img

	def renderImage(self,renderContext=None):
		"""
		WARNING: Do not modify the image without doing a .copy() first!
		"""
		opacity=self.opacity
		if opacity<=0.0 or self.visible==False:
			return None
		image=self._transform(Layer.renderImage(self,renderContext).copy())
		if self.opacity<1.0:
			setOpacity(image,opacity)
		return image


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
		img=None
		for arg in sys.argv[1:]:
			if arg.startswith('-'):
				arg=[a.strip() for a in arg.split('=',1)]
				if arg[0] in ['-h','--help']:
					printhelp=True
				elif arg[0]=='--erode':
					i2=erode(img)
					i2.show()
				elif arg[0]=='--histogram':
					mode='RGB'
					if len(arg)>1:
						mode=arg[1]
					hist=getHistogram(img,mode)
					hist.show()
				elif arg[0]=='--channel':
					ch=getChannel(img,arg[1])
					if ch==None:
						print 'No channel:',arg[1]
					else:
						ch.show()
				elif arg[0]=='--border':
					thickness,border=arg[1].split(',',1)
					im=imageBorder(img,int(thickness),border)
					im.show()
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				img=Image.open(arg)
	if printhelp:
		print 'Usage:'
		print '  modifier.py image.jpg [options]'
		print 'Options:'
		print '   --erode .................. erode the image'
		print '   --histogram[=RGB] ........ possible values are V,R,G,B,A,or RGB'
		print '   --channel=R .............. extract a channel from the image - R,G,B,A,H,S,V'
		print '   --border=thickness,edge .. expand the image with a border - edge can be mirror,repeat,clamp,[color]'