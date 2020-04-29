# -*- coding: utf-8 -*-
"""
This is a text layer
"""
import os
import struct
import urllib.request
import urllib.parse
import urllib.error
import textwrap
from PIL import Image,ImageFont,ImageDraw
import lxml.etree
from imageTools import *
from smartimage.layer import Layer
from smartimage.errors import SmartimageError


# TODO: select based on OS
DEFAULT_FONT=r'c:\windows\fonts\arial.ttf'
#DEFAULT_FONT='Helvetica'
#DEFAULT_FONT='sans-serif'


def fontSquirrelGet(fontName:str,cacheDir:str):
    """
    get a font from fontsquirrel

    :param fontName: the named font to fetch
    :param cacheDir: the location to cache fonts
    """
    fontName=fontName.replace(' ','-')
    url='https://www.fontsquirrel.com/fonts/download/'+fontName
    req=urllib.request.Request(url)
    try:
        response=urllib.request.urlopen(req)
        f=open(fontcache,'wb')
        f.write(response.read())
        f.close()
    except urllib.error.URLError as e:
        print(url)
        print(e)


def fontSquirrelPage(fontName:str,cacheDir:str):
    """
    get the page for a fontsquirrel font

    :param fontName: the named font to fetch
    :param cacheDir: the location to cache fonts
    """
    fontName=fontName.replace(' ','-')
    url='https://www.fontsquirrel.com/fonts/'+fontName
    ret=None
    req=urllib.request.Request(url)
    try:
        response=urllib.request.urlopen(req)
        ret=response.read()
    except urllib.error.URLError as e:
        print(url)
        print(e)
    return ret


def fontSquirrelLicense(fontName:str,cacheDir:str):
    """
    Retrieve the license for the given font as html

    :param fontName: the named font to fetch
    :param cacheDir: the location to cache fonts
    """
    page=fontSquirrelPage(fontName,cacheDir)
    if page is None:
        return None
    page=lxml.etree.fromstring(page)
    return page.xpath('//*[@id="panel_eula"]')[0]


def googleFontsGet(fontName:str,cacheDir:str):
    """
    download the font from google fonts

    :param fontName: the named font to fetch
    :param cacheDir: the location to cache fonts
    """
    font=None
    # try to download from google fonts
    fontcache=cacheDir+fontName
    if not os.path.exists(fontcache):
        # download the info file if we don't have one
        url='https://fonts.googleapis.com/css?family='+urllib.parse.quote_plus(fontName)
        req=urllib.request.Request(url)
        try:
            response=urllib.request.urlopen(req)
            f=open(fontcache,'wb')
            f.write(response.read())
            f.close()
        except urllib.error.URLError as e:
            print(url)
            print(e)
    if os.path.exists(fontcache):
        # peek in the info file and get the real url
        f=open(fontcache,'rb')
        url=f.read().decode('utf-8').split('url(',1)[-1].split(')',1)[0]
        f.close()
        fontcache=cacheDir+urllib.parse.quote_plus(url)
        if not os.path.exists(fontcache):
            # download the real font if we don't already have it
            req=urllib.request.Request(url)
            try:
                response=urllib.request.urlopen(req)
                f=open(fontcache,'wb')
                f.write(response.read())
                f.close()
            except urllib.error.URLError as e:
                print(url)
                print(e)
        font=fontcache
    return font

def downloadFont(fontName:str):
    """
    locate and download the named font

    :param fontName: the named font to fetch
    """
    cacheDir=os.path.abspath(__file__).rsplit(os.sep,1)[0]+os.sep+'font_cache'+os.sep
    font=googleFontsGet(fontName,cacheDir)
    # TODO: fontsquirrel not implemented
    #if font is None:
    #\tfont=fontSquirrelGet(fontName,cacheDir)
    return font


