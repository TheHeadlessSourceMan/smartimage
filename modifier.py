#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This is a modifier layer such as blur, sharpen, posterize, etc
"""
from layer import *
from blendModes import *
from PIL import ImageFilter, ImageOps, ImageEnhance


def imageBorder(img,thickness,edge="#ffffff00"):
	"""
	mirror,repeat,clamp,[color]
	"""
	if edge=='mirror':
		newImage=Image.new(img.mode,(img.size[0]+thickness*2,img.size[0]+thickness*2))
		# top
		fill=img.crop((0,0,img.width,thickness))
		newImage.paste(fill,(thickness,0))
		# bottom
		fill=img.crop((0,image.height-thickness,img.width,image.height))
		newImage.paste(fill,(thickness,newImage.height-img.height))
		# left
		fill=img.crop((0,0,thickness,img.height))
		newImage.paste(fill,(0,thickness))
		# right
		fill=img.crop((image.width-thickness,0,img.width,image.height))
		newImage.paste(fill,(newImage.width-img.width,thickness))
		# TODO: corners
	elif edge=='repeat':
		newImage=Image.new(img.mode,(img.size[0]+thickness*2,img.size[0]+thickness*2))
		# top
		fill=img.crop((0,0,img.width,thickness))
		newImage.paste(fill,(thickness,0))
		# bottom
		fill=img.crop((0,image.height-thickness,img.width,image.height))
		newImage.paste(fill,(thickness,newImage.height-img.height))
		# left
		fill=img.crop((0,0,thickness,img.height))
		newImage.paste(fill,(0,thickness))
		# right
		fill=img.crop((image.width-thickness,0,img.width,image.height))
		newImage.paste(fill,(newImage.width-img.width,thickness))
		# TODO: corners
	elif edge=='clamp':
		newImage=Image.new(img.mode,(img.size[0]+thickness*2,img.size[0]+thickness*2))
		# top
		fill=img.crop((0,0,img.width,1))
		fill.thumbnail((img.width,thickness))
		newImage.paste(fill,(thickness,0))
		# bottom
		fill=img.crop((0,image.height-1,img.width,image.height))
		fill.thumbnail((img.width,thickness))
		newImage.paste(fill,(thickness,newImage.height-img.height))
		# left
		fill=img.crop((0,0,1,img.height))
		fill.thumbnail((thickness,img.width))
		newImage.paste(fill,(0,thickness))
		# right
		fill=img.crop((image.width-1,0,img.width,image.height))
		fill.thumbnail((thickness,img.height))
		newImage.paste(fill,(newImage.width-img.width,thickness))
		# TODO: corners
	else:
		newImage=Image.new(img.mode,(img.size[0]+thickness*2,img.size[0]+thickness*2),edge)
	# splat the original image in the middle
	if newImage.alpha in ['RGBA','LA']:
		newImage.alpha_composite(img,dest=(thickness,thickness))
	else:
		newImage.paste(img,(thickness,thickness))


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
		print '  modifier.py [options]'
		print 'Options:'
		print '   NONE'