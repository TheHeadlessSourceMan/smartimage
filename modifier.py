# -*- coding: utf-8 -*-
"""
This is a modifier layer such as blur, sharpen, posterize, etc
"""
from PIL import ImageFilter, ImageOps, ImageEnhance
from imageTools import *
from smartimage.layer import *
from smartimage.errors import SmartimageError


class Modifier(Layer):
    """
    This is a modifier layer such as blur, sharpen, posterize, etc
    """

    def __init__(self,parent:Layer,xml:str):
        Layer.__init__(self,parent,xml)

    @property
    def filterType(self)->str:
        """
        supported types:
            brightness,contrast,rotate
        """
        return self._getProperty('type','?')

    @property
    def amount(self):
        """
        supported types:
            brightness,contrast,rotate,sharpen,unsharp_mask
        """
        return self._getPropertyPercent('amount',1.0)

    @property
    def edge(self)->str:
        """
        treatment for edges
            options: mirror,repeat,clamp,[color]

        useful for:
            convolve, expand_border, others?
        """
        return self._getProperty('edge','mirror')

    @property
    def add(self)->float:
        """
        add a constant to the convolved value
        useful, for instance, in shifting negative emboss values

        useful for:
            convolve
        """
        return float(self._getProperty('add',0))

    @property
    def divide(self)->float:
        """
        divide the convolved value by a constant

        useful for:
            convolve
        """
        divide=float(self._getProperty('divide',0))
        if divide==0:
            divide=None
        return divide

    @property
    def matrix(self)->list:
        """
        a 3x3 or 5x5 convolution matrix

        useful for:
            convolve
        """
        ret=[]
        matrix=self._getProperty('matrix','[[0,0,0],[0,1,0],[0,0,0]]').replace(' ','')
        if matrix.startswith('[['):
            matrix=matrix[1:-1]
        else:
            matrix=matrix
        matrix=matrix.split('[')[1:]
        size=None
        for row in matrix:
            row=row.split(']',1)[0].split(',')
            if (size is None and len(row) not in [5,3]) or size!=len(row):
                size=len(row)
                info=(matrix,len(row))
                raise SmartimageError(self,'Convolution matrix "%s" size %d not 3x3 or 5x5!'%info)
            ret.append([float(v) for v in row])
        if len(ret)!=size:
            info=(matrix,len(ret))
            raise SmartimageError(self,'Convolution matrix "%s" size %d not 3x3 or 5x5!'%info)
        return ret

    @property
    def channels(self)->str:
        """
        only apply the effect to the given channels

        useful for:
            convolve,others?
        """
        return self._getProperty('channels','rgba').lower()

    @property
    def modifierOpacity(self)->float:
        """
        the opacity of the modifier alone, for instance drop shadows
        """
        return self._getPropertyPercent('modifierOpacity',1.0)

    @property
    def blurRadius(self)->float:
        """
        supported types:
            gaussian_blur,box_blur,shadow,unsharp_mask
        """
        return float(self._getProperty('blurRadius',0))

    @property
    def threshold(self)->float:
        """
        supported types:
            unsharp_mask
        """
        return float(self._getProperty('threshold',0))

    def roi(self,image:PilPlusImage)->Union[PilPlusImage,None]:
        """
        the region of interest
        """
        # only certain transforms change the region of interest
        if self.filterType in ['shadow','blur','flip','mirror']:
            image=self._transform(image)
        return image

    def _transform(self,img):
        """
        For a list of more transformations available, see:
            http://pillow.readthedocs.io/en/latest/reference/ImageFilter.html
        """
        filterType=self.filterType
        if filterType=='shadow':
            offsX=10
            offsY=10
            blurRadius=self.blurRadius
            shadow=img.copy()
            control=ImageEnhance.Brightness(shadow)
            shadow=control.enhance(0)
            final=Image.new("RGBA",(img.width+abs(offsX),img.height+abs(offsX)))
            final.putalpha(int(self.modifierOpacity*255))
            dest=(int(max(offsX-blurRadius,0)),int(max(offsY-blurRadius,0)))
            final.alpha_composite(shadow,dest=dest)
            if blurRadius>0:
                final=final.filter(ImageFilter.GaussianBlur(radius=blurRadius))
            final.alpha_composite(img,dest=(max(-offsX,0),max(-offsY,0)))
            img=final
        elif filterType=='convolve':
            # TODO: make use of separable convoutions, fourier domain convolutions,
            #       and other speed-ups
            matrix=self.matrix
            ImageFilter.Kernel((len(matrix),len(matrix)),matrix,scale=self.divide,offset=self.add)
        elif filterType=='autocrop':
            # the idea is you cut off as many rows from each side that are all alpha=0
            raise NotImplementedError()
        elif filterType=='brightness':
            control=ImageEnhance.Brightness(img)
            control.amount=self.amount
        elif filterType=='contrast':
            control=ImageEnhance.Contrast(img)
            control.amount=self.amount
        elif filterType=='saturation':
            control=ImageEnhance.Color(img)
            control.amount=self.amount
        elif filterType=='blur':
            img=img.filter(ImageFilter.BLUR)#,self.amount)
        elif filterType=='gaussian_blur':
            blurRadius=self.blurRadius
            if blurRadius>0:
                img=img.filter(ImageFilter.GaussianBlur(radius=blurRadius))
        elif filterType=='box_blur':
            blurRadius=self.blurRadius
            if blurRadius>0:
                img.filter(ImageFilter.BoxBlur(radius=blurRadius))
        elif filterType=='unsharp_mask':
            ImageFilter.UnsharpMask(radius=self.blurRadius,
                percent=self.amount*100,threshold=self.threshold)
        elif filterType=='contour':
            img=img.filter(ImageFilter.CONTOUR,self.amount)
        elif filterType=='detail':
            img=img.filter(ImageFilter.DETAIL,self.amount)
        elif filterType=='edge_enhance':
            img=img.filter(ImageFilter.EDGE_ENHANCE,self.amount)
        elif filterType=='edge_enhance_more':
            img=img.filter(ImageFilter.EDGE_ENHANCE_MORE,self.amount)
        elif filterType=='emboss':
            img=img.filter(ImageFilter.EMBOSS,self.amount)
        elif filterType=='edge_detect':
            img=img.filter(ImageFilter.FIND_EDGES,self.amount)
        elif filterType=='smooth':
            img=img.filter(ImageFilter.SMOOTH,self.amount)
        elif filterType=='smooth_more':
            img=img.filter(ImageFilter.SMOOTH_MORE,self.amount)
        elif filterType=='sharpen':
            img=img.filter(ImageFilter.SHARPEN,self.amount)
        elif filterType=='invert':
            img=ImageOps.invert(img)
        elif filterType=='flip':
            img=ImageOps.flip(img)
        elif filterType=='mirror':
            img=ImageOps.mirror(img)
        elif filterType=='posterize':
            img=ImageOps.posterize(img)
        elif filterType=='solarize':
            img=ImageOps.solarize(img)
        else:
            raise SmartimageError(self,'Unknown modifier "%s"'%filterType)
        return img

    def renderImage(self,renderContext=None)->Union[PilPlusImage,None]:
        """
        WARNING: Do not modify the image without doing a .copy() first!
        """
        opacity=self.opacity
        if opacity<=0.0 or not self.visible:
            return None
        image=Layer.renderImage(self,renderContext)
        if image is not None:
            image=self._transform(image.copy())
            if self.opacity<1.0:
                adjustOpacity(image,opacity)
        return image
