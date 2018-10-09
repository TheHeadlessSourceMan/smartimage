#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This program allows an image to behave smartly and automatically
"""
import os
import zipfile
try:
	# first try to use bohrium, since it could help us accelerate
	# https://bohrium.readthedocs.io/users/python/
	import bohrium as np
except ImportError:
	# if not, plain old numpy is good enough
	import numpy as np
import lxml.etree
from PIL import ImageDraw
from layer import *
from form import Form


class SmartImage(Layer):
	"""
	This program allows an image to behave smartly and automatically

	The object acts as an array of pages/frames (array of 1 if it's just a simple image)
	"""

	def __init__(self,filename=None,xmlName='smartimage.xml',topSmartimage=None):
		Layer.__init__(self,self,None,None)
		self._hasRunUi=False
		self._nextId=None
		self._variables=None
		self._varAuto=[]
		self._zipfile=None
		if topSmartimage is None:
			# we are the top, so we'll take care of the peer list
			# (otherwise, we'll access self._topSmartimage._peerSmartimages)
			self._peerSmartimages={}
		if topSmartimage is None:
			self._topSmartimage=self
		else:
			self._topSmartimage=topSmartimage
		self.autoUi=True
		self.load(filename,xmlName)
		self.cacheRenderedLayers=True # trade memory for speed

	# TODO: remove?
	@property
	def variables(self):
		"""
		get the state of all variables in play
		"""
		f=self.form
		if f is None:
			return []
		return f.children
		# if self._variables==None:
			# self._variables=OrderedDict()
			# for variable in self.xml.xpath('//*/variable'):
				# variable=Variable(self,self,variable)
				# self._variables[variable.name]=variable
		# return self._variables

	@property
	def form(self):
		"""
		get the main ui form of this document
		"""
		for f in self.forms:
			if not f.hidden:
				return f
		return None

	@property
	def forms(self):
		"""
		get all of the forms in this document
		"""
		forms=self.xml.xpath('//*/form')
		ret=[]
		for form in forms:
			ret.append(Form(self,None,form))
		return ret

	@property
	def numPages(self):
		"""
		how many pages are in the animation
		"""
		return len(self.xml.xpath('//*/page'))

	@property
	def numFrames(self):
		"""
		how many frames are in the animation
		"""
		return len(self.xml.xpath('//*/frame'))

	@property
	def page(self,pageNumber):
		"""
		if this is a multipage document, get the given page number
		"""
		pages=self.xml.xpath('//*/page')
		if len(pages)<=0 and pageNumber==0:
			return self
		return pages[pageNumber]

	@property
	def frame(self,frameNumber):
		"""
		if this is an animation, get a given frame number
		"""
		frames=self.xml.xpath('//*/frame')
		return frames[rameNumber]

	def __len__(self):
		p=self.numPages
		f=self.numFrames
		if p>1:
			if f>1:
				raise Exception("File cannot contain both pages and frames!")
			return p
		if f>1:
			return f
		return 1

	def __getitem__(self,idxOrSlice):
		ret=None
		p=self.numPages
		f=self.numFrames
		if f==0 and p==0:
			return self
		elif isinstance(idxOrSlice,tuple): # it's a slice
			start,end=idxOrSlice
			if start<0:
				start+=self.__len__()
			if end<0:
				end+=self.__len__()
			ret=[]
			if f>p:
				for idx in range(start,end):
					ret.append(self.frame[idx])
			else:
				for idx in range(start,end):
					ret.append(self.page[idx])
		else:
			if f>p:
				ret=self.frame[idxOrSlice]
			else:
				ret=self.page[idxOrSlice]
		return ret

	def getComponent(self,name):
		"""
		returns a file-like object for the given name
		"""
		if os.path.isdir(self.filename):
			filename=os.path.join(self.filename,name)
			f=open(filename,'rb')
		elif self.filename.endswith(os.sep+'smartimage.xml'):
			filename=os.path.join(self.filename.rsplit(os.sep,1)[0],name)
			f=open(filename,'rb')
		else:
			if self._zipfile is None:
				self._zipfile=zipfile.ZipFile(self.filename)
			f=self._zipfile.open(name)
		return f

	def getPeerSmartimage(self,xmlName):
		"""
		get another smartimage .xml embedded in this file
		"""
		while xmlName[0]=='@':
			xmlName=xmlName[1:]
		xmlName=xmlName.split('.')[0]+'.xml'
		peerSmartimages=self._topSmartimage._peerSmartimages
		if xmlName not in peerSmartimages:
			self._peerSmartimages[xmlName]=SmartImage(self.filename,xmlName,self._topSmartimage)
		return peerSmartimages[xmlName]

	def getItemByFilename(self,name,nameHint='',nofollow=None):
		"""
		get an item that resides in another smartimage

		:param name: should be something like:
			@filename.xml.itemId
			@filename.xml.name
			@filename.itemId
			@subfolder/filename.itemId
		:param nameHint: used as a default when getting attributes
			such as <image file="@layerId"> means <image file="@layerId.result"> (wherein nameHint="result")
		:param nofollow: used internally to prevent loops

		:return: the item object or None if not found
		"""
		item=None
		if nofollow is None:
			nofollow=[]
		while name[0]=='@':
			name=name[1:]
		name=name.split('.')
		if len(name)>1 and name[1]=='xml': # they included the file extension
			filename=name[0]
			if name>2:
				name='.'.join(name[2:])
			else:
				name=''
		else: # they did not include the file extension
			filename=name[0]
			if name>1:
				name='.'.join(name[1:])
			else:
				name=''
		sImg=self.getPeerSmartimage(filename)
		if sImg!=None:
			item=sImg._dereference(name,nameHint,nofollow=nofollow)
		return item

	def getNextId(self,rescan=False):
		"""
		take the next unused id number
		"""
		if self._nextId is None:
			data=self.getComponent('smartimage.xml').read()
			first=True
			maxid=1
			for id in data.split('id="'):
				if first:
					first=False
				else:
					try:
						id=int(id.split('"',1)[0])
						if id>maxid:
							maxid=id
					except ValueError: # if the id is not an integer
						pass
			self._nextId=maxid+1
		id=self._nextId
		self._nextId+=1
		#print 'GENERATED ID:',id
		return id

	def imageByRef(self,ref,visitedLayers=None):
		"""
		grab an image by reference
		ref - one of:
			filename
			#id

		WARNING: Do not modify the image without doing a .copy() first!
		"""
		if visitedLayers is None:
			visitedLayers=[]
		if ref is None:
			return None
		if ref.startswith('@'):
			l=self.getLayer(ref[1:])
			if l is None:
				raise Exception('ERR: Missing reference to "'+ref+'"')
			return l.renderImage()
		return Image.open(self.docRoot.getComponent(ref),'r')

	@property
	def componentNames(self):
		"""
		get the names of the components in this file
		"""
		ret=[]
		if os.path.isdir(self.filename):
			ret.extend(os.listdir(self.filename))
		else:
			if self._zipfile is None:
				self._zipfile=zipfile.ZipFile(self.filename)
			ret.extend(self._zipfile.namelist())
		return ret

	@property
	def xml(self):
		"""
		get the xml tree of the smartimage
		"""
		if self._xml is None:
			self._xml=lxml.etree.parse(self.getComponent('smartimage.xml'))
		return self._xml.getroot()

	def write(self,image,text,xy,align=None,font=None):
		"""
		Write text on the image

		:param image: the image to write on
		:param xy: the point to write
		:param align: how to align the text
		:param font: the name of the font to use
		"""
		if font!=None:
			self.setFont(font)
		if align!=None:
			self.textAlignment=align
		draw=ImageDraw.Draw(image)
		draw.multiline_text(xy,text,None,self.currentFont,anchor=None,spacing=self.lineSpacing,align=self.textAlignment)

	def load(self,filename,xmlName='smartimage.xml'):
		"""
		load an image

		:param filename: the name of the file to load
		:param xmlName: the name of the starting smartimage within the file
		"""
		self._xml=None
		self._zipfile=None
		self.currentFont=None
		self.lineSpacing=0
		self.textAlignment='left'
		self.filename=filename
		self.xmlName=xmlName

	def save(self,filename=None):
		"""
		Save this image.

		If the filename is something other than a smartimage
		(eg. a .png file) then will save the rendered output.

		:param filename: the filename to save.  If unspecified,
			save as the currently loaded filename
		"""
		self.varUi(force=False)
		if filename is None:
			filename=self.filename
		extn=filename.rsplit(os.sep,1)[-1].rsplit('.',1)
		if len(extn)<2 or extn in ['zip','simg','simt']:
			zf=zipfile.ZipFile(filename,'w')
			for name in self.componentNames:
				component=self.getComponent(name)
				if name.rsplit('.') in ['xml']:
					compress_type=zipfile.ZIP_DEFLATED
				else:
					compress_type=zipfile.ZIP_STORED
				zf.writestr(name,component.read(),compress_type)
			zf.close()
		else:
			result=self.renderImage()
			if result is None:
				print 'ERR: No output to save.'
			else:
				result.save(filename)

	def setVariable(self,name,value):
		"""
		simply set a variable
		"""
		self.variables[name].value=value

	def varFile(self,valuefile,name=None):
		"""
		value and name are in reverse order of what is normally expected
		the reason is you can leave off the name and allow smartimage to guess!
		"""
		valuetype='file'
		data=valuefile
		if valuefile.rsplit('.') in ['txt']:
			f=open(valuefile,'r')
			data=f.read().strip()
			if data.find('\n')>=0:
				valuetype='textarea'
			else:
				valuetype='text'
		if name is None:
			for k,v in self.variables.items():
				if k in self._varAuto:
					continue
				if v.uitype==valuetype:
					self._varAuto.append(k)
					v.value=data
					break
		else:
			self.variables[name].value=data

	def hasUserVariables(self):
		"""
		if there are variables that can be edited
		"""
		ret=False
		for variable in self.variables:
			if not variable.hidden:
				ret=True
				break
		return ret

	def varUi(self,force=True):
		"""
		open a user interface to edit the variables
		"""
		if force or (self.autoUi and not self._hasRunUi and self.hasUserVariables()):
			self._hasRunUi=True
			import ui.tkVarsWindow
			ui.tkVarsWindow.runVarsWindow(self.variables,self.filename)

	def renderImage(self,renderContext=None):
		"""
		NOTE: you probably don't want to call directly, but rather do a
			smartimage[0].renderImage() just to make sure you work with
			multi-page and multi-frame documents.

		WARNING: Do not modify the image without doing a .copy() first!
		"""
		self.varUi(force=False)
		return Layer.renderImage(self,renderContext)

	def smartsize(self,size,useGolden=False):
		"""
		returns an image smartly cropped to the given size

		:param size: the size to change to
		:param useGolden: TODO: try to position regions of interest on golden mean
		"""
		image=self.image
		if image is None:
			return image
		if image.size[0]<1 or image.size[1]<1:
			raise Exception("Image is busted. ",image.size)
		roi=self.roi
		resize=1.0 # percent
		if size[0]!=image.size[0]:
			resize=size[0]/max(image.size[0],1)
		if size[1]!=image.size[1]:
			resize=max(resize,size[1]/max(image.size[1],1))
		# TODO: do I want to scale up the image directly, or get smart about oversizing and using region of interest??
		if resize!=1.0:
			newsize=(int(round(image.size[0]*resize)),int(round(image.size[1]*resize)))
			image=image.resize(newsize)
			roi=roi.resize(newsize)
		# crop in on region of interest
		# for now, simply find the best place in the lingering dimension to crop
		if newsize[0]==size[0]:
			if newsize[1]!=size[1]:
				# width matches, crop height
				d=int(size[1])
				a=np.sum(roi,axis=1) # or use mean
				for u in range(len(a)-d):
					a[u]=np.sum(a[u:u+d])
				a=a[0:-d]
				idx=np.argmax(a)
				cropTo=(0,idx,size[0],idx+size[1])
				image=image.crop(cropTo)
		else:
			# height matches, crop width
			d=int(size[0])
			a=np.sum(roi,axis=0) # or use mean
			for u in range(len(a)-d):
				a[u]=np.sum(a[u:u+d])
			a=a[0:-d]
			idx=np.argmax(a)
			cropTo=(idx,0,idx+size[0],size[1])
			image=image.crop(cropTo)
		return image


def registerPILPligin():
	"""
	Register smartimage with PIL (the Python Imaging Library)
	"""
	from PIL import ImageFile
	class SmartImageFile(ImageFile.ImageFile,SmartImage):
		def _open(self):
			try:
				self.smartimage=self.load(self.fp)
			except:
				raise SyntaxError("Not a SmartImage file")
	def _accept(prefix):
		return prefix[:2]==b"PK" or prefix[:1]==b"<"
	def _save(smartImageFile,filename):
		smartImageFile.save(filename)
	formatName='SmartImage'
	Image.register_open(formatName,SmartImageFile,_accept)
	Image.register_save(formatName,_save)
	Image.register_extension(formatName,".simg")
	Image.register_extension(formatName,".simt")
	Image.register_mime(formatName,"image/xml+smartimage")
	print 'registered PIL plugin.'


def registerPlugins():
	"""
	Register SmartImage as a plugin to all known image programs
	"""
	registerPILPligin()


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
	didSomething=False
	if len(sys.argv)<2:
		printhelp=True
	else:
		didOutput=False
		simg=None
		for arg in sys.argv[1:]:
			if arg.startswith('-'):
				arg=[a.strip() for a in arg.split('=',1)]
				if arg[0] in ['-h','--help']:
					printhelp=True
					didSomething=True
				elif arg[0]=='--smartsize':
					didSomething=True
					arg[1]=arg[1].split('=',1)
					size=[float(x.strip()) for x in arg[1][0].split(',')]
					img=simg.smartsize(size)
					if len(arg[1])>1:
						img.save(arg[1][1])
					else:
						img.show()
				elif arg[0] in ['--image','--show']:
					didSomething=True
					didOutput=True
					if len(arg)>1:
						pages=len(simg)
						if pages>1:
							filename=arg[1].split('.',1)
							digits=len(str(pages))
							format=filename[0]+r'_{:0'+digits+'d}.'+filename[1]
							for idx in range(pages):
								img=simg[idx].renderImage()
								img.save(format.format(idx))
						else:
							img=simg[0].renderImage()
							img.save(arg[1])
					else:
						img=simg[0].renderImage()
						img.show()
						import time
						#while True:
						time.sleep(1)
				elif arg[0]=='--roi':
					didSomething=True
					didOutput=True
					img=simg.roi
					if len(arg)>1:
						img.save(arg[1])
					else:
						img.show()
				elif arg[0]=='--save':
					didSomething=True
					didOutput=True
					simg.save(arg[1])
				elif arg[0]=='--testfont':
					didSomething=True
					didOutput=True
					print arg[1],
					if True:#try:
						simg.setFont(arg[1])
					else:#except Exception,e:
						print e
				elif arg[0]=='--variables':
					didSomething=True
					didOutput=True
					for variable in simg.variables.values():
						print variable.name+'('+variable.uitype+') = '+variable.value+'\n\t'+variable.description
				elif arg[0]=='--set':
					didSomething=True
					simg.setVariable(*arg[1].split('=',1))
				elif arg[0]=='--varfile':
					didSomething=True
					vf=arg[1].split('=',1)
					if len(vf)>1:
						simg.varFile(vf[1],vf[0])
					else:
						simg.varFile(vf[1])
				elif arg[0]=='--varui':
					didSomething=True
					simg.varUi()
				elif arg[0]=='--noui':
					simg.autoUi=False
				elif arg[0]=='--registerPlugins':
					registerPlugins()
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				didSomething=True
				simg=SmartImage(arg)
	if not didSomething:
		print 'ERR: Command accomplished nothing!\n'
		printhelp=True
	elif simg is not None and not didOutput:
		print 'WARN: No output captured.  I\'m assuming you want to show the result, so here goes.'
		img=simg[0].renderImage()
		img.show()
	if printhelp:
		print 'Usage:'
		print '  smartimage.py file.simg [options]'
		print 'Options:'
		print '   --smartsize=w,h[=filename] .... smartsize the image. if no filename, show in a window'
		print '   --show ........................ same as --image (this is also the default if no output is selected)'
		print '   --image[=filename] ............ get the base image. if no filename, show in a window'
		print '                                   if multi-image or multi-frame, modify filename to be a numbered sequence'
		print '   --roi[=filename] .............. get the region of interest image. if no filename, show in a window'
		print '   --save=filename ............... save out the .simg as another file name'
		print '   --testfont=fontname ........... try to fetch the given font'
		print '   --variables ................... list all variables'
		print '   --set=name=value .............. set a variable'
		print '   --varui ....................... manually start user interface now, rather than wait till needed'
		print '   --noui ........................ do not bring up a user interface (useful when setting vars manually)'
		print '   --varfile[=name]=value ........ populate a variable based on a filename - if name is omitted, attempt to fill in variables smartly'
		print '   --registerPlugins ............. Register SmartImage as a plugin to all known image programs'
