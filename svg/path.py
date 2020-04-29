#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
A single svg path
"""
from backedObject import SmartimageXmlBackedObject


def samplePath():
	import lxml.etree
	pathXml="""<path
       style="fill:#000400;fill-rule:evenodd;stroke:#000000;stroke-width:0.26458332px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
       d="M 12.095237,129.17857 C 11.339285,104.61012 13.398383,77.635884 37.041665,77.017855 60.684948,76.399826 59.150963,84.587186 65.011904,98.940473 71.059522,80.797613 77.107141,77.017856 93.738095,77.77381 119.42507,78.941402 123.81909,91.214672 123.22024,124.64286 122.59679,159.44393 104.32143,168.48809 69.547618,204.7738 25.111229,169.23687 12.85119,153.74702 12.095237,129.17857 Z"
       id="path815" />"""
	xml=lxml.etree.fromstring(pathXml)
	return Path(None,None,xml)

	   
class Path(SmartimageXmlBackedObject):
	"""
	A single svg path
	"""
	
	def __init__(self,doc,parent,xml):
		SmartimageXmlBackedObject.__init__(self,doc,parent,xml)
		
	@property
	def style(self):
		ret={}
		p=_getProperty('style','').split(';')
		for style in p:
			style=style.split('=',1)
			ret[style[0].strip()]=style[1].strip()
		return ret
		
	@property
	def d(self):
		return self._getProperty('d','')
		
	def image(self):
		"""
		creates a PIL image
		uses wx to do the drawing
		"""
		
		
	def _decode(self,context,moveToFn,lineToFn,cubicBezierFn,quadraticBezierFunction,arcFn,closePathFn=None):
		"""
		given a user-defined context will run through the d tape and call the associated functions as needed
		
		(all values in absolute coordinates)
		
		moveToFn(context,(x,y))
		lineToFn(context,(x,y))
		cubicBezierFn(context,(x,y),(control1X,control1Y),(control2X,control2Y))
		quadraticBezierFunction(context,(x,y),(controlX,controlY))
		arcFn(context,(x,y),(radiusX,radiusY),xAxisRotation,largeArcFlag,sweepFlag)
		closePathFn(context) -- can be None if you don't care
		
		returns None -- expects context to be modified
		"""
		tape=self.d.split(' ')
		i=0
		current=(0,0)
		currentControl=(0,0)
		def decodePoint(raw):
			return [float(coord) for coord in raw.split(',')]
		def decodeFloat(raw):
			return float(raw)
		def decodeBool(raw):
			return raw[0]=='1'
		def rel2abs(rel):
			"""
			convert relative coordinates to absolute
			"""
			return (current[0]+rel[0],current[1]+rel[1])
		while i<len(tape):
			isRelative=tape[i].islower()
			command=tape[i].lower()
			i+=1
			if command=='m': # move
				while i<len(tape) and not tape[i][0].isalpha():
					point=decodePoint(tape[i])
					i+=1
					if isRelative:
						point=rel2abs(point)
					moveToFn(context,point)
					current=point
			elif command=='l': #lineTo
				while i<len(tape) and not tape[i][0].isalpha():
					point=decodePoint(tape[i])
					i+=1
					if isRelative:
						point=rel2abs(point)
					lineToFn(context,point)
					current=point
			elif command=='h':
				while i<len(tape) and not tape[i][0].isalpha():
					point=(current[0],decodeFloat(tape[i]))
					i+=1
					if isRelative:
						point=rel2abs(point)
					lineToFn(context,point)
					current=point
			elif command=='v':
				while i<len(tape) and not tape[i][0].isalpha():
					point=(decodeFloat(tape[i]),current[1])
					i+=1
					if isRelative:
						point=rel2abs(point)
					lineToFn(context,point)
					current=point
			elif command=='c': # curveTo
				while i<len(tape) and not tape[i][0].isalpha():
					cp1=decodePoint(tape[i])
					i+=1
					cp2=decodePoint(tape[i])
					i+=1
					point=decodePoint(tape[i])
					i+=1
					if isRelative:
						cp1=rel2abs(cp1)
						cp2=rel2abs(cp2)
						point=rel2abs(point)
					cubicBezierFn(context,point,cp1,cp2)
					current=point
					currentControl=cp2
			elif command=='s':
				while i<len(tape) and not tape[i][0].isalpha():
					cp2=decodePoint(tape[i])
					i+=1
					point=decodePoint(tape[i])
					i+=1
					if isRelative:
						cp2=rel2abs(cp2)
						point=rel2abs(point)
					cubicBezierFn(context,point,currentControl,cp2)
					current=point
					currentControl=cp2
			elif command=='q':
				while i<len(tape) and not tape[i][0].isalpha():
					cp=decodePoint(tape[i])
					i+=1
					point=decodePoint(tape[i])
					i+=1
					if isRelative:
						cp=rel2abs(cp)
						point=rel2abs(point)
					quadraticBezierFn(context,point,cp)
					current=point
					currentControl=cp
			elif command=='t':
				while i<len(tape) and not tape[i][0].isalpha():
					point=decodePoint(tape[i])
					i+=1
					if isRelative:
						point=rel2abs(point)
					quadraticBezierFn(context,point,currentControl)
					current=point
			elif command=='a':
				while i<len(tape) and not tape[i][0].isalpha():
					radius=decodePoint(tape[i]) # technically a pair of radii, not a point, but... moving on...
					i+=1
					xAxisRotation=decodeFloat(tape[i]) # tilt an ellipse to a given angle
					i+=1
					largeArcFlag=decodeBool(tape[i])
					i+=1
					sweepFlag=decodeBool(tape[i])
					i+=1
					point=decodePoint(tape[i])
					i+=1
					if isRelative:
						point=rel2abs(point)
					arcFn(context,point,radius,xAxisRotation,largeArcFlag,sweepFlag)
					current=point
			elif command=='z':
				if closePathFn is not None:
					closePathFn(context)
			else:
				raise Exception('Unknown svg path command, "'+command+'" in "'+self.d+'"')
		return context


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
				elif arg[0]=='--samplePath':
					path=samplePath()
					def log(name,*args):
						print('+',name,args)
					def moveToFn(*args):
						log('moveTo',args)
					def lineToFn(*args):
						log('lineTo',*args)
					def cubicBezierFn(*args):
						log('cubicBezierFn',*args)
					def quadraticBezierFunction(*args):
						log('quadraticBezierFunction',*args)
					def arcFn(*args):
						log('arcFn',*args)
					def closePathFn(*args):
						log('closePathFn',*args)
					path._decode(None,moveToFn,lineToFn,cubicBezierFn,quadraticBezierFunction,arcFn,closePathFn)
				else:
					print('ERR: unknown argument "'+arg[0]+'"')
			else:
				print('ERR: unknown argument "'+arg+'"')
	if printhelp:
		print('Usage:')
		print('  path.py [options]')
		print('Options:')
		print('   NONE')