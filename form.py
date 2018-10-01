#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Model for forms and their elements.
"""
from xmlBackedObject import *
from image import ImageLayer


class FormElement(XmlBackedObject):
	def __init__(self,docRoot,parent,xml):
		XmlBackedObject.__init__(self,docRoot,parent,xml)
		self._value=None
		
	@property
	def name(self):
		return self._getProperty('name')
		
	@property
	def caption(self):
		ret=self._getProperty('caption')
		if ret!='':
			return ret
		ret=self._getProperty('name')
		if ret!='':
			return ret
		ret=self._getProperty('id')
		return ret
		
	@property
	def name(self):
		return self._getProperty('name')
		
	@property
	def tooltip(self):
		return self._getProperty('tooltip','')
		
	@property
	def hidden(self):
		return self._getPropertyBool('hidden')
		
	@property
	def value(self):
		if self._value==None:
			self._value=self._getProperty('value')
			if self._value==None:
				self._value=self.text
		return self._value
	@value.setter
	def value(self,value):
		self._value=value
		
	def __int__(self):
		return int(self.value)
		
	def __float__(self):
		return float(self.value)
		
	def __repr__(self):
		return str(self.value)
		
	def __bool__(self):
		return self._toBool(self.__repr__())
		
	def _createChild(self,doc,parent,xml):
		child=None
		if xml==self.xml or xml.__class__.__name__ in ['_Comment']:
			pass
		else:
			raise Exception('ERR: unknown element, "'+xml.tag+'"')
		return child

	@property
	def children(self):
		"""
		"""
		if self._children==None:
			self._children=[]
			for tag in [c for c in self.xml.iterchildren()]:
				child=self._createChild(self.docRoot,self,tag)
				if child!=None:
					self._children.append(child)
		return self._children
		
	def __repr__(self):
		ret=[self.__class__.__name__]
		for k,v in self.__class__.__dict__.items():
			if k[0]!='_' and k not in ['parent','docRoot','xml','points'] and type(v)==property:
				ret.append(str(k)+'='+str(v.fget(self)))
		for ch in self.children:
			ret.extend(str(ch).split('\n'))
		return '\n\t'.join(ret)
			
		
		
class Form(FormElement):
	def __init__(self,docRoot,parent,xml):
		if docRoot==None:
			docRoot=self
		FormElement.__init__(self,docRoot,parent,xml)
		
	def getNextId(self):
		return 0 # TODO
		
	def _createChild(self,doc,parent,xml):
		child=None
		if xml==self.xml or xml.__class__.__name__ in ['_Comment']:
			pass
		elif xml.tag=='text':
			child=Text(doc,parent,xml)
		elif xml.tag=='points':
			child=Points(doc,parent,xml)
		elif xml.tag=='image':
			child=Image(doc,parent,xml)
		elif xml.tag=='point':
			child=Point(doc,parent,xml)
		elif xml.tag=='select':
			child=Select(doc,parent,xml)
		elif xml.tag=='color':
			child=Color(doc,parent,xml)
		elif xml.tag=='preview':
			child=Preview(doc,parent,xml)
		elif xml.tag=='numeric':
			child=Numeric(doc,parent,xml)
		else:
			raise Exception('ERR: unknown element, "'+xml.tag+'"')
		return child
		
	@property
	def help(self):
		return self._getProperty('help')
	
class Preview(FormElement):
	def __init__(self,docRoot,parent,xml):
		FormElement.__init__(self,docRoot,parent,xml)
		
	@property
	def showAbove(self):
		return self._getPropertyBool('showAbove')
		
	@property
	def showBelow(self):
		return self._getPropertyBool('showBelow')
	
class Text(FormElement):
	def __init__(self,docRoot,parent,xml):
		FormElement.__init__(self,docRoot,parent,xml)
		
	@property
	def multiline(self):
		return self._getPropertyBool('multiline')
	
class Numeric(FormElement):
	def __init__(self,docRoot,parent,xml):
		FormElement.__init__(self,docRoot,parent,xml)
		
	@property
	def min(self):
		ret=self._getProperty('min')
		if ret!=None:
			ret=float(ret)
		return ret
		
	@property
	def max(self):
		ret=self._getProperty('max')
		if ret!=None:
			ret=float(ret)
		return ret
		
	@property
	def decimal(self):
		return self._getPropertyBool('decimal',True)
		
		
class Select(FormElement):
	def __init__(self,docRoot,parent,xml):
		FormElement.__init__(self,docRoot,parent,xml)
		
	def _createChild(self,doc,parent,xml):
		child=None
		if xml==self.xml or xml.__class__.__name__ in ['_Comment']:
			pass
		elif xml.tag=='option':
			child=Option(doc,parent,xml)
		else:
			raise Exception('ERR: unknown element, "'+xml.tag+'"')
		return child
		
	@property
	def multiple(self):
		return self._getPropertyBool('multiple')
		
	@property
	def textEntry(self):
		return self._getPropertyBool('textEntry')
		
		
class Option(FormElement):
	def __init__(self,docRoot,parent,xml):
		FormElement.__init__(self,docRoot,parent,xml)
		
		
class Color(FormElement):
	def __init__(self,docRoot,parent,xml):
		FormElement.__init__(self,docRoot,parent,xml)
		
	@property
	def alpha(self):
		return self._getPropertyBool('alpha')
		
	@property
	def grayscale(self):
		return self._getPropertyBool('grayscale')
		
		
class Points(FormElement):
	def __init__(self,docRoot,parent,xml):
		FormElement.__init__(self,docRoot,parent,xml)
		
	def _createChild(self,doc,parent,xml):
		child=None
		if xml==self.xml or xml.__class__.__name__ in ['_Comment']:
			pass
		elif xml.tag=='point':
			child=Point(doc,parent,xml)
		else:
			raise Exception('ERR: unknown element, "'+xml.tag+'"')
		return child
		
	@property
	def fixedNumber(self):
		if self.rectangle:
			return True
		return self._getPropertyBool('fixedNumber',True)
		
	@property
	def preview(self):
		return self._getPropertyBool('preview')
		
	@property
	def rectangle(self):
		return self._getPropertyBool('rectangle')
		
	@property
	def points(self):
		ret=self.children
		if self.rectangle:
			np=len(self.children)
			if np<1: # requires two points, so create them
				self.children.append(Point(self.docRoot,self,'<point value="0,0" />'))
				self.children.append(Point(self.docRoot,self,'<point value="-1,-1" />'))
			elif np<2: # requires two points, so create another
				self.children.append(Point(self.docRoot,self,'<point value="-1,-1" />'))
		return self.children[0:2]
		
		
class Point(FormElement):
	def __init__(self,docRoot,parent,xml):
		FormElement.__init__(self,docRoot,parent,xml)
		
	@property
	def preview(self):
		default=False
		if type(self.parent)==Points:
			default=self.parent.preview
		return self._getPropertyBool('preview',default)
		
	@property
	def center(self):
		return self._getPropertyBool('center')
		
		
class Image(ImageLayer,FormElement):
	def __init__(self,docRoot,parent,xml):
		ImageLayer.__init__(self,docRoot,parent,xml)
		FormElement.__init__(self,docRoot,parent,xml)
		
		
def loadForms(filename):
	import os
	ext=filename.rsplit('.',1)[-1]
	if os.path.isdir(filename):
		filename=os.path.join(filename,'smartimage.xml')
	if ext in ['htm','html','xml']:
		f=open(filename,'rb')
	else:
		import zipfile
		zf=zipfile.ZipFile(filename)
		f=zf.open('smartimage.xml')
	import lxml.etree
	doc=lxml.etree.parse(f)
	forms=doc.xpath('//*/form')
	ret=[]
	for form in forms:
		ret.append(Form(None,None,form))
	return ret
		
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
		img1=None
		img2=None
		blendMode='normal'
		custom=None
		opacity=1.0
		mask=None
		for arg in sys.argv[1:]:
			if arg.startswith('-'):
				arg=[a.strip() for a in arg.split('=',1)]
				if arg[0] in ['-h','--help']:
					printhelp=True
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				forms=loadForms(arg)
				for form in forms:
					print form
	if printhelp:
		print 'Usage:'
		print '  form.py [options] form'
		print 'Options:'
		print '   [none]'
