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
		self._variableManager=None
		self.dirty=False
		
	def _fixValueResults(self,value,xob,nameHint):
		"""
		Whenever a value is read from the file, we'll run it through this function
		before returning.  This way special magic values can be implemented.
		
		Probably best to avoid using this if at all possible.
		"""
		if xob!=None: # TODO: do I want to do this?
			# width and height can be auto
			if nameHint in ['w','h'] and value in ('0','auto',None):
				value=getattr(xob,nameHint)
		return value

	def _dereference(self,name,nameHint='',default=None,nofollow=[]):
		"""
		:param nameHint: the attribute in the original object that we got name from (or '_' = text contents)
		:param name: the name to dereference
		"""
		newVal=name
		xob=None
		while type(name) in [str,unicode] and len(name)>0 and name[0]=='@':
			# loop detection
			valueLocation=self.docRoot.xmlName+':'+name
			if valueLocation in nofollow:
				nofollow.append(name)
				raise Exception('ERR: Loop detected "'+('->'.join(nofollow))+'"')
			nofollow.append(valueLocation)
			# --- search by Id
			idFind=name[1:].split('.',1)
			idFind.append(nameHint)
			newVal=None
			if newVal==None:
				xob=self.docRoot.getLayer(idFind[0])
				if xob!=None:
					nameHint=idFind[1]
					if nameHint=='_':
						newVal=self.xml.text
					else:
						newVal=default
						if nameHint in xob.xml.attrib:
							newVal=xob.xml.attrib[nameHint]
			# --- search in context
			if newVal==None:
				if newVal==None and self._variableManager!=None:
					newVal=self._variableManager.getVariableValue(idFind[0])
				if idFind[0] in self.docRoot.variables:
					newVal=self.docRoot.variables[idFind[0]].value
			# --- search by filename
			if newVal==None:
				newVal=self.docRoot.getItemByFilename(name,nofollow)
			# --- search by nameHint
			if newVal==None:
				xob=self.docRoot.getLayerByName(idFind[0])
				if xob!=None:
					nameHint=idFind[1]
					if nameHint=='_':
						newVal=xob.text
					else:
						newVal=default
						if nameHint in xob.xml.attrib:
							newVal=xob.xml.attrib[nameHint]
			name=newVal
		return self._fixValueResults(newVal,xob,nameHint)

	def _getProperty(self,name,default=None):
		"""
		name - retrieve this property from the xml attributes
		default - if there is no attribute, return this instead (can be a link or replacement)
		Optional:
			You can also have a replacement value that is a link, or a link that points to a replacement value.
		"""
		value=default
		if name in self.xml.attrib:
			value=self.xml.attrib[name]
		value=self._dereference(value,name,default,['@'+self.id+'.'+name])
		return value

	def _getPropertyArray(self,name,default=None):
		val=self._getProperty(name,default)
		if val==None:
			return val
		val=val.strip()
		if val[0]=='[':
			val=val[1:-1]
		return [float(v) for v in val.split(',')]
		
	def _getPropertyPercent(self,name,default=1.0):
		"""
		gets a property, always returning a decimal percent (where 1.0 = 100%)

		name - retrieve this property from the xml attributes
		default - if there is no attribute, return this instead (can be a link or replacement)
		Optional:
			You can also have a replacement value that is a link, or a link that points to a replacement value.
		"""
		value=self._getProperty(name,default)
		if type(value) in [str,unicode]:
			value=value.strip()
			if len(value)<1:
				value=default
			else:
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
		return self._dereference(self.xml.text,'_','',['#'+self.id+'._'])


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