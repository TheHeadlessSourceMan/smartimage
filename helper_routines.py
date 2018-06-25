#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This is a grab bag for handy helper routines
"""
import numpy as np
from PIL import Image


#-------------- numpy <-> PIL smart conversion

def numpyArray(img,floatingPoint=True):
	"""
	always return a writeable ndarray
	
	if img is a pil image, convert it.
	if it's already an array, return it
	
	:param img: can be a pil image or a numpy array
	:param floatingPoint: return a float array vs return a byte array
	"""
	if type(img)==np.ndarray:
		a=img
	else:
		a=np.asarray(img)
	if a.flags.writeable==False:
		a=a.copy()
	if isFloat(a)!=floatingPoint:
		if floatingPoint:
			a=a/255.0
		else:
			a=np.int(a*255)
	return a
	
	
def pilImage(a):
	"""
	converts a numpy array to a pil image
	
	:param a: can be a pil image or a numpy array
	"""
	l=len(a[0,0])
	if l==1:
		mode='L'
	elif l==2:
		mode='LA'
	elif l==3:
		mode='RGB'
	else:
		mode='RGBA'
	if isFloat(a):
		a=np.round(a*255)
	return Image.fromarray(a.astype('uint8'),mode)
	

#-------------- color mode/info

def imageMode(img):
	"""
	:param img: can either one be a textual image mode, numpy array, or an image
	
	:return bool:
	"""
	if type(img)==str:
		return img
	elif type(img)==np.ndarray:
		modeGuess=['L','LA','RGB','RGBA']
		return modeGuess[len(img[0,0])]
	return img.mode
	
	
def isFloat(img):
	"""
	Decide whether image pixels are floating point or byte
	
	:param img: can either one be a numpy array, or an image
	
	:return bool:
	"""
	if type(img)==np.ndarray:
		if type(img[0,0,0]) in [np.float,np.float64]:
			return True
	return False

	
def hasAlpha(imgMode):
	"""
	determine if an image mode is has an alpha channel
	
	:param imgMode: can either one be a textual image mode, numpy array, or an image
	:return bool:
	"""
	if type(imgMode)!=str:
		if type(img)==np.ndarray:
			return len(img[0,0]) in [2,4] # 'LA' or 'RGBA'
		else:
			imgMode=imgMode.mode
	return imgMode[-1]=='A'


def isColor(imgMode):
	"""
	determine if an image mode is color (or grayscale)
	
	:param imgMode: can either one be a textual image mode, numpy array, or an image
	:return bool:
	"""
	if type(imgMode)!=str:
		if type(img)==np.ndarray:
			return len(img[0,0])>2
		else:
			imgMode=imgMode.mode
	return imgMode[0]!='L'
	
	
def maxMode(mode1,mode2='L',requireAlpha=False):
	"""
	Finds the maximum color mode.

	:param mode1: can either one be a textual image mode, numpy array, or an image
	:param mode2: can either one be a textual image mode, numpy array, or an image
	:param requireAlpha: stipulate that the result must have an alpha channel

	:return mode: best image mode
	"""
	if isColor(mode1) or isColor(mode2):
		ret='RGB'
	else:
		ret='L'
	if requireAlpha or hasAlpha(mode1) or hasAlpha(mode2):
		ret=ret+'A'
	return ret

	
#------------------- convert to other color representations
	
def rgb2hsvImage(img):
	"""
	same as rgb2hsvArray only returns an image
	
	:param img: image to convert.  can be pil image or numpy array
	
	:return img: returns an "rgb" image, that is actually "hsv"
	"""
	return pilImage(rgb2hsvArray(rgb))
	
	
def rgb2hsvArray(rgb):
	"""
	Transform an rgb array to an hsv array
	
	:param rgb: the input image.  can be pil image or numpy array
	:return hsv: the output array
	
	This comes from scikit-image:
		https://github.com/scikit-image/scikit-image/blob/master/skimage/color/colorconv.py
	"""
	rgb=numpyArray(rgb)
	out = np.empty_like(rgb)
	# -- V channel
	out_v = rgb.max(-1)
	# -- S channel
	delta = rgb.ptp(-1)
	# Ignore warning for zero divided by zero
	old_settings = np.seterr(invalid='ignore')
	out_s = delta / out_v
	out_s[delta == 0.] = 0.
	# -- H channel
	# red is max
	idx = (rgb[:, :, 0] == out_v)
	out[idx, 0] = (rgb[idx, 1] - rgb[idx, 2]) / delta[idx]
	# green is max
	idx = (rgb[:, :, 1] == out_v)
	out[idx, 0] = 2. + (rgb[idx, 2] - rgb[idx, 0]) / delta[idx]
	# blue is max
	idx = (rgb[:, :, 2] == out_v)
	out[idx, 0] = 4. + (rgb[idx, 0] - rgb[idx, 1]) / delta[idx]
	out_h = (out[:, :, 0] / 6.) % 1.
	out_h[delta == 0.] = 0.
	np.seterr(**old_settings)
	# -- output
	out[:, :, 0] = out_h
	out[:, :, 1] = out_s
	out[:, :, 2] = out_v
	# remove NaN
	out[np.isnan(out)] = 0
	return out

	
def hsv2rgbImage(img):
	"""
	same as rgb2hsvArray only returns an image
	
	:param img: image to convert.  can be pil image or numpy array
	
	:return img: returns an "rgb" image, that is actually "hsv"
	"""
	return pilImage(hsv2rgbArray(rgb))
	

def hsv2rgbArray(hsv):
	"""
	Transform an hsv image to an rgb array
	
	:param hsv: the input image.  can be pil image or numpy array
	:return rgb: the output array
	
	This comes from scikit-image:
		https://github.com/scikit-image/scikit-image/blob/master/skimage/color/colorconv.py
	"""
	hsv=numpyArray(hsv)
	hi = np.floor(hsv[:, :, 0] * 6)
	f = hsv[:, :, 0] * 6 - hi
	p = hsv[:, :, 2] * (1 - hsv[:, :, 1])
	q = hsv[:, :, 2] * (1 - f * hsv[:, :, 1])
	t = hsv[:, :, 2] * (1 - (1 - f) * hsv[:, :, 1])
	v = hsv[:, :, 2]
	hi = np.dstack([hi, hi, hi]).astype(np.uint8) % 6
	out = np.choose(hi, [np.dstack((v, t, p)),
		 np.dstack((q, v, p)),
		 np.dstack((p, v, t)),
		 np.dstack((p, q, v)),
		 np.dstack((t, p, v)),
		 np.dstack((v, p, q))])
	return out
	
	
def rgb2cmykImage(img):
	"""
	same as rgb2cmykArray only takes an image and returns an image
	
	:param img: image to convert
	
	:return img: returns an "rgba" image, that is actually "cmyk"
	"""
	rgb=numpyArray(img)
	final=rgb2cmykArray(rgb)
	return pilImage(final)
	
	
def getChannel(img,channel):
	"""
	get a channel as a new image.
	
	:param img: the image to extract a color channel from
	:param channel: name of the channel to extract - supports R,G,B,A,H,S,V
	
	Returns a grayscale image, or None
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
	
	
def clampImage(img,minimum=None,maximum=None):
	"""
	Clamp an image's pixel to a valid color range
	
	:param img: clamp a numpy image to valid pixel values can be a PIL image for "do nothing"
	:param minimum: minimum value to clamp to (default is 0)
	:param maximum: maximum value to clamp to (default is the maximum pixel value)
	"""
	if type(img)!=np.ndarray:
		if minimum!=None and minimum!=0 and maximum!=None and maximum!=255:
			return img
		img=numpyArray(img,type(maximum)==float)
	if isFloat(img):
		if minimum==None:
			minimum=0.0
		if maximum==None:
			maximum=1.0
	else:
		if minimum==None:
			minimum=0
		if maximum==None:
			maximum=255
	return np.clip(img,minimum,maximum)
	
