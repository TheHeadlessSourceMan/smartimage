# -*- coding: utf-8 -*-
"""
This is an object backed by xml data
"""
from typing import *
from backedObject import *
from smartimage.errors import *


class SmartimageXmlObject(XmlBackedObject):
    """
    This is an object backed by xml data
    """

    def __init__(self,parent:Union['SmartimageXmlObject',None],xml:str):
        if xml is None:
            raise Exception()
        XmlBackedObject.__init__(self,parent,None,xml)
        self.elementId=XmlBackedValue(self,'id',default=self.root.getNextId)
        self._variables={}

    @property
    def name(self)->str:
        """
        the friendly, viewable name of this layer
        """
        ret=self._getProperty('name')
        if ret is None:
            ret='Layer '+str(self.elementId)
        return ret
    @name.setter
    def name(self,name):
        """
        the friendly, viewable name of this layer
        """
        self._setProperty('name',name)

    def _fixValueResults(self,value,xob,nameHint):
        """
        Whenever a value is read from the file, we'll run it through this function
        before returning.  This way special magic values can be implemented.

        Probably best to avoid using this if at all possible.
        """
        if xob is not None: # TODO: do I want to do this?
            # width and height can be auto
            if nameHint in ['w','h'] and value in ('0','auto',None):
                value=getattr(xob,nameHint)
        return value

    def getVariableValue(self,name:str):
        """
        get the value of the variable
        """
        if name in self._variables:
            return self._variables[name]
        if self.parent is not None:
            val=self.parent.getVariableValue(name)
            if val is not None:
                return val
        val=self.root.getLayer(name)
        if val is None:
            return None
        return val.getattr('value')

    def _dereference(self,name:str,nameHint='',default=None,nofollow=None):
        """
        :param name: the name to dereference
        :param nameHint: the attribute in the original object that we got name from
            (or '_' = text contents)
        """
        newVal=name
        xob=None
        if nofollow is None:
            nofollow=[]
        while isinstance(name,str) and name and name[0]=='@':
            # loop detection
            valueLocation=self.root.xmlName+':'+name
            if valueLocation in nofollow:
                nofollow.append(name)
                raise SmartimageError(self,'ERR: Loop detected "'+('->'.join(nofollow))+'"')
            nofollow.append(valueLocation)
            # --- search by Id
            idFind=name[1:].split('.',1)
            idFind.append(nameHint)
            newVal=None
            if newVal is None:
                xob=self.root.getLayer(idFind[0])
                if xob is not None:
                    nameHint=idFind[1]
                    if nameHint=='_':
                        newVal=self.xml.text
                    else:
                        newVal=default
                        if nameHint in xob.xml.attrib:
                            newVal=xob.xml.attrib[nameHint]
            # --- search in context
            if newVal is None:
                if newVal is None:
                    newVal=self.getVariableValue(idFind[0])
                if idFind[0] in self.root.variables:
                    newVal=self.root.variables[idFind[0]].value
            # --- search by filename
            if newVal is None:
                newVal=self.root.getItemByFilename(name,nofollow)
            # --- search by nameHint
            if newVal is None:
                xob=self.root.getLayerByName(idFind[0])
                if xob is not None:
                    nameHint=idFind[1]
                    if nameHint=='_':
                        newVal=xob.text
                    else:
                        newVal=default
                        if nameHint in xob.xml.attrib:
                            newVal=xob.xml.attrib[nameHint]
            name=newVal
        return self._fixValueResults(newVal,xob,nameHint)

    def _setProperty(self,name:str,value):
        """
        name - set this property from the xml attributes
        value -
        """
        self.xml.attrib[name]=str(value)

    def _getProperty(self,name:str,default=None):
        """
        name - retrieve this property from the xml attributes
        default - if there is no attribute, return this instead
            (can be a link or replacement)
        Optional:
            You can also have a replacement value that is a link, or a link that
            points to a replacement value.
        """
        if callable(default):
            default=default()
        value=default
        if self.xml is not None and name in self.xml.attrib:
            value=self.xml.attrib[name]
        val1=value
        value=self._dereference(value,name,default,['@%s.%s'%(self.elementId,name)])
        if val1!=value:
            print('dereferenced "%s" to "%s"'%(val1,value))
        return value

    def _getPropertyArray(self,name:str,default=None)->Union[list,None]:
        val=self._getProperty(name,default)
        if val is None:
            return val
        val=val.strip()
        if val[0]=='[':
            val=val[1:-1]
        return [float(v) for v in val.split(',')]

    def _getPropertyBool(self,name:str,default=False)->bool:
        """
        gets a property returning a boolean value
        """
        prop=self._getProperty(name,'').lstrip()
        if prop=='':
            return default
        return prop[0].lower() in ('y','t','1')

    def _setPropertyBool(self,name:str,value=True):
        if value:
            self._setProperty(name,'true')
        else:
            self._setProperty(name,'false')

    def _getPropertyPercent(self,name:str,default=1.0)->float:
        """
        gets a property, always returning a decimal percent (where 1.0 = 100%)

        name - retrieve this property from the xml attributes
        default - if there is no attribute, return this instead
            (can be a link or replacement)
        Optional:
            You can also have a replacement value that is a link, or a link that
             points to a replacement value.
        """
        value=self._getProperty(name,default)
        if isinstance(value,str):
            value=value.strip()
            if value:
                value=default
            else:
                if value[-1]=='%':
                    value=float(value[0:-1])/100.0
                else:
                    value=float(value)
        return value

    def _getPropertyFloat(self,name:str,default=0.0)->float:
        """
        gets a property, always returning a float

        name - retrieve this property from the xml attributes
        default - if there is no attribute, return this instead
            (can be a link or replacement)
        Optional:
            You can also have a replacement value that is a link, or a link
            that points to a replacement value.
        """
        value=self._getProperty(name,default)
        if isinstance(value,str):
            value=value.strip()
            if not value:
                value=default
            value=float(value)
        return value

    @property
    def uitype(self)->str:
        """
        The type for ui representation
        """
        return self.xml.tag

    @property
    def text(self)->str:
        """
        the value as text
        """
        return self._dereference(self.xml.text,'_','',['#'+str(self.elementId)+'._'])