class TextLayer(Layer):
    """
    This is a text layer
    """

    def __init__(self,parent:Layer,xml:str):
        Layer.__init__(self,parent,xml)
        self._font=None

    @property
    def fontName(self)->str:
        """
        get the font name
        """
        return self._getProperty('font',None)
    @property
    def fontSize(self)->int:
        """
        get the font size
        """
        return int(self._getProperty('fontSize',24))
    @property
    def typeFace(self):
        """
        get the type face
        """
        return int(self._getProperty('typeFace',0))

    @property
    def color(self):
        """
        get the background color
        """
        return strToColor(self._getProperty('color','#000000'))
    @color.setter
    def color(self,color):
        if not isinstance(color,str):
            color=colorToStr(color)
        self._setProperty('color',color)

    @property
    def anchor(self)->str:
        """
        get the anchor point
        """
        return self._getProperty('anchor','left')
    @property
    def lineSpacing(self)->int:
        """
        get the spacing between repeats
        """
        return int(self._getProperty('lineSpacing',0))
    @property
    def align(self)->str:
        """
        get the horizontal alignment
        """
        return self._getProperty('align','left')
    @property
    def verticalAlign(self)->str:
        """
        get the vertical alignment
        """
        return self._getProperty('verticalAlign','top')

    @property
    def font(self)->str:
        """
        change to any TrueType or OpenType font

        TODO: check inside the zipfile for embedded fonts!

        if the font is installed on your system, will attempt to install it from
            fonts.google.com

        returns PIL font object
        """
        if self.fontName is not None:
            fontName=self.fontName
        else:
            fontName=DEFAULT_FONT
        if self._font is None:
            # first look in the zipped file
            for name in self.root.componentNames:
                name=name.rsplit('.',1)
                if name[0]==fontName:
                    if len(name)==1 or name[1] in ['ttf','otf','otc','ttc']:
                        name='.'.join(name)
                        component=self.root.getComponent(name)
                        self._font=ImageFont.truetype(component,self.fontSize,self.typeFace)
                        component.close()
                        break
        if self._font is None:
            # try the os
            try:
                self._font=ImageFont.truetype(fontName,self.fontSize,self.typeFace)
            except IOError:
                self._font=None
        if self._font is None:
            fontdata=downloadFont(fontName)
            if fontdata is not None:
                self._font=ImageFont.truetype(fontdata,self.fontSize,self.typeFace)
        if self._font is None:
            raise SmartimageError(self,'Cannot find font anywhere: "%s"'%fontName)
        return self._font

    @property
    def roi(self)->PilPlusImage:
        img=PilPlusImage(Image.new('L',self.size,0))
        d=ImageDraw.Draw(img)
        d.multiline_text((0,0),self.text,255,self.font,self.anchor,self.lineSpacing,self.align)
        return img

    @property
    def image(self)->PilPlusImage:
        text=self.text
        # create a fake image, ImageDraw to use for size calculation
        img=Image.new('L',(1,1))
        d=ImageDraw.Draw(img)
        # some sanity checking
        if not text:
            info=(self.name,self.root.filename,self.xml.sourceline)
            print('WARN: Layer "%s" has no text specified - %s line %d'%info)
            return None
        if self.w==0:
            size=d.textsize(text,font=self.font,spacing=self.lineSpacing)
            w,h=size
        else:
            # determine the text wrapping and final size
            w=self.w
            textWrapper=textwrap.TextWrapper()
            charSize=d.textsize('l',font=self.font,spacing=self.lineSpacing)[0]
            textWrapper.width=int(w/len(text)*charSize)
            size=d.textsize(text,font=self.font,spacing=self.lineSpacing)
            while size[0]>w and textWrapper.width>0:
                textWrapper.width-=1
                text=textWrapper.fill(self.text)
                size=d.textsize(text,font=self.font,spacing=self.lineSpacing)
            h=max(size[1],self.h)
        # determine vertical alignment position
        x=self.x
        y=self.y
        align=self.align
        verticalAlign=self.verticalAlign
        if verticalAlign=='top':
            pass
        elif verticalAlign=='bottom':
            y+=h-size[1]
        elif verticalAlign in ['center','middle']:
            y+=h/2-size[1]/2
        else:
            raise SmartimageError(self,'ERR: Unknown text vertical align mode "%s"'%verticalAlign)
        if align=='left':
            pass
        elif align=='right':
            x+=w-size[0]
        elif align in ['center','middle']:
            x+=w/2-size[0]/2
        else:
            raise SmartimageError(self,'Unknown text alignment mode "%s"'%align)
        # draw the stuff
        img=Image.new('RGBA',(int(w),int(h)),(128,128,128,0))
        d=ImageDraw.Draw(img)
        d.multiline_text((0,0),text,tuple(self.color),self.font,
            self.anchor,self.lineSpacing,self.align)
        return img