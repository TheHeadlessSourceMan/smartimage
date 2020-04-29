#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Modern zipped+xml image editor format
"""
from typing import *
import os
import io
import zipfile
try:
    # first try to use bohrium, since it could help us accelerate
    # https://bohrium.readthedocs.io/users/python/
    import bohrium as np
except ImportError:
    # if not, plain old numpy is good enough
    import numpy as np
import lxml
from backedObject import XmlBackedDocument
from smartimage.layer import *
from smartimage.form import Form


class SmartImage(XmlBackedDocument,Layer):
    r"""
    Modern zipped+xml image editor format

    The object acts as an array of pages/frames (array of 1 if it's just a simple image)

    Format:
        name: Smartimage
        description: Modern zipped+xml image editor format
        guid: {71a4d284-86eb-413a-810b-1c2d60d21326}
        #parentNames: pilFormats (???)
        actions: int=numPages # the number of pages
        actions: int=numFrame # the number of frames
        actions: setVariable(str name,str value) # assign a variable
        actions: varUi() # launch a variable setter ui
        actions: show() # show the final output
        magicNumber: 0,PK
        magicNumber: 0,<
        mimeTypes: image/xml+smartimage
        filenamePatterns: *.simg
        filenamePatterns: *.simt
        iconLocation: C:\backed_up\computers\formats\smartimage\icon.ico
    """

    def __init__(self,filename:str=None,xmlName:str='smartimage.xml',topSmartimage=None):
        Layer.__init__(self,None,'<smartimage/>')
        XmlBackedDocument.__init__(self,'<smartimage/>',self)
        self._filename=None
        self._nextId=None
        self._moreComponents={}
        self._loaded=False
        self._hasRunUi=False
        self._variables=None
        self._varAuto=[]
        self._zipfile=None
        self.textAlignment=None
        if topSmartimage is None:
            # we are the top, so we'll take care of the peer list
            # (otherwise, we'll access self._topSmartimage._peerSmartimages)
            self._peerSmartimages={}
        if topSmartimage is None:
            self._topSmartimage=self
        else:
            self._topSmartimage=topSmartimage
        self.autoUi=True
        self.load(filename,xmlName)
        self.cacheRenderedLayers=True # trade memory for speed

    # TODO: remove?
    @property
    def variables(self):
        """
        get the state of all variables in play
        """
        f=self.form
        if f is None:
            return []
        return f.children
        # if self._variables is None:
            # self._variables=OrderedDict()
            # for variable in self.xml.xpath('//*/variable'):
                # variable=Variable(self,self,variable)
                # self._variables[variable.name]=variable
        # return self._variables

    @property
    def form(self)->'Form':
        """
        get the main ui form of this document
        """
        for f in self.forms:
            if not f.hidden:
                return f
        return None

    @property
    def forms(self)->Union['Form']:
        """
        get all of the forms in this document
        """
        ret=[]
        forms=self.xml.xpath('//*/form')
        for form in forms:
            ret.append(Form(self,form))
        return ret

    @property
    def numPages(self)->int:
        """
        how many pages are in the animation
        """
        return len(self.xml.xpath('//*/page'))

    @property
    def numFrames(self)->int:
        """
        how many frames are in the animation
        """
        return len(self.xml.xpath('//*/frame'))

    @property
    def page(self,pageNumber:int)->'Layer':
        """
        if this is a multipage document, get the given page number
        """
        pages=self.xml.xpath('//*/page')
        if not pages and pageNumber==0:
            return self
        return pages[pageNumber]

    @property
    def frame(self,frameNumber:int)->'Layer':
        """
        if this is an animation, get a given frame number
        """
        frames=self.xml.xpath('//*/frame')
        return frames[frameNumber]

    def __len__(self)->int:
        """
        how many pages or frames this image consists of
        """
        p=self.numPages
        f=self.numFrames
        if p>1:
            if f>1:
                info=(self.filename,self.page[0].xml.sourceline,self.frame[0].xml.sourceline)
                raise Exception("File can't contain both pages and frames! %s lines %d and %d"%info)
            return p
        if f>1:
            return f
        return 1

    def __getitem__(self,idxOrSlice:Union[int,Tuple[int,int]])->Union['Layer',None]:
        """
        get a page or frame by idx
        """
        ret=None
        p=self.numPages
        f=self.numFrames
        if f==0 and p==0:
            return self
        if isinstance(idxOrSlice,tuple): # it's a slice
            start,end=idxOrSlice
            if start<0:
                start+=self.__len__()
            if end<0:
                end+=self.__len__()
            ret=[]
            if f>p:
                for idx in range(start,end):
                    ret.append(self.frame[idx])
            else:
                for idx in range(start,end):
                    ret.append(self.page[idx])
        else:
            if f>p:
                ret=self.frame[idxOrSlice]
            else:
                ret=self.page[idxOrSlice]
        return ret

    def getComponent(self,name:str):
        """
        returns a file-like object for the given name
        """
        f=None
        if name in self._moreComponents:
            return io.TextIO(self._moreComponents[name])
        if self._filename is not None:
            if os.path.isdir(self._filename):
                filename=os.path.join(self._filename,name)
                f=open(filename,'rb')
            elif self._filename.endswith(os.sep+'smartimage.xml'):
                filename=os.path.join(self._filename.rsplit(os.sep,1)[0],name)
                f=open(filename,'rb')
            else:
                if self._zipfile is None:
                    self._zipfile=zipfile.ZipFile(self._filename)
                f=self._zipfile.open(name)
        if f is None:
            if name=='smartimage.xml':
                xml=r"""<?xml version='1.0'?><smartimage/>"""
                f=io.BinaryIO(xml.encode('utf-8'))
        return f

    def getPeerSmartimage(self,xmlName:str)->'Smartimage':
        """
        get another smartimage .xml embedded in this file
        """
        while xmlName[0]=='@':
            xmlName=xmlName[1:]
        xmlName=xmlName.split('.')[0]+'.xml'
        peerSmartimages=self._topSmartimage._peerSmartimages
        if xmlName not in peerSmartimages:
            self._peerSmartimages[xmlName]=SmartImage(self._filename,xmlName,self._topSmartimage)
        return peerSmartimages[xmlName]

    def getItemByFilename(self,name:str,nameHint:str='',nofollow:Union[bool,None]=None):
        """
        get an item that resides in another smartimage

        :param name: should be something like:
            @filename.xml.itemId
            @filename.xml.name
            @filename.itemId
            @subfolder/filename.itemId
        :param nameHint: used as a default when getting attributes such as
                <image file="@layerId">
            means
                <image file="@layerId.result">
            (wherein nameHint="result")
        :param nofollow: used internally to prevent loops

        :return: the item object or None if not found
        """
        item=None
        if nofollow is None:
            nofollow=[]
        while name[0]=='@':
            name=name[1:]
        name=name.split('.')
        if len(name)>1 and name[1]=='xml': # they included the file extension
            filename=name[0]
            if len(name)>2:
                name='.'.join(name[2:])
            else:
                name=''
        else: # they did not include the file extension
            filename=name[0]
            if len(name)>1:
                name='.'.join(name[1:])
            else:
                name=''
        sImg=self.getPeerSmartimage(filename)
        if sImg is not None:
            item=sImg._dereference(name,nameHint,nofollow=nofollow)
        return item

    def getNextId(self)->str:
        """
        take the next unused id number
        """
        if self._nextId is None:
            component=self.getComponent('smartimage.xml')
            data=component.read().decode('utf-8')
            component.close()
            first=True
            maxid=1
            for idTag in data.split('id="'):
                if first:
                    first=False
                else:
                    try:
                        idTag=int(idTag.split('"',1)[0])
                        if idTag>maxid:
                            maxid=idTag
                    except ValueError: # if the id is not an integer
                        pass
            self._nextId=maxid+1
        idTag=self._nextId
        self._nextId+=1
        #print 'GENERATED ID:',idTag
        return idTag

    def imageByRef(self,ref:str,visitedLayers=None)->'PilPlusImage':
        """
        grab an image by reference
        ref - one of:
            filename
            #id

        WARNING: Do not modify the image without doing a .copy() first!
        """
        ret=None
        if visitedLayers is None:
            visitedLayers=[]
        if ref is None:
            return None
        if ref.startswith('@'):
            l=self.getLayer(ref[1:])
            if l is None:
                raise Exception('ERR: Missing reference to "'+ref+'"')
            return l.renderImage()
        component=self.root.getComponent(ref)
        if component is not None:
            ret=PilPlusImage(component)
            #component.close() NOTE: PIL will handle this when it's ready
        return ret

    @property
    def componentNames(self)->List[str]:
        """
        get the names of the components in this file
        """
        ret={}
        for name in self._moreComponents:
            ret[name]=None
        if self._filename is None:
            pass
        elif os.path.isdir(self._filename):
            for name in os.listdir(self._filename):
                ret[name]=None
        else:
            if self._zipfile is None:
                self._zipfile=zipfile.ZipFile(self._filename)
            for name in os.listdir(self._zipfile.namelist()):
                ret[name]=None
        return ret.keys()

    @property
    def xml(self)->Union[lxml.etree.Element,None]:
        """
        get the xml tree of the smartimage
        """
        if self._xml is None:
            component=self.getComponent('smartimage.xml')
            if component is not None:
                self.decode(component.read())
                component.close()
            else:
                return None
        if hasattr(self._xml,'getroot'):
            self._xml=self._xml.getroot()
        si=self._xml
        while True:
            si=si.xpath('./smartimage')
            if not si:
                break
            if len(si)>1:
                vals=(self.filename,si[1].sourceline)
                raise Exception('More than one <smartimage> tag in file %s line %d'%vals)
            si=si[0]
            self._xml=si
        return self._xml

    def load(self,filename:str,xmlName:str='smartimage.xml'):
        """
        load an image

        :param filename: the name of the file to load - can also take most common URLs
        :param xmlName: the name of the starting smartimage within the file
        """
        self._loaded=False
        self._xml=None
        self._zipfile=None
        self.currentFont=None
        self.lineSpacing=0
        self.textAlignment='left'
        self._filename=filename
        self.xmlName=xmlName

    def addComponent(self,internalFileName:str,data:Union[str,bytes,bytearray],overwrite:bool=True):
        """
        Add a new component to the file

        :param overwrite: whether to overwrite an existing file
            if False, then will come up with a unique file name

        :returns: the name of the filename saved
        """
        fn=internalFileName
        if not overwrite:
            internalFileName=internalFileName.rsplit('.')
            internalFileName[0]=internalFileName[0]+' ('
            internalFileName[1]=')'+internalFileName[1]
            i=1
            while fn in self.componentNames:
                fn=internalFileName[0]+str(i)+internalFileName[1]
        self._moreComponents[fn]=data
        return fn

    def save(self,filename:Union[str,None]=None):
        """
        Save this image.

        If the filename is something other than a smartimage
        (eg. a .png file) then will save the rendered output.

        :param filename: the filename to save.  If unspecified,
            save as the currently loaded filename
        """
        self.varUi(force=False)
        if filename is None:
            filename=self._filename
        extn=filename.rsplit(os.sep,1)[-1].rsplit('.',1)
        if len(extn)<2 or extn in ['zip','simg','simt']:
            zf=zipfile.ZipFile(filename,'w')
            for name in self.componentNames:
                component=self.getComponent(name)
                if name.rsplit('.') in ['xml']:
                    compress_type=zipfile.ZIP_DEFLATED
                else:
                    compress_type=zipfile.ZIP_STORED
                zf.writestr(name,component.read().decode('utf-8'),compress_type)
                component.close()
            zf.close()
        else:
            result=self.renderImage()
            if result is None:
                print('ERR: No output to save.')
            elif result.size==(0,0):
                print('ERR: Unable to save 0x0 pixel image.')
            else:
                result.save(filename)

    def setVariable(self,name:str,value:Any)->NoReturn:
        """
        simply set a variable
        """
        self.variables[name].value=value

    def varFile(self,valuefile:str,name:Union[str,None]=None):
        """
        value and name are in reverse order of what is normally expected
        the reason is you can leave off the name and allow smartimage to guess!
        """
        valuetype='file'
        data=valuefile
        if valuefile.rsplit('.') in ['txt']:
            f=open(valuefile,'r')
            data=f.read().decode('utf-8').strip()
            if data.find('\n')>=0:
                valuetype='textarea'
            else:
                valuetype='text'
        if name is None:
            for k,v in list(self.variables.items()):
                if k in self._varAuto:
                    continue
                if v.uitype==valuetype:
                    self._varAuto.append(k)
                    v.value=data
                    break
        else:
            self.variables[name].value=data

    def hasUserVariables(self)->bool:
        """
        if there are variables that can be edited
        """
        ret=False
        for variable in self.variables:
            if not variable.hidden:
                ret=True
                break
        return ret

    def varUi(self,force:bool=True)->NoReturn:
        """
        open a user interface to edit the variables

        :param force: force the ui to show up (default is to only show if there are values missing)
        """
        if force or (self.autoUi and not self._hasRunUi and self.hasUserVariables()):
            self._hasRunUi=True
            from .ui.tkVarsWindow import runVarsWindow
            runVarsWindow(self.variables,self._filename)

    def renderImage(self,renderContext:Union[None,'RenderingContext']=None)->PilPlusImage:
        """
        NOTE: you probably don't want to call directly, but rather do a
            smartimage[0].renderImage() just to make sure you work with
            multi-page and multi-frame documents.

        WARNING: Do not modify the image without doing a .copy() first!
        """
        self.varUi(force=False)
        return Layer.renderImage(self,renderContext)

    def smartsize(self,size:Tuple[int,int],useGolden:bool=False):
        """
        returns an image smartly cropped to the given size

        :param size: the size to change to
        :param useGolden: TODO: try to position regions of interest on golden mean
        """
        image=self.image
        if image is None:
            return image
        if image.size[0]<1 or image.size[1]<1:
            raise Exception("Image is busted. ",image.size)
        roi=self.roi
        resize=1.0 # percent
        if size[0]!=image.size[0]:
            resize=size[0]/max(image.size[0],1)
        if size[1]!=image.size[1]:
            resize=max(resize,size[1]/max(image.size[1],1))
        # TODO: do I want to scale up the image directly,
        #   or get smart about oversizing and using region of interest??
        if resize!=1.0:
            newsize=(int(round(image.size[0]*resize)),int(round(image.size[1]*resize)))
            image=image.resize(newsize)
            roi=roi.resize(newsize)
        # crop in on region of interest
        # for now, simply find the best place in the lingering dimension to crop
        if newsize[0]==size[0]:
            if newsize[1]!=size[1]:
                # width matches, crop height
                d=int(size[1])
                a=np.sum(roi,axis=1) # or use mean
                for u in range(len(a)-d):
                    a[u]=np.sum(a[u:u+d])
                a=a[0:-d]
                idx=np.argmax(a)
                cropTo=(0,idx,size[0],idx+size[1])
                image=image.crop(cropTo)
        else:
            # height matches, crop width
            d=int(size[0])
            a=np.sum(roi,axis=0) # or use mean
            for u in range(len(a)-d):
                a[u]=np.sum(a[u:u+d])
            a=a[0:-d]
            idx=np.argmax(a)
            cropTo=(idx,0,idx+size[0],size[1])
            image=image.crop(cropTo)
        return image


def registerPILPligin()->NoReturn:
    """
    Register smartimage with PIL (the Python Imaging Library)
    """
    from PIL import ImageFile
    class SmartImageFile(ImageFile.ImageFile,SmartImage):
        """wrapper"""
        def __init__(self):
            self.smartimage=None
        def _open(self):
            "opener"
            try:
                self.smartimage=self.load(self.fp)
            except:
                raise SyntaxError("Not a SmartImage file")
    def _accept(prefix):
        return prefix[:2]==b"PK" or prefix[:1]==b"<"
    def _save(smartImageFile,filename):
        smartImageFile.save(filename)
    formatName='SmartImage'
    Image.register_open(formatName,SmartImageFile,_accept)
    Image.register_save(formatName,_save)
    Image.register_extension(formatName,".simg")
    Image.register_extension(formatName,".simt")
    Image.register_mime(formatName,"image/xml+smartimage")
    print('registered PIL plugin.')


def registerPlugins()->NoReturn:
    """
    Register SmartImage as a plugin to all known image programs
    """
    registerPILPligin()


def cmdline(args):
    """
    Run the command line
    
    :param args: command line arguments (WITHOUT the filename)
    """
    printhelp=False
    didSomething=False
    if len(args)<1:
        printhelp=True
    else:
        didOutput=False
        simg=None
        for arg in args:
            if arg.startswith('-'):
                arg=[a.strip() for a in arg.split('=',1)]
                if arg[0] in ['-h','--help']:
                    printhelp=True
                    didSomething=True
                elif arg[0]=='--smartsize':
                    didSomething=True
                    arg[1]=arg[1].split('=',1)
                    size=[float(x.strip()) for x in arg[1][0].split(',')]
                    img=simg.smartsize(size)
                    if len(arg[1])>1:
                        img.save(arg[1][1])
                    else:
                        img.show()
                elif arg[0] in ['--image','--show']:
                    didSomething=True
                    didOutput=True
                    if len(arg)>1:
                        pages=len(simg)
                        if pages>1:
                            filename=arg[1].split('.',1)
                            digits=len(str(pages))
                            fileFormat=filename[0]+r'_{:0'+digits+'d}.'+filename[1]
                            for idx in range(pages):
                                img=simg[idx].renderImage()
                                img.save(fileFormat.format(idx))
                        else:
                            img=simg[0].renderImage()
                            img.save(arg[1])
                    else:
                        img=simg[0].renderImage()
                        img.show()
                        import time
                        #while True:
                        time.sleep(1)
                elif arg[0]=='--roi':
                    didSomething=True
                    didOutput=True
                    img=simg.roi
                    if len(arg)>1:
                        img.save(arg[1])
                    else:
                        img.show()
                elif arg[0]=='--save':
                    didSomething=True
                    didOutput=True
                    simg.save(arg[1])
                elif arg[0]=='--testfont':
                    didSomething=True
                    didOutput=True
                    print(arg[1], end=' ')
                    simg.setFont(arg[1])
                elif arg[0]=='--variables':
                    didSomething=True
                    didOutput=True
                    for variable in simg.variables.values():
                        val=variable.value+'\n\t'+variable.description
                        print(variable.name+'('+variable.uitype+') = '+val)
                elif arg[0]=='--set':
                    didSomething=True
                    simg.setVariable(*arg[1].split('=',1))
                elif arg[0]=='--varfile':
                    didSomething=True
                    vf=arg[1].split('=',1)
                    if len(vf)>1:
                        simg.varFile(vf[1],vf[0])
                    else:
                        simg.varFile(vf[1])
                elif arg[0]=='--varui':
                    didSomething=True
                    simg.varUi()
                elif arg[0]=='--noui':
                    simg.autoUi=False
                elif arg[0]=='--registerPlugins':
                    registerPlugins()
                else:
                    print('ERR: unknown argument "'+arg[0]+'"')
            else:
                didSomething=True
                simg=SmartImage(arg)
    if not didSomething:
        print('ERR: Command accomplished nothing!\n')
        printhelp=True
    elif simg is not None and not didOutput:
        print('WARN: No output captured.  I\'m assuming you want to show the result, so here goes.')
        img=simg[0].renderImage()
        img.show()
    if printhelp:
        print('Usage:')
        print('  smartimage.py file.simg [options]')
        print('Options:')
        print('   --smartsize=w,h[=filename] .... smartsize the image.')
        print('         if no filename, show in a window')
        print('   --show ........................ same as --image')
        print('         (this is also the default if no output is selected)')
        print('   --image[=filename] ............ get the base image. if no filename,')
        print('         show in a window')
        print('         if multi-image or multi-frame, modify filename to be a numbered sequence')
        print('   --roi[=filename] .............. get the region of interest image.')
        print('         if no filename, show in a window')
        print('   --save=filename ............... save out the .simg as another file name')
        print('   --testfont=fontname ........... try to fetch the given font')
        print('   --variables ................... list all variables')
        print('   --set=name=value .............. set a variable')
        print('   --varui ....................... manually start user interface now')
        print('   --noui ........................ do not bring up a user interface')
        print('         (useful when setting vars manually)')
        print('   --varfile[=name]=value ........ populate a variable based on a filename')
        print('         if name is omitted, attempt to fill in variables smartly')
        print('   --registerPlugins ............. Register SmartImage as a plugin')
        print('         to all known image programs')


if __name__ == '__main__':
    import sys
    # Use the Psyco python accelerator if available
    # See:
    #\t http://psyco.sourceforge.net
    try:
        import psyco
        psyco.full() # accelerate this program
    except ImportError:
        pass
    cmdline(sys.argv[1:])