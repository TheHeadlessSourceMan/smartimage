# -*- coding: utf-8 -*-
"""
This is a layer that links to another layer
"""
from smartimage.layer import *
from smartimage.errors import SmartimageError


class Link(Layer):
    """
    This is a layer that links to another layer
    """

    def __init__(self,parent:Layer,xml:str):
        self._target=None
        Layer.__init__(self,parent,xml)

    @property
    def ref(self)->str:
        """
        get the reference
        """
        return self.xml.attrib['ref']
    @ref.setter
    def ref(self,ref):
        """
        set the reference
        """
        self.xml.attrib['ref']=ref
        self.root.dirty=True

    def _getProperty(self,name:str,default=None):
        """
        override _getProperty so that when somebody uses this object
        they get the property of the one it is linked to instead
        """
        val=default
        if name in self.xml.attrib:
            val=self.xml.attrib[name]
        elif name not in ['name','elementId']: # can't be unique to this object
            val=self.target._getProperty(name,default)
        return val

    @property
    def target(self)->Layer:
        """
        the target to link to
        """
        if self._target is None:
            layerId=self.ref.split('.',1)[0]
            self._target=self.getLayer(layerId)
            if self._target is None:
                raise SmartimageError(self,'ERR: broken link to layer %s'%layerId)
        return self._target

    @property
    def image(self)->Union[PilPlusImage,None]:
        """
        get the image for this layer
        """
        img=self.target.image

        w=self._getProperty('w','auto')
        h=self._getProperty('h','auto')
        if (w not in ['0','auto']) and (h not in ['0','auto']):
            if w in ['0','auto']:
                w=img.width*(img.height/h)
            elif h in ['0','auto']:
                h=img.height*(img.width/w)
            img=img.resize((int(w),int(h)),img.ANTIALIAS)
        img.immutable=True # mark this image so that compositor will not alter it
        return img