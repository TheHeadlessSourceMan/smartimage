#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
	This program allows an image to behave smartly and automatically
"""
import os
import zipfile
import lxml.etree
from layer import *
from variable import *
from collections import OrderedDict
import numpy as np
from PIL import ImageDraw


class SmartImage(Layer):
	"""
	This program allows an image to behave smartly and automatically
	"""

	def __init__(self,filename):
		Layer.__init__(self,self,None,None)
		self._hasRunUi=False
		self._nextId=None
		self._variables=None
		self._varAuto=[]
		self.autoUi=True
		self.load(filename)
		self.cacheRenderedLayers=True # trade memory for speed

	@property
	def variables(self):
		if self._variables==None:
			self._variables=OrderedDict()
			for variable in self.xml.xpath('//*/variable'):
				variable=Variable(self,variable)
				self._variables[variable.name]=variable
		return self._variables

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
			if self._zipfile==None:
				self._zipfile=zipfile.ZipFile(self.filename)
			f=self._zipfile.open(name)
		return f

	def getNextId(self,rescan=False):
		"""
		take the next unused id number
		"""
		if self._nextId==None:
			data=self.getComponent('smartimage.xml').read()
			first=True
			maxid=1
			for id in data.split('id="'):
				if first:
					first=False
				else:
					id=int(id.split('"',1)[0])
					if id>maxid:
						maxid=id
			self._nextId=maxid+1
		id=self._nextId
		self._nextId+=1
		#print 'GENERATED ID:',id
		return id

	def imageByRef(self,ref,visitedLayers=[]):
		"""
		grab an image by reference
		ref - one of:
			filename
			#id
			
		WARNING: Do not modify the image without doing a .copy() first!
		"""
		if ref==None:
			return None
		if ref.startswith('@'):
			l=self.getLayer(ref[1:])
			if l==None:
				raise Exception('ERR: Missing reference to "'+ref+'"')
			return l.renderImage()
		return Image.open(self.docRoot.getComponent(ref),'r')

	@property
	def componentNames(self):
		ret=[]
		if os.path.isdir(self.filename):
			ret.extend(os.listdir(self.filename))
		else:
			if self._zipfile==None:
				self._zipfile=zipfile.ZipFile(self.filename)
			ret.extend(self._zipfile.namelist())
		return ret

	@property
	def xml(self):
		if self._xml==None:
			self._xml=lxml.etree.parse(self.getComponent('smartimage.xml'))
		return self._xml.getroot()

	def write(self,image,text,xy,align=None,font=None):
		if font!=None:
			self.setFont(font)
		if align!=None:
			self.textAlignment=align
		draw=ImageDraw.Draw(image)
		draw.multiline_text(xy,text,None,self.currentFont,anchor=None,spacing=self.lineSpacing,align=self.textAlignment)

	def load(self,filename):
		self._xml=None
		self._zipfile=None
		self.currentFont=None
		self.lineSpacing=0
		self.textAlignment='left'
		self.filename=filename

	def save(self,filename=None):
		self.varUi(force=False)
		if filename==None:
			filename=self.filename
		zf=zipfile.ZipFile(filename,'w')
		for name in self.componentNames:
			component=self.getComponent(name)
			if name.rsplit('.') in ['xml']:
				compress_type=zipfile.ZIP_DEFLATED
			else:
				compress_type=zipfile.ZIP_STORED
			zf.writestr(name,component.read(),compress_type)
		zf.flush()
		zf.close()

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
		if name==None:
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
			if variable.type!='hidden':
				ret=True
				break
		return ret
			
	def varUi(self,force=True):
		"""
		open a user interface to edit the variables
		"""
		if force or (self.autoUi and not self._hasRunUi and self.hasUserVariables()):
			self._hasRunUi=True
			import tkVarsWindow
			tkVarsWindow.runVarsWindow(self.variables,self.filename)

	def renderImage(self,renderContext=None):
		"""
		WARNING: Do not modify the image without doing a .copy() first!
		"""
		self.varUi(force=False)
		return Layer.renderImage(self,renderContext)

	def smartsize(self,size,useGolden=False):
		"""
		returns an image smartly cropped to the given size

		useGolden - TODO: try to position regions of interest on golden mean
		"""
		image=self.image
		if image==None:
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
		simg=None
		for arg in sys.argv[1:]:
			if arg.startswith('-'):
				arg=[a.strip() for a in arg.split('=',1)]
				if arg[0] in ['-h','--help']:
					printhelp=True
				elif arg[0]=='--smartsize':
					arg[1]=arg[1].split('=',1)
					size=[float(x.strip()) for x in arg[1][0].split(',')]
					img=simg.smartsize(size)
					if len(arg[1])>1:
						img.save(arg[1][1])
					else:
						img.show()
				elif arg[0]=='--image':
					img=simg.renderImage()
					print [0,0,img.width,img.height]
					if len(arg)>1:
						img.save(arg[1])
					else:
						img.show()

						import time
						while True:
							time.sleep(1)
				elif arg[0]=='--roi':
					img=simg.roi
					if len(arg)>1:
						img.save(arg[1])
					else:
						img.show()
				elif arg[0]=='--save':
					simg.save(arg[1])
				elif arg[0]=='--testfont':
					print arg[1],
					if True:#try:
						simg.setFont(arg[1])
						print True
					else:#except Exception,e:
						print False
						print e
				elif arg[0]=='--variables':
					for variable in simg.variables.values():
						print variable.name+'('+variable.uitype+') = '+variable.value+'\n\t'+variable.description
				elif arg[0]=='--set':
					simg.setVariable(*arg[1].split('=',1))
				elif arg[0]=='--varfile':
					vf=arg[1].split('=',1)
					if len(vf)>1:
						simg.varFile(vf[1],vf[0])
					else:
						simg.varFile(vf[1])
				elif arg[0]=='--varui':
					simg.varUi()
				elif arg[0]=='--noui':
					simg.autoUi=False
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				simg=SmartImage(arg)
	if printhelp:
		print 'Usage:'
		print '  smartimage.py file.simg [options]'
		print 'Options:'
		print '   --smartsize=w,h[=filename] .... smartsize the image. if no filename, show in a window'
		print '   --image[=filename] ............ get the base image. if no filename, show in a window'
		print '   --roi[=filename] .............. get the region of interest image. if no filename, show in a window'
		print '   --save=filename ............... save out the .simg as another file name'
		print '   --testfont=fontname ........... try to fetch the given font'
		print '   --variables ................... list all variables'
		print '   --set=name=value .............. set a variable'
		print '   --varui ....................... manually start user interface now, rather than wait till needed'
		print '   --noui ........................ do not bring up a user interface (useful when setting vars manually)'
		print '   --varfile[=name]=value ........ populate a variable based on a filename - if name is omitted, attempt to fill in variables smartly'