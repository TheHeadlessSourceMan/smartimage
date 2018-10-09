#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Model for forms and their elements.
"""
from xmlBackedObject import *
from image import ImageLayer


class FormElement(XmlBackedObject):
	"""
	common root for any element within a form
	"""

	def __init__(self,docRoot,parent,xml):
		XmlBackedObject.__init__(self,docRoot,parent,xml)
		self._value=None

	@property
	def name(self):
		"""
		the name of the form element
		"""
		return self._getProperty('name')

	@property
	def caption(self):
		"""
		the caption of the form element
		"""
		ret=self._getProperty('caption')
		if ret!='':
			return ret
		ret=self._getProperty('name')
		if ret!='':
			return ret
		ret=self._getProperty('id')
		return ret

	@property
	def tooltip(self):
		"""
		a popup tooltip for this form element
		"""
		return self._getProperty('tooltip','')

	@property
	def hidden(self):
		"""
		if this element is hidden or not
		"""
		return self._getPropertyBool('hidden')

	@property
	def value(self):
		"""
		the value of this element
		"""
		if self._value is None:
			self._value=self._getProperty('value')
			if self._value is None:
				self._value=self.text
		return self._value
	@value.setter
	def value(self,value):
		"""
		set the value of this element
		"""
		self._value=value

	def __int__(self):
		return int(self.value)

	def __float__(self):
		return float(self.value)

	def __bool__(self):
		return self._toBool(self.__repr__())

	def _createChild(self,doc,parent,xml):
		"""
		create a child form element
		"""
		child=None
		if xml==self.xml or xml.__class__.__name__ in ['_Comment']:
			pass
		else:
			raise Exception('ERR: unknown element, "'+xml.tag+'"')
		return child

	@property
	def children(self):
		"""
		list the child form elements
		"""
		if self._children is None:
			self._children=[]
			for tag in [c for c in self.xml.iterchildren()]:
				child=self._createChild(self.docRoot,self,tag)
				if child!=None:
					self._children.append(child)
		return self._children

	def __repr__(self):
		ret=[self.__class__.__name__]
		for k,v in self.__class__.__dict__.items():
			if k[0]!='_' and k not in ['parent','docRoot','xml','points'] and isinstance(v,property):
				ret.append(str(k)+'='+str(v.fget(self)))
		for ch in self.children:
			ret.extend(str(ch).split('\n'))
		return '\n\t'.join(ret)



class Form(FormElement):
	"""
	A form
	"""

	def __init__(self,docRoot,parent,xml):
		if docRoot==None:
			docRoot=self
		FormElement.__init__(self,docRoot,parent,xml)

	def getNextId(self):
		"""
		get the next unused id
		"""
		return 0 # TODO: implement this

	def _createChild(self,doc,parent,xml):
		"""
		create a child form element
		"""
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
		"""
		return the html help address
		(possibly within the smartimage)
		"""
		return self._getProperty('help')


class Preview(FormElement):
	"""
	a form element for an image previewer
	"""

	def __init__(self,docRoot,parent,xml):
		FormElement.__init__(self,docRoot,parent,xml)

	@property
	def showAbove(self):
		"""
		should show the layers on top of this layer in the preview
		"""
		return self._getPropertyBool('showAbove')

	@property
	def showBelow(self):
		"""
		should show the layers below this layer in the preview
		"""
		return self._getPropertyBool('showBelow')

class Text(FormElement):
	"""
	a text entry form element
	"""

	def __init__(self,docRoot,parent,xml):
		FormElement.__init__(self,docRoot,parent,xml)

	@property
	def multiline(self):
		"""
		can the user enter multiple lines of text
		"""
		return self._getPropertyBool('multiline')

class Numeric(FormElement):
	"""
	a numeric form control
	"""

	def __init__(self,docRoot,parent,xml):
		FormElement.__init__(self,docRoot,parent,xml)

	@property
	def min(self):
		"""
		the minimum allowed value
		"""
		ret=self._getProperty('min')
		if ret!=None:
			ret=float(ret)
		return ret

	@property
	def max(self):
		"""
		the maximum allowed value
		"""
		ret=self._getProperty('max')
		if ret!=None:
			ret=float(ret)
		return ret

	@property
	def decimal(self):
		"""
		whether or not decimals are allowed
		"""
		return self._getPropertyBool('decimal',True)


class Select(FormElement):
	"""
	an item selection form element
	"""

	def __init__(self,docRoot,parent,xml):
		FormElement.__init__(self,docRoot,parent,xml)

	def _createChild(self,doc,parent,xml):
		"""
		the only child elements allowed are option form elements
		"""
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
		"""
		if multiple selections are allowed
		"""
		return self._getPropertyBool('multiple')

	@property
	def textEntry(self):
		"""
		if freeform text entry is also allowed
		"""
		return self._getPropertyBool('textEntry')


class Option(FormElement):
	"""
	a single option within a selection
	"""

	def __init__(self,docRoot,parent,xml):
		FormElement.__init__(self,docRoot,parent,xml)


class Color(FormElement):
	"""
	A color selector/picker form element
	"""

	def __init__(self,docRoot,parent,xml):
		FormElement.__init__(self,docRoot,parent,xml)

	@property
	def alpha(self):
		"""
		Also want to get an alpha value
		"""
		return self._getPropertyBool('alpha')

	@property
	def grayscale(self):
		"""
		Grayscale only colors
		"""
		return self._getPropertyBool('grayscale')


class Points(FormElement):
	"""
	A container form element for a group of points.
	"""

	def __init__(self,docRoot,parent,xml):
		FormElement.__init__(self,docRoot,parent,xml)

	def _createChild(self,doc,parent,xml):
		"""
		the child elements are all points (duh)
		"""
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
		"""
		If there are a fixed number of points as opposed to
		the user being able to add as many as they want.
		"""
		if self.rectangle:
			return True
		return self._getPropertyBool('fixedNumber',True)

	@property
	def preview(self):
		"""
		Show/move points in the current preview element
		"""
		return self._getPropertyBool('preview')

	@property
	def rectangle(self):
		"""
		The display idiom is to snap points to a rectangle
		"""
		return self._getPropertyBool('rectangle')

	@property
	def points(self):
		"""
		get at the contained point values
		"""
		if self.rectangle:
			np=len(self.children)
			if np<1: # requires two points, so create them
				self.children.append(Point(self.docRoot,self,'<point value="0,0" />'))
				self.children.append(Point(self.docRoot,self,'<point value="-1,-1" />'))
			elif np<2: # requires two points, so create another
				self.children.append(Point(self.docRoot,self,'<point value="-1,-1" />'))
		return self.children[0:2]


class Point(FormElement):
	"""
	A form element to hold a single x,y point
	"""

	def __init__(self,docRoot,parent,xml):
		FormElement.__init__(self,docRoot,parent,xml)

	@property
	def preview(self):
		"""
		display/move the poit on the current image preview
		"""
		default=False
		if isinstance(self.parent,Points):
			default=self.parent.preview
		return self._getPropertyBool('preview',default)

	@property
	def center(self):
		"""
		hint the ui to draw the point as a rotation/center point for something
		"""
		return self._getPropertyBool('center')


class Image(ImageLayer,FormElement):
	"""
	an image file loader form element
	"""

	def __init__(self,docRoot,parent,xml):
		ImageLayer.__init__(self,docRoot,parent,xml)
		FormElement.__init__(self,docRoot,parent,xml)


def loadForms(filename):
	"""
	Utility to load the forms from a smartimage
	"""
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
