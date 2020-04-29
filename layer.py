# -*- coding: utf-8 -*-
"""
The base class for image layers
"""
from typing import *
from imageTools import *
from smartimage.smartimageXmlObject import SmartimageXmlObject
from smartimage.errors import SmartimageError
from smartimage.renderingContext import *


class Layer(SmartimageXmlObject,Bounds):
    """
    The base class for image layers
    """

    def __init__(self,parent:Union[None,'Layer']=None,xml:str='<group/>'):
        SmartimageXmlObject.__init__(self,parent,xml)
        self._children=None
        self._lastRenderedImage=None

    def __hash__(self)->int:
        """
        hash value for efficient sorting
        (based upon the element Id, since it is unique)
        """
        return hash(self.elementId)

    def __repr__(self)->str:
        #name=self.name
        #if name is not None:
        #    return 'Layer '+str(self.elementId)+' - "'+name+'"'
        return 'Layer '+str(self.elementId)

    def getLayer(self,idOrName:str)->'Layer':
        """
        fetch a layer with the given name or id

        :param idOrName: find the idOrName
        :param ignore: list of layers to ignore (prevent looping)
        """
        if idOrName[0]=='@':
            idOrName=idOrName[1:]
        if idOrName:
            l=self._getLayerById(idOrName)
            if l is None:
                l=self._getLayerByName(idOrName)
                if l is None:
                    # try all that again without case sensitivity
                    idOrName=idOrName.lower()
                    l=self._getLayerById(idOrName,True)
                    if l is None:
                        l=self._getLayerByName(idOrName,True)
        return l

    def _getLayerById(self,layerId:str,ignorecase:bool=False,fromRoot:bool=False)->'Layer':
        """
        fetch a layer with the given id

        :param layerId: find the id
        :param fromRoot: whether we are being scanned or the scanner
        """
        l=None
        #print('comparing id',layerId,self.elementId)
        if layerId==self.elementId:
            l=self
        elif ignorecase and str(self.elementId).lower()==layerId:
            l=self
        elif not fromRoot:
            l=self.root._getLayerById(layerId,ignorecase,True)
        else:
            for c in self.children:
                l=c._getLayerById(layerId,ignorecase,True)
                if l is not None:
                    break
        return l

    def _getLayerByName(self,name:str,ignorecase:bool=False,ignore:Union[bool,None]=None)->'Layer':
        """
        fetch a layer with the given name

        :param name: find the name (if ignorecase, must be lower cased)
        :param ignore: list of layers to ignore (prevent looping)
        """
        #print('comparing name',name,self.name)
        if ignore is None:
            ignore=[self]
        else:
            ignore.append(self)
        l=None
        if self.name==name:
            l=self
        elif ignorecase and self.name.lower()==name:
            l=self
        else:
            for c in self.children:
                if c not in ignore:
                    l=c._getLayerByName(name,ignorecase,ignore)
                    if l is not None:
                        break
        if l is None and self.parent is not None:
            l=self.parent._getLayerByName(name,ignorecase,ignore)
        return l

    @property
    def x(self)->float:
        """
        if value=="auto", then take on the child value
        """
        x=self._getProperty('x','auto')
        if x in ('','auto','None'):
            x=[child.x for child in self.children]
            if x:
                x=min(x)
            else:
                x=0
        else:
            try:
                x=float(x)
            except ValueError:
                raise SmartimageError(self,'Unable to convert x="%s" to float'%x)
            if x<0:
                x=self.w+x
        return x
    @x.setter
    def x(self,x):
        self._setProperty('x',x)
    @property
    def y(self)->float:
        """
        if value=="auto", then take on the child value
        """
        y=self._getProperty('y','auto')
        if y in ('','auto','None'):
            y=[child.y for child in self.children]
            if y:
                y=min(y)
            else:
                y=0
        else:
            try:
                y=float(y)
            except ValueError:
                raise SmartimageError(self,'Unable to convert y="%s" to float'%y)
            if y<0:
                y=self.h+y
        return y
    @y.setter
    def y(self,y):
        self._setProperty('y',y)
    @property
    def w(self)->float:
        """
        the current width
        """
        w=self._getProperty('w','auto')
        if w in ('','0','auto','None'):
            if self.children:
                w=[child.x+child.w for child in self.children]
                w=max(w)-self.x
            else:
                w=0
        else:
            try:
                w=float(w)
            except ValueError:
                raise SmartimageError(self,'Unable to convert w="%s" to float'%w)
        return w
    @w.setter
    def w(self,w):
        self._setProperty('w',w)
    @property
    def h(self)->float:
        """
        the current height
        """
        h=self._getProperty('h','auto')
        if h in ('','0','auto','None'):
            if self.children:
                h=[child.y+child.h for child in self.children]
                h=max(h)-self.y
            else:
                h=0
        else:
            try:
                h=float(h)
            except ValueError:
                raise SmartimageError(self,'Unable to convert h="%s" to float'%h)
        return h
    @h.setter
    def h(self,h):
        self._setProperty('h',h)

    @property
    def visible(self)->bool:
        """
        makes the layer visible
        """
        return self._getPropertyBool('visible','true')

    @property
    def detatched(self)->bool:
        """
        detaches the layer
        """
        return self._getPropertyBool('detatched',None)

    @property
    def rotation(self)->float:
        """
        rotatagtes the layer
        """
        return self._getPropertyFloat('rotation','0')

    @property
    def cropping(self)->list:
        """
        crop the layer
        """
        return self._getPropertyArray('crop',None)

    @property
    def relativeTo(self):
        """
        set the frame of reference for sizing, moving, etc
        """
        # TODO: dimensions need to account for this!
        return self._getProperty('relativeTo','parent')

    @property
    def opacity(self)->float:
        """
        the overall opacity of this layer
        """
        return self._getPropertyPercent('opacity',1.0)
    @opacity.setter
    def opacity(self,opacity):
        """
        the overall opacity of this layer
        """
        self._setProperty('opacity',str(opacity))

    @property
    def blendMode(self)->str:
        """
        available: (from imagechops module)
            'normal','darker','difference','add','add_mod','multiply',
            'and','or','screen','subtract','subtract_mod'
        """
        return self._getProperty('blendMode','normal')
    @blendMode.setter
    def blendMode(self,blendMode):
        self._setProperty('blendMode',blendMode)

    def _createChild(self,parent,xml)->'Layer':
        """
        create a child layer
        """
        child=None
        if xml==self.xml or xml.__class__.__name__ in ['_Comment']:
            pass
        elif xml.tag in ('form','color','select','preview','numeric'):
            # form elements do not belong to an image
            pass
        elif xml.tag=='text':
            from . import text
            child=text.TextLayer(parent,xml)
        elif xml.tag=='link':
            from . import link
            child=link.Link(parent,xml)
        elif xml.tag=='image':
            from . import image
            child=image.ImageLayer(parent,xml)
        elif xml.tag=='group':
            child=Layer(parent,xml)
        elif xml.tag=='modifier':
            from . import modifier
            child=modifier.Modifier(parent,xml)
        elif xml.tag=='solid':
            from . import solid
            child=solid.Solid(parent,xml)
        elif xml.tag=='texture':
            from . import texture
            child=texture.Texture(parent,xml)
        elif xml.tag=='pattern':
            from . import pattern
            child=pattern.Pattern(parent,xml)
        elif xml.tag=='particles':
            from . import particles
            child=particles.Particles(parent,xml)
        elif xml.tag=='numberspace':
            from . import numberspace
            child=numberspace.NumberSpace(parent,xml)
        elif xml.tag=='ext':
            from . import extension
            child=extension.ExtensionLayer(parent,xml)
        else:
            raise SmartimageError(self,'ERR: unexpected child element "%s"'%xml.tag)
        return child

    @property
    def children(self)->List['Layer']:
        """
        all of the children of the layer
        """
        if self._children is None:
            self._children=[]
            # NOTE: this loop is reversed so that the xml file has top layers first
            # (visually on top in an editor) like what we're used to in a gui like GIMP.
            childTags=self.xml.getchildren()
            #print('\nchildren of',self.xml.tag)
            #print('XML-',self.xml,childTags)
            for tag in reversed(childTags):
                #print('TAG=',tag.tag)
                child=self._createChild(self,tag)
                if child is not None:
                    self._children.append(child)
                #else:
                #\traise SmartimageError(self,'Null child element')
        return self._children

    @property
    def roi(self)->Union[PilPlusImage,None]:
        """
        "region of interest" used for smart resizing and possibly other things
        """
        ref=self._getProperty('roi')
        try:
            img=self.root.imageByRef(ref)
        except FileNotFoundError as e:
            raise SmartimageError(self,'Missing roi resource "%s"'%e.filename)
        return ref

    @property
    def normalMap(self)->Union[PilPlusImage,None]:
        """
        A 3d normal map, wherein red=X, green=Y, blue=Z (facing directly out from the screen)
        """
        ref=self._getProperty('normalMap',None)
        if ref is None:
            ref=normalMapFromImage(self.image)
        try:
            img=self.root.imageByRef(ref)
        except FileNotFoundError as e:
            raise SmartimageError(self,'Missing normalMap resource "%s"'%e.filename)
        return img

    @property
    def bumpMap(self)->Union[PilPlusImage,None]:
        """
        a grayscale bump map or heightmap.
        """
        ref=self._getProperty('bumpMap',None)
        if ref is None:
            ref=heightMapFromNormalMap(self.normalMap)
        try:
            img=self.root.imageByRef(ref)
        except FileNotFoundError as e:
            raise SmartimageError(self,'Missing bumpMap resource "%s"'%e.filename)
        return img

    def compareOutput(self,compareTo:Union[PilPlusImage,str],tolerance:float=0.99)->bool:
        """
        determine if the output of this layer matches an image

        this is used mainly for testing
        """
        rendered=self.renderImage()
        return compareImage(rendered,compareTo,tolerance)

    @property
    def image(self)->Union[PilPlusImage,None]:
        """
        Implemented by child classes
        """
        return None

    @property
    def mask(self)->Union[PilPlusImage,None]:
        """
        grayscale image to be used as layer mask
        it can also be an image with alpha component which will be INVERTED to use as mask!

        NOTE: the mask can either be a link to another file,

        TODO: this could be made smarter with imageTools
        """
        from PIL import Image
        ref=self._getProperty('mask')
        try:
            img=self.root.imageByRef(ref)
        except FileNotFoundError as e:
            raise SmartimageError(self,'Missing mask resource "%s"'%e.filename)
        if img is not None:
            if img.mode in ['RGBA','LA']:
                alpha=img.split()[-1]
                img=Image.new("RGBA",img.size,(0,0,0,255))
                img.paste(alpha,mask=alpha)
            img=img.convert("L")
        return img

    def renderImage(self,renderContext:RenderingContext=None)->Union[PilPlusImage,None]:
        """
        render this layer to a final image

        renderContext - used to keep track for child renders
            (Used internally, so no need to specify this)

        WARNING: Do not modify the image without doing a .copy() first!
        """
        if self.root.cacheRenderedLayers and not self.dirty:
            if self._lastRenderedImage is not None:
                return self._lastRenderedImage
        if renderContext is None:
            renderContext=RenderingContext()
        ret=renderContext.renderImage(self)
        if self.root.cacheRenderedLayers:
            self._lastRenderedImage=ret
        return ret

    @property
    def finalRoi(self)->Union[PilPlusImage,None]:
        """
        self.roi only with all children applied
        """
        image=self.roi
        for c in self.children:
            image=ImageChops.add(image,c.finalRoi)
        return image
