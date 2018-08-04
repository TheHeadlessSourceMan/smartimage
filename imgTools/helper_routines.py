#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This is a grab bag for handy helper routines
"""
from imageRepr import *
	

def clampImage(img,minimum=None,maximum=None):
	"""
	Clamp an image's pixel to a valid color range
	
	:param img: clamp a numpy image to valid pixel values can be a PIL image for "do nothing"
	:param minimum: minimum value to clamp to (default is 0)
	:param maximum: maximum value to clamp to (default is the maximum pixel value)
	"""
	if type(img)!=np.ndarray:
		if minimum!=None and minimum!=0 and maximum!=None and maximum!=255:
			return img
		img=numpyArray(img)
	if isFloat(img):
		minval=0.0
		maxval=1.0
	else:
		minval=0
		maxval=255
	if minimum==None:
		minimum=minval
	if maximum==None:
		maximum=maxval
	return np.where(img<minimum,minval,np.where(img>maximum,maxval,img))
	
def normalize(img):
	"""
	squash the image to fit in range 0.0 to 1.0
	"""
	img=img-img.min()
	imax=img.max()
	if imax!=0:
		img=img/imax
	return img
	
	
def deltaFromGray(img):
	"""
	returns an image differenced from gray
	"""
	return normalize(abs(img-0.5))

	
def valueRotate(img,amount=0.5):
	"""
	Rotate the values, wrapping around at the beginning
	"""
	return np.mod(np.clip(img,0.0,1.0)+amount,1.0)
	
	
def flip90(src):
	return np.transpose(src)
	
	
def highlights(img,threshold=0.9):
	"""
	return a mask of all highlights
	"""
	return np.where(img<threshold,0,img)
	
	
def shadows(img,threshold=0.1):
	"""
	return a mask of all shadows
	"""
	return np.where(img>threshold,0,1-img)
	

def distort(img,points,r=1):
	"""
	morph an image to fit the given points
	"""
	data=((f[0],f[1]) for f,t in points)
	img.transform(size,Image.MESH,data)
	
	
def rolling_window(a, shape):  # rolling window for 2D array
    s = (a.shape[0] - shape[0] + 1,) + (a.shape[1] - shape[1] + 1,) + shape
    strides = a.strides + a.strides
    return np.lib.stride_tricks.as_strided(a, shape=s, strides=strides)
	
	
def applyFunctionToPatch(fn,a,patchSize=(3,3)):
	# get all patchSize mattrices possible by sliding a patchSize window across the array
	w=rolling_window(a,patchSize)
	v=np.vectorize(fn,signature='(m,n)->(k,l)')
	if False:
		marginX=(patchSize[0]-1)/2
		marginY=(patchSize[1]-1)/2
		a2=np.array([])
		for x in range(marginX,a.shape[0]-marginX):
			for y in range(marginY,a.shape[1]-marginY):
				v(a[x-marginX:x+marginX+1,y-marginY:y+marginY+1])
	w.flags.writeable=True
	r=v(w)
	return r


def getHistogram(img,channel='V',invert=False):
	"""
	Gets a histogram for the given image
	
	:param channel: can be V,R,G,B,A, or RGB
		if single channel, returns a simple black and white image
		if RGB, returns all three layered together in a color image
	:param invert: do a white histogram on black, rather than the usual black on white
		
	:return pilImage: always grayscale, unless RGB, then an RGB image with each channel as its name
	"""
	import PIL.ImageDraw
	if len(channel)==1:
		size=(255,255)
		if invert:
			bg=0
			fg=255
		else:
			fg=0
			bg=255
		ch=getChannel(img,channel)
		out=Image.new("L",size,bg)
		draw=PIL.ImageDraw.Draw(out) 
		hist=ch.histogram()
		histMax=max(hist)
		yScale=float(size[1])/histMax
		for i in range(len(hist)):
			val=hist[i]
			if val>0:
				draw.line((i,size[1],i,size[1]-(val*yScale)),fill=fg)        
	elif channel=='RGB':
		out=PIL.Image.merge('RGB',(
			getHistogram(img,'R',invert==False),
			getHistogram(img,'G',invert==False),
			getHistogram(img,'B',invert==False)
			))   
	else:
		raise Exception('not a valid channel')
	return out
	

def compareImage(img1,img2,tolerance=0.99999):
	"""
	images can be a pil image, rgb numpy array, url, or filename
	tolerance - a decimal percent, default is five-nines
	"""
	img1,img2=makeSameMode([defaultLoader(img1),defaultLoader(img2)])
	img1,img2=numpyArray(img1),numpyArray(img2)
	if img1.shape!=img2.shape:
		# if they're not even the same size, never mind, then
		return False
	return np.allclose(img1,img2,rtol=tolerance)
	
	
def preview(img):
	"""
	this is a utility to do image previews
	
	It was created because stinking photoshop always took over the pil Image.show()
	
	TODO: this belongs in a different file
	"""
	mode='pilShow'
	#mode='save'
	#mode='windowsPhotoViewer'
	# ------
	img=pilImage(img)
	if mode=='pilShow':
		pilImage(img).show()
	elif mode=='save':
		path=os.path.abspath('tmp.png')
		img.save(path)
	elif mode=='windowsPhotoViewer':
		if False:
			for dllPath in [r'%ProgramFiles%\Windows Photo Viewer',r'%ProgramFiles%\Windows Photo Gallery']:
				if os.path.exists(dllPath):
					break			
			# %SystemRoot%\System32\rundll32.exe "%ProgramFiles%\Windows Photo Gallery\PhotoViewer.dll", ImageView_Fullscreen %1
			dllPath=r'C:\Program Files\Windows Photo Gallery'
			cmd=r'%SystemRoot%\System32\rundll32.exe "'+dllPath+r'\PhotoViewer.dll", ImageView_Fullscreen "'+path+'"'
			print cmd
			po=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			out,err=po.communicate()
			print out,err
		else:
			cmd=r'"C:\Program Files\Windows Photo Gallery\WindowsPhotoGallery.exe" "'+path+'"'
			print cmd
			po=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			out,err=po.communicate()
			print out,err
		time.sleep(2.5)
		os.remove(path)


if __name__ == '__main__':
	import sys
	# Use the Psyco python accelerator if available
	# See:
	# 	http://psyco.sourceforge.net
	try:
		import psyco
		psyco.full() # accelerate this program
	except ImportError:
		pass
	printhelp=False
	if len(sys.argv)<2:
		printhelp=True
	else:
		for arg in sys.argv[1:]:
			if arg.startswith('-'):
				arg=[a.strip() for a in arg.split('=',1)]
				if arg[0] in ['-h','--help']:
					printhelp=True
				elif arg[0]=='--histogram':
					mode='RGB'
					if len(arg)>1:
						mode=arg[1]
					hist=getHistogram(img,mode)
					hist.show()
				elif arg[0]=='--compare':
					print compareImage(img,arg[1])
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				img=defaultLoader(arg)
	if printhelp:
		print 'Usage:'
		print '  helper_routines.py image.jpg [options]'
		print 'Options:'
		print '   --histogram[=RGB] ........ possible values are V,R,G,B,A,or RGB'
		print '   --compare=img2.jpg ....... compares to another image (useful for testing)'
		print 'Notes:'
		print '   * All filenames can also take file:// http:// https:// ftp:// urls'