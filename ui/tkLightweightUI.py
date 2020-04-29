#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This is a very lightweight UI for editing images.  You'll be done and off to Zanzibar before Photoshop could even boot up!
"""
import os
import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.ttk as ttk
from PIL import Image, ImageTk
from smartimage import *
from smartimage.imgTools import *
import time


HERE=os.path.abspath(__file__).rsplit(os.sep,1)[0]+os.sep


class FileWatcher(object):
    """
    A snazzy little tool to watch a filename for changes
    and notify us if it happens.
    """

    def __init__(self,filename):
        if os.path.isdir(filename):
            filename=filename+os.sep+'smartimage.xml'
        self.filename=filename
        self.lastModified=os.path.getmtime(filename)

    def isModified(self):
        modified=os.path.getmtime(self.filename)
        hasChanged=modified!=self.lastModified
        self.lastModified=modified
        return hasChanged

    def _watchFile(filename,callback):
        while True:
            time.sleep(0.25)
            if self.isModified():
                callback(filename)

    def watchFile(filename,callback):
        """
        Uses a thread to watch for file changes

        returns a thread object
        """
        import threading
        t=threading.Thread(target=self._watchFile,args=(callback))
        t.daemon=True
        t.start()
        return t


class TreeviewPanel(tk.Frame):
    """
    Display a treeview of image layers.  Get notified
    back whenever the selection changes.
    """

    def __init__(self, master, smartimage,viewer=None):
        tk.Frame.__init__(self,master)
        self.thumbnailSize=(50,50)
        self.thumbnailBG=backgrounds.checkerboard(self.thumbnailSize[0],self.thumbnailSize[1],color1=(102,102,102,255),color2=(153,153,153,255))
        self.smartimage=None
        self.viewer=viewer
        self._treeImages={}
        self.tree=ttk.Treeview(self)
        yScrollbar=ttk.Scrollbar(self,orient=tk.VERTICAL,command=self.tree.yview)
        xScrollbar=ttk.Scrollbar(self,orient=tk.HORIZONTAL,command=self.tree.xview)
        self.tree.configure(yscroll=yScrollbar.set,xscroll=xScrollbar.set)
        style=ttk.Style(master)
        style.configure('Treeview',rowheight=50)
        self.tree.heading('#0',text="Layer",anchor=tk.W)
        self.tree.bind("<Button-1>",self.OnClick)
        self.tree.bind("<Double-1>",self.OnDoubleClick)
        self.tree.grid(row=0,column=0)
        yScrollbar.grid(row=0,column=1,sticky=tk.NS)
        xScrollbar.grid(row=1,column=0,sticky=tk.EW)
        self.grid()
        self.setSmartimage(smartimage)

    def setSmartimage(self,smartimage):
        if not isinstance(smartimage,SmartImage):
            smartimage=SmartImage(smartimage)
        self.smartimage=smartimage
        iid=smartimage.id
        self.tree.delete(*self.tree.get_children())
        image=self.thumbnailForLayer(smartimage)
        photoImage=ImageTk.PhotoImage(image)
        self._treeImages[iid]=photoImage # this is necessary so photoImage is not deleted
        root_node=self.tree.insert('','end',iid,text="smartimage",open=True,image=photoImage)
        self.populate(root_node,smartimage)
        self.tree.selection_set(iid)
        self.tree.focus_set()
        self.tree.focus(iid)

    def thumbnailForLayer(self,layer):
        try:
            image=layer.renderImage()
        except Exception as e:
            print(e)
            return self.thumbnailBG
        if image==None:
            image=self.thumbnailBG
        else:
            image=image.copy()
            image.thumbnail(self.thumbnailSize)
            if image.mode=='RGBA':
                bg=self.thumbnailBG.copy()
                bg.alpha_composite(image)
                image=bg
        return image

    def populate(self,parent,layer):
        for child in layer.children:
            iid=child.id
            image=self.thumbnailForLayer(child)
            photoImage=ImageTk.PhotoImage(image)
            self._treeImages[iid]=photoImage # this is necessary so photoImage is not deleted
            oid=self.tree.insert(parent,'0',iid,text=child.name,open=False,image=photoImage)
            self.populate(oid,child)

    def OnClick(self, event):
        item = self.tree.identify('item', event.x, event.y)
        if self.viewer!=None:
            self.viewer.setImage(self.smartimage.imageByRef('@'+item))

    def OnDoubleClick(self, event):
        item = self.tree.identify('item', event.x, event.y)
        if self.viewer!=None:
            self.viewer.setImage(self.smartimage.imageByRef('@'+item))

    def onFileChanged(self,filename):
        self.setSmartimage(filename)


class ImagePanel(tk.Frame):
    """
    A scrollable panel whose only purpose in life is to display an image.
    """

    def __init__(self,master,smartimage,allowRaise):
        self.allowRaise=allowRaise
        self.smartimage=smartimage
        tk.Frame.__init__(self,master)
        frame=self
        self.canvas=tk.Canvas(frame,bg='#FFFFFF',width=300,height=300,scrollregion=(0,0,500,500))
        hbar=tk.Scrollbar(frame,orient=tk.HORIZONTAL)
        hbar.pack(side=tk.BOTTOM,fill=tk.X)
        hbar.config(command=self.canvas.xview)
        vbar=tk.Scrollbar(frame,orient=tk.VERTICAL)
        vbar.pack(side=tk.RIGHT,fill=tk.Y)
        vbar.config(command=self.canvas.yview)
        self.canvas.config(width=300,height=300)
        self.canvas.config(xscrollcommand=hbar.set,yscrollcommand=vbar.set)
        self.canvas.pack(side=tk.LEFT,expand=True,fill=tk.BOTH)
        self.setImage(smartimage)

    def setImage(self,image):
        if isinstance(image,Layer):
            if self.allowRaise:
                image=image.renderImage()
            else:
                try:
                    image=image.renderImage()
                except Exception as e:
                    messagebox.showerror(e.__class__.__name__,str(e))
                    return
        if image.mode=='RGBA':
            bg=backgrounds.checkerboard(image.width,image.height,color1=(102,102,102,255),color2=(153,153,153,255))
            bg.alpha_composite(image)
            image=bg
        self.canvas.delete("all")
        self.photoImage=ImageTk.PhotoImage(image)
        imagesprite=self.canvas.create_image(0,0,image=self.photoImage,anchor=tk.NW)
        self.canvas.config(scrollregion=(0,0,image.width,image.height))
        #self.canvas.config(width=image.width,height=image.height)

    def setSmartimage(self,smartimage):
        if not isinstance(smartimage,SmartImage):
            smartimage=SmartImage(smartimage)
        self.smartimage=smartimage
        self.setImage(smartimage)

    def onFileChanged(self,filename):
        self.setSmartimage(filename)


class EditPanel(tk.Frame):
    """
    This is a very lightweight UI for editing images.  You'll be done and off to Zanzibar before Photoshop could even boot up!
    """
    def __init__(self,master,smartimage,allowRaise):
        tk.Frame.__init__(self, master)
        self.smartimage=smartimage
        self.imageToolSplit=tk.PanedWindow(master,orient=tk.HORIZONTAL)
        self.imageToolSplit.pack(fill=tk.BOTH,expand=1)
        self.imageToolSplit.config(handlesize=10)
        self.imageToolSplit.config(sashwidth=5)
        self.imageToolSplit.config(sashrelief=tk.RAISED)
        self.imagePane=ImagePanel(self.imageToolSplit,smartimage,allowRaise)
        self.imageToolSplit.add(self.imagePane,stretch="always")
        self.treeviewPanel=TreeviewPanel(self.imageToolSplit,smartimage,viewer=self.imagePane)
        self.imageToolSplit.add(self.treeviewPanel)

    def setSmartimage(self,smartimage):
        if not isinstance(smartimage,SmartImage):
            smartimage=SmartImage(smartimage)
        self.smartimage=smartimage
        self.imagePane.setSmartimage(smartimage)
        self.treeviewPanel.setSmartimage(smartimage)

    def onFileChanged(self,filename):
        self.setSmartimage(filename)


def runUI(smartimage,mode='edit',allowRaise=False):
    """
    mode: 'edit', 'view', 'treeview'
    """
    if type(smartimage) in [str,str]:
        smartimage=SmartImage(smartimage)
    root = tk.Tk()
    root.iconbitmap(HERE+'..'+os.sep+'icon.ico')
    filename=smartimage.filename
    if filename==None:
        filename='Untitled'
    else:
        filename=filename.rsplit(os.sep,1)[-1]
    root.wm_title('smartimage - '+filename)
    if mode=='treeview':
        app = TreeviewPanel(root,smartimage)
    elif mode=='view':
        app = ImagePanel(root,smartimage,allowRaise)
    elif mode=='edit':
        app = EditPanel(root,smartimage,allowRaise)
    else:
        raise Exception('ERR: unknown ui mode "'+mode+'"')
    # notify the ui whenever the file on disk changes
    fw=FileWatcher(smartimage.filename)
    def q():
        if fw.isModified():
            app.onFileChanged(smartimage.filename)
        root.after(250,q)
    root.after(250,q)
    app.mainloop()


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
    printhelp=False
    if len(sys.argv)<2:
        printhelp=True
    else:
        allowRaise=False
        mode='edit'
        for arg in sys.argv[1:]:
            if arg.startswith('-'):
                arg=[a.strip() for a in arg.split('=',1)]
                if arg[0] in ['-h','--help']:
                    printhelp=True
                elif arg[0]=='--allowRaise':
                    allowRaise=True
                else:
                    print('ERR: unknown argument "'+arg[0]+'"')
            else:
                runUI(arg,mode,allowRaise)
    if printhelp:
        print('Usage:')
        print('  tkLightweightUI.py file.simg [options]')
        print('Options:')
        print('   --allowRaise ........ allow image errors to kick out of application')
        print('   --mode .............. ui mode (edit, view, treeview)')






