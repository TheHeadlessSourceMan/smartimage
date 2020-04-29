# -*- coding: utf-8 -*-
"""
This is a layer that represents a single frame in an animation or presentation
"""
from smartimage.layer import *


class Frame(Layer):
    """
    This is a layer that represents a single frame in an animation or presentation
    """

    def __init__(self,parent:Layer,xml:str):
        Layer.__init__(self,parent,xml)

    @property
    def time(self)->float:
        """
        the time delay of this frame before advancing to the next one
        """
        return self._getFloat('time',0.25)

    @property
    def wait(self)->bool:
        """
        wait for user input to advance to the next frame
        """
        return self._getBool('wait',False)
