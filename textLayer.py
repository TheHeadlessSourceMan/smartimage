#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This is a text layer
"""
import os
from layer import *
import struct
import textwrap
from PIL import ImageFont, ImageDraw
import urllib,urllib2


def fontSquirrelGet(fontName,cachedir):
	fontName=fontName.replace(' ','-')
	url='https://www.fontsquirrel.com/fonts/download/'+fontName
	req=urllib2.Request(url)
	try:
		response=urllib2.urlopen(req)
		print dir(response)
		raise NotImplementedError()
		f=open(fontcache,'wb')
		f.write(response.read())
		f.close()
	except urllib2.URLError,e:
		print url
		print e
		
def fontSquirrelPage(fontName,cachedir):
	fontName=fontName.replace(' ','-')
	url='https://www.fontsquirrel.com/fonts/'+fontName
	ret=None
	req=urllib2.Request(url)
	try:
		response=urllib2.urlopen(req)
		ret=response.read()
	except urllib2.URLError,e:
		print url
		print e
	return ret
		
def fontSquirrelLicense(fontName,cachedir):
	"""
	Retrieve the license for the given font as html
	"""
	page=fontSquirrelPage(fontName,cachedir)
	if page==None:
		return None
	page=lxml.etree(page)
	return lxml.xpath('//*[@id="panel_eula"]')[0]
	

def googleFontsGet(fontName,cachedir):
	font=None
	# try to download from google fonts
	fontcache=cachedir+self.fontName
	if not os.path.exists(fontcache):
		# download the info file if we don't have one
		url='https://fonts.googleapis.com/css?family='+urllib.quote_plus(self.fontName)
		req=urllib2.Request(url)
		try:
			response=urllib2.urlopen(req)
			f=open(fontcache,'wb')
			f.write(response.read())
			f.close()
		except urllib2.URLError,e:
			print url
			print e
	if os.path.exists(fontcache):
		# peek in the info file and get the real url
		f=open(fontcache,'rb')
		url=f.read().split('url(',1)[-1].split(')',1)[0]
		f.close()
		fontcache=cachedir+urllib.quote_plus(url)
		if not os.path.exists(fontcache):
			# download the real font if we don't already have it
			req = urllib2.Request(url)
			try:
				response = urllib2.urlopen(req)
				f=open(fontcache,'wb')
				f.write(response.read())
				f.close()
			except urllib2.URLError,e:
				print url
				print e
		self._font=ImageFont.truetype(fontcache,self.fontSize,self.typeFace)
	
def downloadFont(fontName):
	cachedir=os.path.abspath(__file__).rsplit(os.sep,1)[0]+os.sep+'font_cache'+os.sep
	font=googleFontsGet(fontName,cachedir)
	if font==None:
		font=fontSquirrelGet(fontName,cachedir)
	return font

class TextLayer(Layer):
	"""
	This is a text layer
	"""

	def __init__(self,docRoot,parent,xml):
		Layer.__init__(self,docRoot,parent,xml)
		self._font=None

	@property
	def fontName(self):
		return self._getProperty('font',None)
	@property
	def fontSize(self):
		return int(self._getProperty('fontSize',10))
	@property
	def typeFace(self):
		return int(self._getProperty('typeFace',0))
	@property
	def color(self):
		return self._getProperty('color','#000000')

	@property
	def rgba(self):
		"""
		always returns an rgba[], regardless of color being:
			#FFFFFF
			#FFFFFFFF
			rgb(128,12,23)
			rgba(234,33,23,0)
		"""
		s=self.color
		if s.find('(')>=0:
			ret=[int(c.strip()) for c in s.split('(',1)[-1].rsplit(')',1)[0].split(',')]
		else:
			format='B'*int(len(s)/2)
			ret=[c for c in struct.unpack(format,s.split('#',1)[-1].decode('hex'))]
		while len(ret)<3:
			ret.append(ret[0])
		if len(ret)<4:
			ret.append(255)
		return tuple(ret)

	@property
	def anchor(self):
		return self._getProperty('anchor','left')
	@property
	def lineSpacing(self):
		return int(self._getProperty('lineSpacing',0))
	@property
	def align(self):
		return self._getProperty('align','left')
	@property
	def verticalAlign(self):
		return self._getProperty('verticalAlign','top')

	@property
	def font(self):
		"""
		change to any TrueType or OpenType font

		TODO: check inside the zipfile for embedded fonts!

		if the font is installed on your system, will attempt to install it from
			fonts.google.com

		returns PIL font object
		"""
		if self._font==None:
			# first look in the zipped file
			for name in self.docRoot.componentNames:
				name=name.rsplit('.',1)
				if name[0]==self.fontName:
					if len(name)==1 or name[1] in ['ttf','otf','otc','ttc']:
						name='.'.join(name)
						self._font=ImageFont.truetype(self.docRoot.getComponent(name),self.fontSize,self.typeFace)
						break
		if self._font==None:
			# try the os
			try:
				self._font=ImageFont.truetype(self.fontName,self.fontSize,self.typeFace)
			except IOError:
				self._font=None
		if self._font==None:
			self._font=downloadFont(self.fontName)
		return self._font

	@property
	def roi(self):
		img=Image.new('L',self.size,0)
		d=ImageDraw.Draw(img)
		d.multiline_text((0,0),self.text,255,self.font,self.anchor,self.lineSpacing,self.align)
		return img
			
	@property
	def image(self):
		text=self.text
		img=Image.new('L',(1,1))
		d=ImageDraw.Draw(img)
		# some sanity checking
		if self.w==0:
			size=d.textsize(text,font=self.font,spacing=self.lineSpacing)
			w,h=size
		else:
			# determine the text wrapping and final size
			w=self.w
			textWrapper=textwrap.TextWrapper()
			textWrapper.width=int(w/len(text)*d.textsize('l',font=self.font,spacing=self.lineSpacing)[0])
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
			raise Exception('ERR: Unknown text vertical alignment mode "'+verticalAlign+'"')
		if align=='left':
			pass
		elif align=='right':
			x+=w-size[0]
		elif align in ['center','middle']:
			x+=w/2-size[0]/2
		else:
			raise Exception('ERR: Unknown text alignment mode "'+align+'"')
		# draw the stuff
		img=Image.new('RGBA',(int(x+w),int(y+h)),(128,128,128,0))
		d=ImageDraw.Draw(img)
		d.multiline_text((x,y),text,self.color,self.font,
			self.anchor,self.lineSpacing,self.align)
		return img


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
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				print 'ERR: unknown argument "'+arg+'"'
	if printhelp:
		print 'Usage:'
		print '  textLayer.py [options]'
		print 'Options:'
		print '   NONE'