#------------------------ image size manipulation


def imageBorder(img,thickness,edge="#ffffff00"):
	"""
	Add a border of thickness pixels around the image

	:param img: the image to add a border to
	:param thickness: the border thickness in pixels
	:param edge: defines how to extend.  It can be:
		mirror - reflect the pixels leading up to the border
		repeat - repeat the image over again (useful with repeating textures)
		clamp - streak last pixels out to edge
		[background color] - simply fill with the given color
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
	

#------------------ histograms


def getHistogram(img,channel='V',invert=False):
	"""
	Gets a histogram for the given image
	
	:param channel: can be V,R,G,B,A, or RGB
		if single channel, returns a simple black and white image
		if RGB, returns all three layered together in a color image
	:param invert: do a white histogram on black, rather than the usual black on white
		
	:return pilImage: always grayscale, unless RGB, then an RGB image with each channel as its name
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
	
	
#------------------ main entry point for external fun


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
		print '  helper_routines.py image.jpg [options]'
		print 'Options:'
		print '   --histogram[=RGB] ........ possible values are V,R,G,B,A,or RGB'
		print '   --channel=R .............. extract a channel from the image - R,G,B,A,H,S,V'
		print '   --border=thickness,edge .. expand the image with a border - edge can be mirror,repeat,clamp,[color]'