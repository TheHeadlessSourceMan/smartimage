class XmlBackedList:
	"""
	This is a list that shadows a bit of xml, such that when
	the list changes, the xml changes.
	
	Supports lazy loading.
	"""
	
	def __init__(self,doc,parent,xpath,listItemObject):
		"""
		automatically populates based on xpath!
		
		listItemObject can be an object to create, or a function
			it is expected to take(doc,parent,xml_single_xpath_result)
		"""
		self.doc=doc
		self.parent=parent
		self.xpath=xpath
		self.listItemObject=listItemObject
		self._actualList=None
		
	@property
	def _list(self):
		if self._actualList==None:
			self._actualList=[]
			for item in self.doc.xpath(self.xpath):
				item=self.listItemObject(self.doc,self,item)
				self._actualList.append(item)
		return self._actualList
		
    def __delitem__(self, key):
        del self._list(key)
		self.doc.dirty=True
    
	def __getitem__(self,key):
        return self._list[key]
    
	def __setitem__(self,key,value):
        self._list[key]=value
		self.doc.dirty=True