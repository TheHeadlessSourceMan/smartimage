import datetime
from xmlBackedObject import *


class Variable(XmlBackedObject):
	def __init__(self,docRoot,parent,xml):
		XmlBackedObject.__init__(self,docRoot,parent,xml)
		self._value=None
		
	@property
	def name(self):
		return self._getProperty('name')
		
	@property
	def description(self):
		return self._getProperty('description','')
		
	@property
	def uitype(self):
		# an html input type like (checkbox color date datetime datetime-local email file hidden image month number password radio range search tel text time url week )
		return self._getProperty('type','text')
	@property
	def type(self):
		return self.uitype
	
	@property
	def default(self):
		return self._getProperty('default','')	
		
	@property
	def value(self):
		if self._value==None:
			return self.default
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
		# this doesn't seem to work right with python.
		# must call toBool directly!
		return self.toBool()
	def toBool(self):
		s=self.__repr__()
		return len(s)>0 and (s[0] in 'YyTt1')