# -*- coding: utf-8 -*-
"""
This is a layer of a solid color (same nomenclature as Adobe AfterEffects)
"""
from imageTools import *
from smartimage.layer import *


class Solid(Layer):
    """
    This is a layer of a solid color (same nomenclature as Adobe AfterEffects)
    """

    def __init__(self,parent:Layer,xml:str):
        Layer.__init__(self,parent,xml)

    @property
    def color(self):
        """
        get the background color
        """
        return strToColor(self._getProperty('color','#ff00ff'))
    @color.setter
    def color(self,color):
        if not isinstance(color,str):
            color=colorToStr(color)
        self._setProperty('color',color)

    @property
    def image(self)->PilPlusImage:
        """
        returns a new solid color image
        """
        if self.w==0:
            self.w=1
        if self.h==0:
            self.h=1
        return PilPlusImage(Image.new('RGBA',(int(self.w),int(self.h)),tuple(self.color)))