#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This is a grab bag for handy helper routines
"""
import numpy as np
from PIL import Image


#-------------- numpy <-> PIL smart conversion

def defaultLoader(f):
	"""
	load an image from a file-like object, filename, or url of type
		file://
		ftp://
		sftp://
		http://
		https://
	"""
	if isinstance(f,np.ndarray) or isinstance(f,Image.Image):
		return f
	if type(f) in [str,unicode]:
		proto=f.split('://',1)
		if len(proto)>2 and proto.find('/')<0:
			if proto[0]=='file':	
				f=proto[-1]
				if os.sep!='/':
					f=f.replace('/',os.sep)
					if f[1]=='|':
						f[1]=':'
			else:
				proto=proto[1]
		else:
			proto='file'
		if proto!='file':
			import urllib2,cStringIO
			headers={'User-Agent':'Mozilla 5.10'} # some servers only like "real browsers"
			request=urllib2.Request(f,None,headers)
			response=urllib2.urlopen(request)
			f=cStringIO.StringIO(response.read())
	return Image.open(f)

def numpyArray(img,floatingPoint=True,loader=None):
	"""
	always return a writeable ndarray
	
	if img is a pil image, convert it.
	if it's already an array, return it
	
	:param img: can be a pil image, a numpy array, or anything loader can load
	:param floatingPoint: return a float array vs return a byte array
	:param loader: return a tool used to load images from strings.  if None, use defaultLoader() in this file
	"""
	if type(img) in [str,unicode] or hasattr(img,'read'):
		if loader==None:
			loader=defaultLoader
		img=loader(img)
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
	mode=imageMode(a)
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
		if len(img.shape)<3: # black and white is [x,y,val] not [x,y,[val]]
			return 'L'
		modeGuess=['L','LA','RGB','RGBA']
		return modeGuess[img.shape[2]-1]
	return img.mode
	
	
def isFloat(img):
	"""
	Decide whether image pixels are floating point or byte
	
	:param img: can either one be a numpy array, or an image
	
	:return bool:
	"""
	if type(img)==np.ndarray:
		if len(img.shape)<3: # black and white is [x,y,val] not [x,y,[val]]
			if type(img[0,0]) in [np.float,np.float64]:
				return True
		else:
			if type(img[0,0,0]) in [np.float,np.float64]:
				return True
	return False

	
def hasAlpha(mode):
	"""
	determine if an image mode is has an alpha channel
	
	:param mode: can either one be a textual image mode, numpy array, or an image
	:return bool:
	"""
	if type(mode)!=str:
		mode=imageMode(mode)
	return mode[-1]=='A'


def isColor(mode):
	"""
	determine if an image mode is color (or grayscale)
	
	:param mode: can either one be a textual image mode, numpy array, or an image
	:return bool:
	"""
	if type(mode)!=str:
		mode=imageMode(mode)
	return mode[0]!='L'
	
	
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

	
def changeMode(img,mode):
	"""
	changes the image to a different color mode
	"""
	curmode=imageMode(img)
	if curmode!=mode:
		if type(img)==np.ndarray:
			# TODO: this would be faster to do in array-land, but I'm too lazy to 
			#	mess with the if/then spaghetti required for that.
			img=pilImage(img)
			
			img=img.convert(mode)
		else:
			img=img.convert(mode)
	return img
	
	
def makeSameMode(images):
	"""
	takes an array of images, returns an array of images
	converts all into the max image mode of all images in the list
	"""
	maxmode='L'
	modeDifferences=False
	for i in range(len(images)):
		if i==0:
			maxmode=imageMode(images[i])
		else:
			mode=imageMode(images[i])
			if mode!=maxmode:
				modeDifferences=True
				maxmode=maxMode(maxmode,mode)
	if modeDifferences:
		images=[changeMode(img,maxmode) for img in images]
	return images
	
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
	

def rgb2cmykArray(rgb):
	"""
	Takes [[[r,g,b]]] colors in range 0..1
	Returns [[[c,m,y,k]]] in range 0..1
	"""
	k=rgb.sum(-1)
	c = 1.0 - rgb[:,:,0]
	m = 1.0 - rgb[:,:,1]
	y = 1.0 - rgb[:,:,2]
	minCMY=np.dstack((c,m,y)).min(-1)
	c = (c - minCMY) / (1.0 - minCMY)
	m = (m - minCMY) / (1.0 - minCMY)
	y = (y - minCMY) / (1.0 - minCMY)
	k = minCMY
	cmyk=np.dstack((c,m,y,k))
	return cmyk
	
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
	
	
#------------------ compare images (useful for automated testing)

def compareImage(img1,img2,tolerance=0.99999):
	"""
	images can be a pil image, rgb numpy array, url, or filename
	tolerance - a decimal percent, default is five-nines
	"""
	img1,img2=makeSameMode([defaultLoader(img1),defaultLoader(img2)])
	img1,img2=numpyArray(img1),numpyArray(img2)
	if img1.shape!=img2.shape:
		# if they're not even the same size, never mind, then
		return False
	return np.allclose(img1,img2,rtol=tolerance)
	
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
				elif arg[0]=='--compare':
					print compareImage(img,arg[1])
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				img=defaultLoader(arg)
	if printhelp:
		print 'Usage:'
		print '  helper_routines.py image.jpg [options]'
		print 'Options:'
		print '   --histogram[=RGB] ........ possible values are V,R,G,B,A,or RGB'
		print '   --channel=R .............. extract a channel from the image - R,G,B,A,H,S,V'
		print '   --border=thickness,edge .. expand the image with a border - edge can be mirror,repeat,clamp,[color]'
		print '   --compare=img2.jpg ....... compares to another image (useful for testing)'
		print 'Notes:'
		print '   * All filenames can also take file:// http:// https:// ftp:// urls'