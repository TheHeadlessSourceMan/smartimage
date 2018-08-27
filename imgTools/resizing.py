#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Contains a litany of resizing/pasting/cropping routines
"""
from imageRepr import *
from bounds import *


def imageBorder(img,thickness,edge="#ffffff00"):
	"""
	Add a border of thickness pixels around the image

	:param img: the image to add a border to can be pil image, numpy array, or whatever
	:param thickness: the border thickness in pixels
	:param edge: defines how to extend.  It can be:
		mirror - reflect the pixels leading up to the border
		repeat - repeat the image over again (useful with repeating textures)
		clamp - streak last pixels out to edge
		[background color] - simply fill with the given color
	
	TODO: combine into extendImageCanvas function
	"""
	img=pilImage(img)
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
		fill=img.crop((0,0,img.width,1)).regetSize((img.width,thickness),resample=Image.NEAREST)
		newImage.paste(fill,(thickness,0))
		# bottom
		fill=img.crop((0,img.height-1,img.width,img.height)).regetSize((img.width,thickness),resample=Image.NEAREST)
		newImage.paste(fill,(thickness,img.height+thickness))
		# left
		fill=img.crop((0,0,1,img.height)).regetSize((thickness,img.height),resample=Image.NEAREST)
		newImage.paste(fill,(0,thickness))
		# right
		fill=img.crop((img.width-1,0,img.width,img.height)).regetSize((thickness,img.height),resample=Image.NEAREST)
		newImage.paste(fill,(img.width+thickness,thickness))
		# TODO: corners
		# top-left corner
		fill=img.crop((0,0,1,1)).regetSize((thickness,thickness),resample=Image.NEAREST)
		newImage.paste(fill,(0,0))
		# top-right corner
		fill=img.crop((img.width-1,0,img.width,1)).regetSize((thickness,thickness),resample=Image.NEAREST)
		newImage.paste(fill,(img.width+thickness,0))
		# bottom-left corner
		fill=img.crop((0,img.height-1,1,img.height)).regetSize((thickness,thickness),resample=Image.NEAREST)
		newImage.paste(fill,(0,img.height+thickness))
		# bottom-right corner
		fill=img.crop((img.width-1,img.height-1,img.width,img.height)).regetSize((thickness,thickness),resample=Image.NEAREST)
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

	
def extendImageCanvas(pilImage,newBounds,extendColor=(128,128,128,0)):
	"""
	Make pilImage the correct canvas size/location.

	:param pilImage: the image to move
	:param newBounds: - (w,h) or (x,y,w,h) or Bounds object
	:param extendColor: color to use when extending the canvas (automatically choses image mode based on this color)

	:return new PIL image:
	
	NOTE: always creates a new image, so no original bits are altered
	"""
	if type(newBounds)==tuple:
		if len(newBounds)>2:
			x,y,w,h=newBounds
		else:
			x,y=0,0
			w,h=newBounds
	else:
		x,y,w,h=newBounds.x,newBounds.y,newBounds.w,newBounds.h
	if w<pilImage.width or h<pilImage.height:
		raise Exception('Cannot "extend" canvas to smaller size. ('+str(pilImage.width)+','+str(pilImage.height)+') to ('+str(w)+','+str(h)+')')
	if type(extendColor) not in [list,tuple] or len(extendColor)<2:
		mode="L"
	elif len(extendColor)<4:
		mode="RGB"
	else:
		mode="RGBA"
	mode=maxMode(mode,pilImage)
	img=Image.new(mode,(int(w),int(h)),extendColor)
	x=max(0,w/2-pilImage.width/2)
	y=max(0,h/2-pilImage.height/2)
	if hasAlpha(mode):
		if not hasAlpha(pilImage):
			pilImage=pilImage.convert(maxMode(pilImage,requireAlpha=True))
		img.alpha_composite(pilImage,dest=(int(x),int(y)))
	else:
		img.paste(pilImage,box=(int(x),int(y)))
	return img


def paste(image,overImage,position=(0,0),resize=True):
	"""
	A simple, dumb, paste operation like PIL's paste, only automatically uses alpha

	:param image: the image to be pasted on top (if None, returns overImage)
	:param overImage: the image will be pasted over the top of this image (if None, returns image)
	:param position: the position to place the new image, relative to overImage (can be negative)
	:param resize: allow the resulting image to be resized if overImage extends beyond its bounds

	:returns: a combined image, or None if both image and overImage are None

	NOTE: this is effectively the same as doing blend(image,'normal',overImage,position,resize)

	IMPORTANT: the image bits may be altered.  To prevent this, set image.immutable=True
	"""
	if image==None:
		return overImage
	if overImage==None:
		if position==(0,0): # no change
			return image
		else:
			# create a blank background
			overImage=Image.new(maxMode(image,requireAlpha=True),(int(image.width+position[0]),int(image.height+position[1])))
	elif (image.width+position[0]>overImage.width) or (image.height+position[1]>overImage.height):
		# resize the overImage if necessary
		newImg=Image.new(
			size=(int(max(image.width+position[0],overImage.width)),int(max(image.height+position[1],overImage.height))),
			mode=maxMode(image,overImage,requireAlpha=True))
		paste(overImage,newImg)
		overImage=newImg
	elif hasattr(overImage,'immutable') and overImage.immutable==True:
		# if it is flagged immutable, create a copy that we are allowed to change
		overImage=overImage.copy()
	# do the deed
	if hasAlpha(image):
		# TODO: which of these two lines is best?
		#overImage.paste(image,position,image) # NOTE: (image,(x,y),alphaMask)
		if overImage.mode!=image.mode:
			overImage=overImage.convert(image.mode)
		overImage.alpha_composite(image,dest=(int(position[0]),int(position[1])))
	else:
		overImage.paste(image,(int(position[0]),int(position[1])))
	return overImage

	
def getSize(ofThis):
	"""
	get the xy size of something regardless of what kind it is
	
	:param ofThis: can be any of
		PIL image
		numpy array
		(w,h) or [w,h]
		(x,y,w,h) or [x,y,w,h]
		"w,h"
		anything derived from Bounds
	"""
	if type(ofThis) in [str,unicode]:
		return ofThis.split(',')[0:2]
	if type(ofThis) in [tuple,list]:
		if len(ofThis)==2:
			return [ofThis[-2],ofThis[-1]]	
	if type(ofThis)==np.ndarray:
		return [ofThis.shape[0]-1,ofThis.shape[1]-1]
	if isinstance(ofThis,Bounds):
		return bounds.size
	if isinstance(ofThis,Image.Image):
		return [ofThis.width,ofThis.height]
	return None

def makeSameSize(img1,img2,edge=(0,0,0,0)):
	"""
	pad the images with so they are the same size.  Commonly used for things like
	resizing before blending
	
	:param img1: first image
	:param img2: second image
	:param edge: defines how to extend.  It can be:
		mirror - reflect the pixels leading up to the border
		repeat - repeat the image over again (useful with repeating textures)
		clamp - streak last pixels out to edge
		[background color] - simply fill with the given color
		
	:return: (img1,img2)
	"""
	size1=getSize(img1)
	size2=getSize(img2)
	if size1[0]<size2[0] or size1[0]<size2[0]:
		img1=extendImageCanvas(img1,(max(size1[0],size2[0]),max(size1[1],size2[1])),edge)
	if size2[0]<size1[0] or size2[0]<size1[0]:
		img2=extendImageCanvas(img2,(max(size1[0],size2[0]),max(size1[1],size2[1])),edge)
	return img1,img2
	
	
def crop(img,size):
	"""
	crop an image to a given size
	
	:param size: can be anything that getSize() supports
	
	:returns: image of the cropped size (or smaller)
		can return None if selection is of zero size
	"""	
	region=None
	img=numpyArray(img)
	if (type(size) not in (list,tuple)) and (isinstance(size,np.ndarray)==False or len(size.shape)>1):
		size=getSize(size)
	imsize=getSize(img)
	size[0]=min(size[0],imsize[0])
	size[1]=min(size[1],imsize[1])
	if len(size)<4:
		if size[0]>0 and size[1]>0:
			region=img[0:size[0]+1,0:size[1]+1]
	else:
		# NOTE: slicing wants x2,y2 not w,h so there is a conversion here
		size[2]=min(size[2]+size[0],imsize[0])
		size[3]=min(size[1]+size[3],imsize[1])
		if size[2]>0 and size[3]>0:
			region=img[size[0]:size[2],size[1]:size[3]]
	return region
	

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
				elif arg[0]=='--border':
					thickness,border=arg[1].split(',',1)
					im=imageBorder(img,int(thickness),border)
					im.show()
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				img=defaultLoader(arg)
	if printhelp:
		print 'Usage:'
		print '  resizing.py [options]'
		print 'Options:'
		print '   --border=thickness,edge .. expand the image with a border - edge can be mirror,repeat,clamp,[color]'
		print 'Notes:'
		print '   * All filenames can also take file:// http:// https:// ftp:// urls'