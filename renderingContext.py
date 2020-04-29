# -*- coding: utf-8 -*-
"""
Used to track an image render
"""
from typing import *
import PIL
from imageTools import *
from smartimage.errors import SmartimageError


class RenderingContext:
    """
    Used to keep track of atributes while rendering an image from layers
    and also a box to keep utility functions in.
    """
    def __init__(self):
        self.desired:Bounds=Bounds(0,0,0,0)
        self.cur_rot:float=0
        self.cur:Bounds=Bounds(0,0,0,0)
        self.cur_image:Union[PIL.Image.Image,None]=None
        self.visitedLayers:Set['Layer']=set()

    def log(self,*vals)->NoReturn:
        """
        write something to the rendering debug log
        """
        print((' '*len(self.visitedLayers))+(' '.join([str(v) for v in vals])))

    def renderImage(self,layer:'Layer')->Union[PIL.Image.Image,None]:
        """
        render an image from the layer image and all of its children

        WARNING: Do not modify the image without doing a .copy() first!
        """
        image=None
        # loop prevention
        if layer.elementId in self.visitedLayers:
            info=(layer.elementId,layer.name)
            raise SmartimageError(layer,'Link loop with layer %s "%s"'%info)
        self.visitedLayers.add(layer.elementId)
        # push a new variable context
        # do we need to do anything?
        opacity=layer.opacity
        if opacity<=0.0 or not layer.visible:
            self.log('skipping',layer.name)
        else:
            self.log('creating new %s layer named "%s"'%(layer.__class__.__name__,layer.name))
            image=layer.image # NOTE: base image can be None
            for childLayer in layer.children:
                childImage=childLayer.renderImage(self)
                image=composite(childImage,image,
                    opacity=childLayer.opacity,blendMode=childLayer.blendMode,mask=childLayer.mask,
                    position=childLayer.location,resize=True)
                self.log('adding child layer "%s" at %s'%(childLayer.name,childLayer.location))
            if layer.cropping is not None:
                image=image.crop(layer.cropping)
            if layer.rotation%360!=0:
                self.log('rotating',layer.name)
                bounds=Bounds(0,0,image.width,image.height)
                bounds.rotateFit(layer.rotation)
                image=extendImageCanvas(image,bounds)
                image=image.rotate(layer.rotation)
            # logging
            if image is None:
                self.log('info','for "%s":'%layer.name)
                self.log('info','   NULL IMAGE')
            else:
                self.log('info','for "%s":'%layer.name)
                self.log('info','   mode='+image.mode)
                self.log('info','   bounds=(0,0,%d,%d)'%(image.width,image.height))
        self.log('finished',layer.name)
        # pop off tracking info for this layer
        self.visitedLayers.pop()
        return image
