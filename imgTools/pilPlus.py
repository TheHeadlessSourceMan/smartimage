#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This is an experimental extension of PIL images allowing advanced access
"""
try:
	# first try to use bohrium, since it could help us accelerate
	# https://bohrium.readthedocs.io/users/python/
	import bohrium as np
except ImportError:
	# if not, plain old numpy is good enough
	import numpy as np
from PIL import Image
from bounds import Bounds
from colorSpaces import *


class PilPlusImage(Image.Image,Bounds):
	"""
	This is an experimental extension of PIL images allowing advanced access
	"""

	def __init__(self,image=None):
		Image.Image.__init__(self)
		Bounds.__init__(self)
		self._activeChannels={}
		self._image=None
		self.imageLoader=None
		if image!=None:
			self.image=image

	def getChannel(self,id):
		"""
		get a channel in floating point form
		"""
		if id not in self._activeChannels:
			if id in ['r','g','b'] or (id=='a' and len(self._activeChannels)<2):
				if 'v' in self._activeChannels:
					return self._activeChannels['v']
				else:
					res=numpyArray(self.image,floatingPoint=True,loader=None)
					if len(res.size)<3: # L
						self._activeChannels['v']=res
						return self._activeChannels['v']
					elif res.size[2]==2: # LA
						self._activeChannels['v']=res[:,:,0]
						self._activeChannels['a']=res[:,:,1]
					elif res.size[2]==3: # RGB
						self._activeChannels['r']=res[:,:,0]
						self._activeChannels['g']=res[:,:,1]
						self._activeChannels['b']=res[:,:,2]
					elif res.size[2]==3: # RGBA
						self._activeChannels['r']=res[:,:,0]
						self._activeChannels['g']=res[:,:,1]
						self._activeChannels['b']=res[:,:,2]
						self._activeChannels['a']=res[:,:,3]
			elif id=='a':
				ret=np.array(self.image.size())
				ret.fill(1.0)
				self._activeChannels['a']=ret
				return ret
		return self._activeChannels[id]

	def grayscale(self,method='BT.709'):
		"""
		Convert to grayscale

		:param method: available are:
			"max" - max of all channels
			"min" - min of all channels
			"avg" - average of all channels
			"HSV" or "median" - average of max and min
			"ps-gimp" - weighted average used by most image applications
			"BT.709" - [default] weighted average specified by ITU-R "luma" specification BT.709
			"BT.601" - weighted average specified by ITU-R specification BT.601 used by video formats

		NOTE:
			There are many different ways to go about this.
			http://www.tannerhelland.com/3643/grayscale-image-algorithm-vb6/
		"""
		return grayscale(self.image,method)

	@property
	def image(self):
		"""
		get the wrapped image
		"""
		return self._image
	@image.setter
	def image(self,image):
		"""
		set the wrapped image
		"""
		self._activeChannels={}
		if isinstance(image,PilPlusImage):
			self._image=image.image
		else:
			self._image=pilImage(image,loader=self.imageLoader)

	def assign(self,sizeOrImage):
		"""
		assign this image to another image, or a certain size
		"""
		if type(sizeOrImage) in [list,tuple] and len(sizeOrImage) in [2,4]:
			Bounds.assign(self,sizeOrImage)
		elif isinstance(sizeOrImage,Bounds) and not isinstance(sizeOrImage,PilPlusImage):
			Bounds.assign(self,sizeOrImage)
		else:
			self.image=sizeOrImage

	def __repr__(self):
		return 'Image '+str(self.bounds)+' mode:'+self.mode+' source:'+str(self.filename)

	@property
	def R(self):
		return self.getChannel('r')
	@property
	def G(self):
		return self.getChannel('g')
	@property
	def B(self):
		return self.getChannel('b')
	@property
	def A(self):
		return self.getChannel('a')
	@property
	def mask(self):
		return self.getChannel('a')

	# ----- implement PIL image routines so that we can use this directly as an image
	def alpha_composite(self,*args):
		return self.image.alpha_composite(*args)
	def category(self,*args):
		return self.image.category(*args)
	def close(self,*args):
		return self.image.close(*args)
	def convert(self,*args):
		return self.image.convert(*args)
	def copy(self,*args):
		return self.image.copy(*args)
	def crop(self,*args):
		return self.image.crop(*args)
	def draft(self,*args):
		return self.image.draft(*args)
	def effect_spread(self,*args):
		return self.image.effect_spread(*args)
	def filter(self,*args):
		return self.image.filter(*args)
	def format(self,*args):
		return self.image.format(*args)
	def format_description(self,*args):
		return self.image.format_description(*args)
	def frombytes(self,*args):
		return self.image.frombytes(*args)
	def fromstring(self,*args):
		return self.image.fromstring(*args)
	def getbands(self,*args):
		return self.image.getbands(*args)
	def getbbox(self,*args):
		return self.image.getbbox(*args)
	def getchannel(self,*args):
		return self.image.getchannel(*args)
	def getcolors(self,*args):
		return self.image.getcolors(*args)
	def getdata(self,*args):
		return self.image.getdata(*args)
	def getextrema(self,*args):
		return self.image.getextrema(*args)
	def getim(self,*args):
		return self.image.getim(*args)
	def getpalette(self,*args):
		return self.image.getpalette(*args)
	def getpixel(self,*args):
		return self.image.getpixel(*args)
	def getprojection(self,*args):
		return self.image.getprojection(*args)
	#def height(self,*args): # get from bounds
	#	return self.image.height(*args)
	def histogram(self,*args):
		return self.image.histogram(*args)
	def im(self,*args):
		return self.image.im(*args)
	def info(self,*args):
		return self.image.info(*args)
	def load(self,*args):
		return self.image.load(*args)
	def mode(self,*args):
		return self.image.mode(*args)
	#def offset(self,*args): # get from bounds
	#	return self.image.offset(*args)
	def palette(self,*args):
		return self.image.palette(*args)
	def paste(self,*args):
		return self.image.paste(*args)
	def point(self,*args):
		return self.image.point(*args)
	def putalpha(self,*args):
		return self.image.putalpha(*args)
	def putdata(self,*args):
		return self.image.putdata(*args)
	def putpalette(self,*args):
		return self.image.putpalette(*args)
	def putpixel(self,*args):
		return self.image.putpixel(*args)
	def pyaccess(self,*args):
		return self.image.pyaccess(*args)
	def quantize(self,*args):
		return self.image.quantize(*args)
	def readonly(self,*args):
		return self.image.readonly(*args)
	def remap_palette(self,*args):
		return self.image.remap_palette(*args)
	def resize(self,*args):
		return self.image.resize(*args)
	def rotate(self,*args):
		return self.image.rotate(*args)
	def save(self,*args):
		return self.image.save(*args)
	def seek(self,*args):
		return self.image.seek(*args)
	def show(self,*args):
		return self.image.show(*args)
	#def size(self,*args): # get from bounds
	#	return self.image.size(*args)
	def split(self,*args):
		return self.image.split(*args)
	def tell(self,*args):
		return self.image.tell(*args)
	def thumbnail(self,*args):
		return self.image.thumbnail(*args)
	def tobitmap(self,*args):
		return self.image.tobitmap(*args)
	def tobytes(self,*args):
		return self.image.tobytes(*args)
	def toqimage(self,*args):
		return self.image.toqimage(*args)
	def toqpixmap(self,*args):
		return self.image.toqpixmap(*args)
	def tostring(self,*args):
		return self.image.tostring(*args)
	def transform(self,*args):
		return self.image.transform(*args)
	def transpose(self,*args):
		return self.image.transpose(*args)
	def verify(self,*args):
		return self.image.verify(*args)
	#def width(self,*args): # get from bounds
	#	return self.image.width(*args)


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
		print '  pilPlus.py [options]'
		print 'Options:'
		print '   NONE'
