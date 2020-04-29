# -*- coding: utf-8 -*-
"""
This is a layer that represents a single, final page in a multi-page document (like a book)
"""
from smartimage.layer import *


class Page(Layer):
    """
    This is a layer that represents a single, final page in a multi-page document (like a book)
    """

    def __init__(self,parent:Layer,xml:str):
        Layer.__init__(self,parent,xml)
