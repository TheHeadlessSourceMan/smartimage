#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
The base class for image layers
"""
from PIL import Image
from imgTools import *
from xmlBackedObject import *
from imgTools import *
import math


class RenderingContext(object):
	"""
	Used to keep track of atributes while rendering an image from layers
	and also a box to keep utility functions in.
	"""
	def __init__(self,initialLayer):
		self.desired=Bounds(0,0,0,0)
		self.cur_rot=0
		self.cur=Bounds(0,0,0,0)
		self.cur_image=None
		self.visitedLayers={}
		self.variableContexts=[] # an array of dicts
		
	def getVariableValue(self,name):
		for contextId in range(len(self.variableContexts),0):
			if name in variableContexts[contextId]:
				return variableContexts[contextId][name]
		return None
		
	def setVariableValue(self,name,value):
		self.variableContexts[-1][name]=value

	def log(self,*vals):
		print (' '*len(self.visitedLayers))+(' '.join([str(v) for v in vals]))

	def _setLocation(self,x,y,absolute=False):
		"""
		Set the location indicator.

		:param x: x location
		:param y: y location
		:param absolute: absolute or relative to current position
		"""
		if absolute:
			self.cur_x=x
			self.cur_y=y
		else:
			self.cur_x+=x
			self.cur_y+=y

   	def renderImage(self,layer):
		"""
		render an image from the layer image and all of its children

		WARNING: Do not modify the image without doing a .copy() first!
		"""
		# loop prevention
		if layer in self.visitedLayers:
			raise Exception('ERR: Link loop with layer '+str(layer.id)+' "'+layer.name+'"')
		self.visitedLayers[layer]=True
		# push a new variable context
		self.variableContexts.append({})
		# do we need to do anything?
		opacity=layer.opacity
		if opacity<=0.0 or layer.visible==False:
			self.log('skipping',layer.name)
			del self.visitedLayers[layer]
			return None
		self.log('creating',layer.name)
		image=layer.image
		for childLayer in layer.children:
			childImage=childLayer.renderImage(self)
			image=composite(childImage,image,
				opacity=childLayer.opacity,blendMode=childLayer.blendMode,mask=childLayer.mask,
				position=childLayer.location,resize=True)
			self.log('adding',childLayer.name,'at',childLayer.location)
		if layer.crop!=None:
			image=image.crop(layer.crop)
		if layer.rotate%360!=0:
			self.log('rotating',layer.name)
			bounds=Bounds(0,0,image.width,image.height)
			bounds.rotateFit(layer.rotate)
			image=extendImageCanvas(image,bounds)
			image=image.rotate(layer.rotate)
		# logging
		if image==None:
			self.log('info',layer.name,'NULL IMAGE')
		else:
			self.log('info',layer.name,'mode='+image.mode,'bounds='+str((0,0,image.width,image.height)))
		self.log('finished',layer.name)
		# pop off tracking info for this layer
		del self.visitedLayers[layer]
		del self.variableContexts[-1]
		return image


class Layer(XmlBackedObject,PilPlusImage):
	"""
	The base class for image layers
	"""
	def __init__(self,docRoot,parent,xml):
		XmlBackedObject.__init__(self,docRoot,parent,xml)
		self.parent=parent
		self._lastRenderedImage=None

	def __repr__(self):
		name=self.name
		if len(name)>0:
			return 'Layer '+str(self.id)+' - "'+name+'"'
		return 'Layer '+str(self.id)

	def getLayer(self,id):
		l=None
		if self.id==id:
			l=self
		else:
			for c in self.children:
				l=c.getLayer(id)
				if l!=None:
					break
		return l

	@property
	def x(self):
		"""
		if value=="auto", then take on the child value
		"""
		x=self._getProperty('x','auto')
		if x=='auto':
			x=[child.x for child in self.children]
			if len(x)>0:
				x=min(x)
			else:
				x=0
		else:
			x=float(x)
			if x<0:
				x=self.w+x
		return x
	@property
	def y(self):
		"""
		if value=="auto", then take on the child value
		"""
		y=self._getProperty('y','auto')
		if y=='auto':
			y=[child.y for child in self.children]
			if len(y)>0:
				y=min(y)
			else:
				y=0
		else:
			y=float(y)
			if y<0:
				y=self.w+y
		return y
	@property
	def w(self):
		w=self._getProperty('w','auto')
		if w in ['0','auto']:
			if len(self.children)>0:
				w=[child.x+child.w for child in self.children]
				w=max(w)-self.x
			else:
				w=0
		else:
			w=float(w)
		return w
	@property
	def h(self):
		h=self._getProperty('h','auto')
		if h in ['0','auto']:
			if len(self.children)>0:
				h=[child.y+child.h for child in self.children]
				h=max(h)-self.y
			else:
				h=0
		else:
			h=float(h)
		return h

	@property
	def visible(self):
		return self._getProperty('visible','y')[0] in ['y','Y','t','T','1']
		
	@property
	def detatched(self):
		return self._getProperty('detatched','n')[0] in ['y','Y','t','T','1']
		
	@property
	def crop(self):
		return self._getPropertyArray('crop',None)

	@property
	def rotate(self):
		return float(self._getProperty('rotate','0'))
		
	@property
	def relativeTo(self):
		# TODO: dimensions need to account for this!
		return self._getProperty('relativeTo','parent')

	@property
	def name(self):
		ret=self._getProperty('name')
		if ret==None:
			ret='Layer '+str(self.id)
		return ret

	@property
	def opacity(self):
		return self._getPropertyPercent('opacity',1.0)

	@property
	def blendMode(self):
		"""
		available: (from imagechops module)
			'normal','darker','difference','add','add_mod','multiply','and','or','screen','subtract','subtract_mod'
		"""
		return self._getProperty('blendMode','normal')

	def _createChild(self,doc,parent,xml):
		child=None
		if xml==self.xml or xml.__class__.__name__ in ['_Comment']:
			pass
		elif xml.tag in ['variable','form']:
			# form elements do not belong to an image
			pass
		elif xml.tag=='text':
			import text
			child=text.TextLayer(doc,parent,xml)
		elif xml.tag=='link':
			import link
			child=link.Link(doc,parent,xml)
		elif xml.tag=='image':
			import image
			child=image.ImageLayer(doc,parent,xml)
		elif xml.tag=='group':
			child=Layer(doc,parent,xml)
		elif xml.tag=='modifier':
			import modifier
			child=modifier.Modifier(doc,parent,xml)
		elif xml.tag=='solid':
			import solid
			child=solid.Solid(doc,parent,xml)
		elif xml.tag=='texture':
			import texture
			child=texture.Texture(doc,parent,xml)
		elif xml.tag=='pattern':
			import pattern
			child=pattern.Pattern(doc,parent,xml)
		elif xml.tag=='particles':
			import particles
			child=particles.Particles(doc,parent,xml)
		elif xml.tag=='ext':
			import extension
			child=extension.Extension(doc,parent,xml)
		else:
			raise Exception('ERR: unknown element, "'+xml.tag+'"')
		return child

	@property
	def children(self):
		"""
		"""
		if self._children==None:
			self._children=[]
			# NOTE: this loop is reversed so that the xml file has top layers first
			# (visually on top in an editor) like what we're used to in a gui like GIMP.
			for tag in reversed([c for c in self.xml.iterchildren()]):
				child=self._createChild(self.docRoot,self,tag)
				if child!=None:
					self._children.append(child)
		return self._children

	@property
	def roi(self):
		"""
		"region of interest" used for smart resizing and possibly other things
		"""
		#return Image.new('L',(int(self.w),int(self.h)),0)
		ref=self._getProperty('roi')
		return self.docRoot.imageByRef(ref)
		
	@property
	def normalMap(self):
		"""
		A 3d normal map, wherein red=X, green=Y, blue=Z (facing directly out from the screen)
		"""
		ref=self._getProperty('normalMap',None)
		if ref==None:
			ref=normalMapFromImage(self.image)
		return self.docRoot.imageByRef(ref)
		
	@property
	def bumpMap(self):
		"""
		a grayscale bump map or heightmap.
		"""
		ref=self._getProperty('bumpMap',None)
		if ref==None:
			ref=heightMapFromNormalMap(self.normalMap)
		return self.docRoot.imageByRef(ref)
		
	def compareOutput(self,compareTo,tolerance=0.99999):
		rendered=self.renderImage()
		return compareImage(rendered,compareTo,tolerance)

	@property
	def image(self):
		"""
		Implemented by child classes
		"""
		return None

	@property
	def mask(self):
		"""
		grayscale image to be used as layer mask
		it can also be an image with alpha component which will be INVERTED to use as mask!

		NOTE: the mask can either be a link to another file,
		"""
		ref=self._getProperty('mask')
		img=self.docRoot.imageByRef(ref)
		if img!=None:
			if img.mode in ['RGBA','LA']:
				alpha=img.split()[-1]
				img=Image.new("RGBA",img.size,(0,0,0,255))
				img.paste(alpha,mask=alpha)
			img=img.convert("L")
		return img

	def renderImage(self,renderContext=None):
		"""
		render this layer to a final image

		renderContext - used to keep track for child renders
			(Used internally, so no need to specify this)

		WARNING: Do not modify the image without doing a .copy() first!
		"""
		if self.docRoot.cacheRenderedLayers and self.dirtyBranch==False and self._lastRenderedImage!=None:
			return self._lastRenderedImage
		if renderContext==None:
			renderContext=RenderingContext(self)
		ret=renderContext.renderImage(self)
		if self.docRoot.cacheRenderedLayers:
			self._lastRenderedImage=ret
		return ret

	@property
	def finalRoi(self):
		"""
		self.roi only with all children applied
		"""
		image=self.roi
		for c in self.children:
			image=ImageChops.add(image,c.finalRoi)
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
		print '  layer.py [options]'
		print 'Options:'
		print '   NONE'