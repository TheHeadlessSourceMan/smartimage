# -*- coding: utf-8 -*-
"""
This contains the error objects for the system
"""


class SmartimageError(Exception):
    """
    An error for smartimages that contains
    extra useful information for debugging
    """

    def __init__(self,layer:'Layer',text:str):
        self.layer=layer
        self.filename=layer.root.filename
        self.xml=layer.xml
        self.line=self.xml.sourceline
        text='%s\n\tin tag <%s> at %s line %d'%(text,self.xml.tag,self.filename,self.line)
        Exception.__init__(self,text)