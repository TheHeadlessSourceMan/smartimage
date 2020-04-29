# -*- coding: utf-8 -*-
"""
This is a number space conversion layer
"""
from smartimage.layer import *


class NumberSpace(Layer):
    """
    This is a number space conversion layer
    """

    def __init__(self,parent:Layer,xml:str):
        Layer.__init__(self,parent,xml)

    @property
    def space(self)->str:
        """
        nunberspace to transform to/from
        """
        return self._getProperty('space')

    @property
    def levels(self):
        """
        the levels to use (if necessary for a given transformation)
        """
        return self._getProperty('levels')

    @property
    def mode(self):
        """
        the mode to use (if necessary for a given transformation)
        """
        return self._getProperty('mode')

    @property
    def invert(self)->bool:
        """
        perform the reverse transformation to get back to the original
        """
        return self._getPropertyBool('invert')

    @property
    def complex(self)->bool:
        """
        whether or not complex number results are allowed
        """
        return self._getPropertyBool('complex')

    def renderImage(self,renderContext=None)->Union[PilPlusImage,None]:
        """
        WARNING: Do not modify the image without doing a .copy() first!
        """
        opacity=self.opacity
        if opacity<=0.0 or not self.visible:
            return None
        image=numberspaceTransform(Layer.renderImage(self,renderContext).copy(),
            self.space,invert=self.invert,complex=self.complex,level=self.levels,mode=self.mode)
        if self.opacity<1.0:
            self.setOpacity(image,opacity)
        return image