#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Twiddle with svg filters

See also:
	https://www.w3.org/TR/2007/WD-SVGFilter12-20070501/#FilterPrimitivesOverview
"""
from xmlBackedObject import XmlBackedObject


def sampleFilter():
	import lxml.etree
	xml="""<filter
       style="color-interpolation-filters:sRGB"
       x="-0.25"
       width="1.5"
       y="-0.25"
       height="1.5"
       id="filter885">
      <feGaussianBlur
         in="SourceGraphic"
         result="result8"
         stdDeviation="5"
         id="feGaussianBlur865" />
      <feComposite
         result="result18"
         operator="xor"
         in2="result8"
         in="SourceGraphic"
         id="feComposite867" />
      <feComposite
         in2="result18"
         result="result16"
         operator="arithmetic"
         k2="0.5"
         k1="1"
         in="result8"
         id="feComposite869" />
      <feComposite
         in="result16"
         operator="atop"
         result="result6"
         in2="result8"
         id="feComposite871" />
      <feOffset
         in="result6"
         result="result17"
         id="feOffset873" />
      <feDisplacementMap
         result="result4"
         scale="100"
         yChannelSelector="A"
         xChannelSelector="A"
         in="result17"
         in2="result16"
         id="feDisplacementMap875" />
      <feComposite
         k3="1"
         in="result17"
         operator="arithmetic"
         result="result2"
         in2="result4"
         id="feComposite877" />
      <feComposite
         operator="out"
         in="result2"
         result="fbSourceGraphic"
         in2="result17"
         id="feComposite879" />
      <feComposite
         result="result14"
         operator="over"
         in2="fbSourceGraphic"
         in="fbSourceGraphic"
         id="feComposite881" />
      <feComposite
         in="result14"
         operator="in"
         in2="SourceGraphic"
         result="result15"
         id="feComposite883" />
    </filter>"""
	xml=lxml.etree.fromstring(xml)
	return Filter(None,None,xml)

	
def surfaceNormals(rgbArry,surfaceScale=1.0,FACTORx=1.0,FACTORy=1.0):
	Nx= - surfaceScale * FACTORx *
			   (Kx(0,0)*I(x-dx,y-dy) + Kx(1,0)*I(x,y-dy) + Kx(2,0)*I(x+dx,y-dy) +
				Kx(0,1)*I(x-dx,y)    + Kx(1,1)*I(x,y)    + Kx(2,1)*I(x+dx,y)    +
				Kx(0,2)*I(x-dx,y+dy) + Kx(1,2)*I(x,y+dy) + Kx(2,2)*I(x+dx,y+dy))
	Ny= - surfaceScale * FACTORy *
			   (Ky(0,0)*I(x-dx,y-dy) + Ky(1,0)*I(x,y-dy) + Ky(2,0)*I(x+dx,y-dy) +
				Ky(0,1)*I(x-dx,y)    + Ky(1,1)*I(x,y)    + Ky(2,1)*I(x+dx,y)    +
				Ky(0,2)*I(x-dx,y+dy) + Ky(1,2)*I(x,y+dy) + Ky(2,2)*I(x+dx,y+dy))
	Nz= 1.0
	N = (Nx, Ny, Nz) / Norm((Nx,Ny,Nz))
	return N

class FilterPrimitive(XmlBackedObject):
	"""
	A feWhatever filter primitive tag
	"""
	
	PRIMITIVE_TYPES=[
		'feDistantLight',
		'fePointLight',
		'feSpotLight',
		'lighting-color',
		'feBlend',
		'feColorMatrix',
		'feComponentTransfer',
		'feComposite',
		'feConvolveMatrix',
		'feDiffuseLighting',
		'feDisplacementMap',
		'feFlood',
		'feGaussianBlur',
		'feImage',
		'feMerge',
		'feMorphology',
		'feOffset',
		'feSpecularLighting',
		'feTile',
		'feTurbulence',
		'feDropShadow',
		'feDiffuseSpecular',
		'feCustom' ]
		
	def __init__(self,doc,parent,xml):
		XmlBackedObject.__init__(self,doc,parent,xml)
		if self.type not in self.PRIMITIVE_TYPES:
			raise Exception('ERR: Unknown SVG filter primitive, "'+self.type+'"')
		
	@property
	def type(self):
		return self.xml.tag
		
	@property
	def style(self):
		ret={}
		p=_getProperty('style','').split(';')
		for style in p:
			style=style.split('=',1)
			ret[style[0].strip()]=style[1].strip()
		return ret
		

class Filter(XmlBackedObject):
	"""
	Twiddle with svg filters
	"""
		
	def __init__(self,docRoot,parent,xml):
		XmlBackedObject.__init__(self,docRoot,parent,xml)
		
	@property
	def children(self):
		if self._children==None:
			self._children=[]
			for tag in self.xml.getchildren():
				self._children.append(FilterPrimitive(self.docRoot,self,tag))
		return self._children


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
				elif arg[0]=='--sampleFilter':
					filter=sampleFilter()
					print filter.id
					for child in filter.children:
						print '   '+child.type
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				print 'ERR: unknown argument "'+arg+'"'
	if printhelp:
		print 'Usage:'
		print '  filter.py [options]'
		print 'Options:'
		print '   NONE'