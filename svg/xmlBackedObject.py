#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This is an object backed by xml data
"""


class XmlBackedObject(object):
	"""
	This is an object backed by xml data
	"""

	def __init__(self,docRoot,parent,xml):
		self._children=None
		self.docRoot=docRoot
		self.parent=parent
		self._xml=xml
		self._id=None
		self.dirty=False

	def _dereference(self,name,value,default=None,allowReplacements=True,allowLinks=True,nofollow=[]):
		"""
		name - the attribute in the original object that we got value from (or '_' = text contents)
		"""
		while type(value) in [str,unicode] and len(value)>0 and value[0]=='@':
			# loop detection
			if value in nofollow:
				nofollow.append(value)
				raise Exception('ERR: Loop detected "'+('->'.join(nofollow))+'"')
			nofollow.append(value)
			# determine what to link to
			idFind=value[1:].split('.',1)
			idFind.append(name)
			value=None
			if allowReplacements and idFind[0] in self.docRoot.variables:
				value=self.docRoot.variables[idFind[0]].value
			if allowLinks and value==None:
				xob=self.docRoot.getLayer(idFind[0])
				if xob!=None:
					name=idFind[1]
					if name=='_':
						value=self.xml.text
					else:
						value=default
						if name in xob.xml.attrib:
							value=xob.xml.attrib[name]
		return value

	def _getProperty(self,name,default=None,allowReplacements=True,allowLinks=True):
		"""
		name - retrieve this property from the xml attributes
		default - if there is no attribute, return this instead (can be a link or replacement)
		Optional:
			allowLinks - replace a "@id", "@id._", or "@id.attr" value with the same value from the layer with that id
			allowReplacements - replace a "@label" value with the current value of a variable
			You can also have a replacement value that is a link, or a link that points to a replacement value.
		"""
		value=default
		if name in self.xml.attrib:
			value=self.xml.attrib[name]
		value=self._dereference(name,value,default,allowReplacements,allowLinks,['#'+self.id+'.'+name])
		return value
		
	def _getPropertyPercent(self,name,default=1.0,allowReplacements=True,allowLinks=True):
		"""
		gets a property, always returning a decimal percent (where 1.0 = 100%)
		
		name - retrieve this property from the xml attributes
		default - if there is no attribute, return this instead (can be a link or replacement)
		Optional:
			allowLinks - replace a "@id", "@id._", or "@id.attr" value with the same value from the layer with that id
			allowReplacements - replace a "@label" value with the current value of a variable
			You can also have a replacement value that is a link, or a link that points to a replacement value.
		"""
		value=self._getProperty(name,default,allowReplacements,allowLinks)
		if type(value) in [str,unicode]:
			if len(value)<1:	
				value=default
			else:
				value=value.strip()
				if value[-1]=='%':
					value=float(value[0:-1])/100.0
				else:
					value=float(value)
		return value

	@property
	def id(self):
		if 'id' not in self.xml.attrib:
			if self._id==None:
				self._id=str(self.docRoot.getNextId())
			return self._id
		return self.xml.attrib['id']

	@property
	def dirtyBranch(self):
		if self.dirty:
			return True
		for child in self.children:
			if child.dirtyBranch:
				return True
		return False

	@property
	def xml(self):
		return self._xml

	@property
	def text(self):
		return self._getText()
	def _getText(self,allowReplacements=True,allowLinks=True):
		"""
		Optional:
			allowLinks - replace a "@id", "@id._", or "@id.attr" value with the same value from the layer with that id
			allowReplacements - replace a "@label" value with the current value of a variable
			You can also have a replacement value that is a link, or a link that points to a replacement value.
		"""
		return self._dereference('_',self.xml.text,'',allowReplacements,allowLinks,['#'+self.id+'._'])


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
		print '  xmlBackedObject.py [options]'
		print 'Options:'
		print '   NONE'