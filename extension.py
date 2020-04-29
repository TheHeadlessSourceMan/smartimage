# -*- coding: utf-8 -*-
"""
A layer representing a smartimage extension
"""
from smartimage.image import *


class ExtensionLayer(ImageLayer):
    """
    A layer representing a smartimage extension
    """

    def __init__(self,parent,xml):
        ImageLayer.__init__(self,parent,xml)

    @property
    def type(self):
        """
        the type for the extension
        """
        return self._getProperty('type')

    @property
    def filename(self)->str:
        """
        turn this extension+id into a filename to save
        the extension's output image
        """
        return self.type+'/'+self.elementId+'.png'

    @property
    def extensionClass(self):
        """
        get the external extension class or None
        """
        extPkgName=self.type.replace('.','_')
        try:
            exec('import extensions.'+extPkgName)
            return eval('extensions.'+extPkgName+'Extension')
        except ImportError:
            pass

    @property
    def image(self)->Union[PilPlusImage,None]:
        """
        get the layer's image
        """
        extensionClass=self.extensionClass
        if extensionClass is None:
            image=ImageLayer.image
        else:
            ext=extensionClass(self.root,self,self.xml)
            image=ext.image
            self.root.saveImage(image,self.filename)
        return image
