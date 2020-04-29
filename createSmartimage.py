#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This creates a new smart image (usually by wrapping existing image(s))

It is totally standalone code that creates the zipfile directly
and illustrates how easy it is to manually roll a smartimage file.
"""
from typing import *
import os
from zipfile import *


def createSmartimage(filename:Union[str,None]=None,images:Union[str,Tuple[str],None]=None)->str:
    """
    This creates a new smart image (usually by wrapping existing image(s))

    It is totally standalone code that creates the zipfile directly
    and illustrates how easy it is to manually roll a smartimage file.

    :return: the name of the file created
    """
    if images is None:
        images=[]
    elif not isinstance(images,(list,tuple)):
        images=[images]
    if filename is None:
        if images:
            filename=images[0].rsplit(os.sep,1)[-1].split('.',1)[0]
        else:
            filename='new_image'
    if not filename.endswith('.simg'):
        filename=filename+'.simg'
    zf=ZipFile(filename,'w')
    si=[]
    si.append('<?xml version="1.0" encoding="UTF-8"?>')
    si.append('<smartimage>')
    addedImages={} # filename:zipname
    for img in images:
        zipname='images/'+img.rsplit(os.sep,1)[-1]
        addFile=True
        n=None
        while zipname in addedImages:
            addedPath=addedImages[zipname]
            if addedPath==img:
                # it's the same image, so don't add it, but simply use it
                addFile=False
                break
            # it's a different file so pick a new zipped name
            if n is None:
                n=1
                zipname=zipname.split('.')
                zipname="%s_%d%s"%(zipname[0],n,zipname[1])
            else:
                zipname=zipname.rsplit('_',1).split('.')
                zipname="%s_%d%s"%(zipname[0],n,zipname[1])
                n+=1
        # add the file to the zip
        if addFile:
            zf.write(img,zipname,ZIP_STORED)
        # add to the smartimage
        si.append('<image src="%s" />'%(zipname))
    si.append('</smartimage>')
    zf.writestr('smartimage.xml',(''.join(si)).encode('utf-8'),ZIP_DEFLATED)
    zf.close()
    return filename


def cmdline(args):
    """
    Run the command line
    
    :param args: command line arguments (WITHOUT the filename)
    """
    printhelp=False
    saveAsName=None
    images=[]
    for arg in args:
        if arg.startswith('-'):
            arg=[a.strip() for a in arg.split('=',1)]
            if arg[0] in ['-h','--help']:
                printhelp=True
            elif arg[0] in ['--saveAsName']:
                if len(arg)>1 and saveAsName:
                    saveAsName=arg[1]
            else:
                print('ERR: unknown argument "'+arg[0]+'"')
        else:
            images.append(arg)
    name=createSmartimage(saveAsName,images)
    print('Saved as "%s"'%name)
    if printhelp:
        print('Usage:')
        print('  createSmartimage.py [options] [images]')
        print('Options:')
        print('   --saveAsName=name ...... a name for the resulting smartimage (optional)')


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