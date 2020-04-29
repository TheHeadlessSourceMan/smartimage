# -*- coding: utf-8 -*-
"""
A layer that contains an image
"""
from typing import *
import io
from imageTools import *
from smartimage.layer import *
from smartimage.errors import SmartimageError


class ImageLayer(Layer):
    """
    A layer that contains an image
    """

    def __init__(self,parent,xml='image'):
        Layer.__init__(self,parent,xml)

    @property
    def roi(self)->Union[PilPlusImage,None]:
        """
        the region of interest of a graphical image

        if there is none, figure it out
        """
        ref=self._getProperty('roi')
        if ref is not None:
            try:
                img=self.root.imageByRef(ref)
            except FileNotFoundError as e:
                raise SmartimageError(self,'Missing roi resource "%s"'%e.filename)
        else:
            img=interest(self.image)
        if img.size!=self.image.size:
            img.resize(self.image.size)
        return img

    @property
    def src(self)->Union[PilPlusImage,None,str]:
        """
        The source of the image.

        Can be one of:
            an internal filename
            an external filename
            a reference to another image
        """
        return self._getProperty('src')
    @src.setter
    def src(self,src):
        self._setProperty('src',src)

    @property
    def image(self)->Union[PilPlusImage,None]:
        """
        the image for this layer
        """
        try:
            img=self.root.imageByRef(self.src)
        except FileNotFoundError as e:
            raise SmartimageError(self,'Missing image src resource "%s"'%e.filename)
        if img is None:
            return img
        w=self._getProperty('w','auto')
        h=self._getProperty('h','auto')
        if (w not in ['0','auto']) and (h not in ['0','auto']):
            if w in ['0','auto']:
                w=img.width*(img.height/h)
            elif h in ['0','auto']:
                h=img.height*(img.width/w)
            img=img.resize((int(w),int(h)),img.ANTIALIAS)
        if img is not None:
            img.immutable=True # mark this image so that compositor will not alter it
        return img
    @image.setter
    def image(self,image):
        """
        Can assign any PIL image or a filename that can be loaded as one
        """
        if image is None:
            raise SmartimageError(self,'Attempt to assign None as an image')
        if isinstance(image,str):
            filename=image
            image=PilPlusImage(filename)
            imageFormat=image.format
        elif image.format is not None:
            filename=self.name+'.'+image.format.lower()
            imageFormat=image.format
        else:
            filename=self.name+'.png'
            imageFormat='PNG'
        data=io.BytesIO()
        image.save(data,imageFormat)
        data=data.getvalue()
        filename=self.root.addComponent(filename,data,overwrite=False)
        self.src=filename
