#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Contains css-compatible colors and color names.
"""
import numpy as np


HTML_COLOR_NAMES={
	'aliceblue':('AliceBlue',[0xF0,0xF8,0xFF]),
	'antiquewhite':('AntiqueWhite',[0xFA,0xEB,0xD7]),
	'aqua':('Aqua',[0x00,0xFF,0xFF]),
	'aquamarine':('Aquamarine',[0x7F,0xFF,0xD4]),
	'azure':('Azure',[0xF0,0xFF,0xFF]),
	'beige':('Beige',[0xF5,0xF5,0xDC]),
	'bisque':('Bisque',[0xFF,0xE4,0xC4]),
	'black':('Black',[0x00,0x00,0x00]),
	'blanchedalmond':('BlanchedAlmond',[0xFF,0xEB,0xCD]),
	'blue':('Blue',[0x00,0x00,0xFF]),
	'blueviolet':('BlueViolet',[0x8A,0x2B,0xE2]),
	'brown':('Brown',[0xA5,0x2A,0x2A]),
	'burlywood':('BurlyWood',[0xDE,0xB8,0x87]),
	'cadetblue':('CadetBlue',[0x5F,0x9E,0xA0]),
	'chartreuse':('Chartreuse',[0x7F,0xFF,0x00]),
	'chocolate':('Chocolate',[0xD2,0x69,0x1E]),
	'coral':('Coral',[0xFF,0x7F,0x50]),
	'cornflowerblue':('CornflowerBlue',[0x64,0x95,0xED]),
	'cornsilk':('Cornsilk',[0xFF,0xF8,0xDC]),
	'crimson':('Crimson',[0xDC,0x14,0x3C]),
	'cyan':('Cyan',[0x00,0xFF,0xFF]),
	'darkblue':('DarkBlue',[0x00,0x00,0x8B]),
	'darkcyan':('DarkCyan',[0x00,0x8B,0x8B]),
	'darkgoldenrod':('DarkGoldenRod',[0xB8,0x86,0x0B]),
	'darkgray':('DarkGray',[0xA9,0xA9,0xA9]),
	'darkgrey':('DarkGrey',[0xA9,0xA9,0xA9]),
	'darkgreen':('DarkGreen',[0x00,0x64,0x00]),
	'darkkhaki':('DarkKhaki',[0xBD,0xB7,0x6B]),
	'darkmagenta':('DarkMagenta',[0x8B,0x00,0x8B]),
	'darkolivegreen':('DarkOliveGreen',[0x55,0x6B,0x2F]),
	'darkorange':('DarkOrange',[0xFF,0x8C,0x00]),
	'darkorchid':('DarkOrchid',[0x99,0x32,0xCC]),
	'darkred':('DarkRed',[0x8B,0x00,0x00]),
	'darksalmon':('DarkSalmon',[0xE9,0x96,0x7A]),
	'darkseagreen':('DarkSeaGreen',[0x8F,0xBC,0x8F]),
	'darkslateblue':('DarkSlateBlue',[0x48,0x3D,0x8B]),
	'darkslategray':('DarkSlateGray',[0x2F,0x4F,0x4F]),
	'darkslategrey':('DarkSlateGrey',[0x2F,0x4F,0x4F]),
	'darkturquoise':('DarkTurquoise',[0x00,0xCE,0xD1]),
	'darkviolet':('DarkViolet',[0x94,0x00,0xD3]),
	'deeppink':('DeepPink',[0xFF,0x14,0x93]),
	'deepskyblue':('DeepSkyBlue',[0x00,0xBF,0xFF]),
	'dimgray':('DimGray',[0x69,0x69,0x69]),
	'dimgrey':('DimGrey',[0x69,0x69,0x69]),
	'dodgerblue':('DodgerBlue',[0x1E,0x90,0xFF]),
	'firebrick':('FireBrick',[0xB2,0x22,0x22]),
	'floralwhite':('FloralWhite',[0xFF,0xFA,0xF0]),
	'forestgreen':('ForestGreen',[0x22,0x8B,0x22]),
	'fuchsia':('Fuchsia',[0xFF,0x00,0xFF]),
	'gainsboro':('Gainsboro',[0xDC,0xDC,0xDC]),
	'ghostwhite':('GhostWhite',[0xF8,0xF8,0xFF]),
	'gold':('Gold',[0xFF,0xD7,0x00]),
	'goldenrod':('GoldenRod',[0xDA,0xA5,0x20]),
	'gray':('Gray',[0x80,0x80,0x80]),
	'grey':('Grey',[0x80,0x80,0x80]),
	'green':('Green',[0x00,0x80,0x00]),
	'greenyellow':('GreenYellow',[0xAD,0xFF,0x2F]),
	'honeydew':('HoneyDew',[0xF0,0xFF,0xF0]),
	'hotpink':('HotPink',[0xFF,0x69,0xB4]),
	'indianred':('IndianRed',[0xCD,0x5C,0x5C]),
	'indigo':('Indigo',[0x4B,0x00,0x82]),
	'ivory':('Ivory',[0xFF,0xFF,0xF0]),
	'khaki':('Khaki',[0xF0,0xE6,0x8C]),
	'lavender':('Lavender',[0xE6,0xE6,0xFA]),
	'lavenderblush':('LavenderBlush',[0xFF,0xF0,0xF5]),
	'lawngreen':('LawnGreen',[0x7C,0xFC,0x00]),
	'lemonchiffon':('LemonChiffon',[0xFF,0xFA,0xCD]),
	'lightblue':('LightBlue',[0xAD,0xD8,0xE6]),
	'lightcoral':('LightCoral',[0xF0,0x80,0x80]),
	'lightcyan':('LightCyan',[0xE0,0xFF,0xFF]),
	'lightgoldenrodyellow':('LightGoldenRodYellow',[0xFA,0xFA,0xD2]),
	'lightgray':('LightGray',[0xD3,0xD3,0xD3]),
	'lightgrey':('LightGrey',[0xD3,0xD3,0xD3]),
	'lightgreen':('LightGreen',[0x90,0xEE,0x90]),
	'lightpink':('LightPink',[0xFF,0xB6,0xC1]),
	'lightsalmon':('LightSalmon',[0xFF,0xA0,0x7A]),
	'lightseagreen':('LightSeaGreen',[0x20,0xB2,0xAA]),
	'lightskyblue':('LightSkyBlue',[0x87,0xCE,0xFA]),
	'lightslategray':('LightSlateGray',[0x77,0x88,0x99]),
	'lightslategrey':('LightSlateGrey',[0x77,0x88,0x99]),
	'lightsteelblue':('LightSteelBlue',[0xB0,0xC4,0xDE]),
	'lightyellow':('LightYellow',[0xFF,0xFF,0xE0]),
	'lime':('Lime',[0x00,0xFF,0x00]),
	'limegreen':('LimeGreen',[0x32,0xCD,0x32]),
	'linen':('Linen',[0xFA,0xF0,0xE6]),
	'magenta':('Magenta',[0xFF,0x00,0xFF]),
	'maroon':('Maroon',[0x80,0x00,0x00]),
	'mediumaquamarine':('MediumAquaMarine',[0x66,0xCD,0xAA]),
	'mediumblue':('MediumBlue',[0x00,0x00,0xCD]),
	'mediumorchid':('MediumOrchid',[0xBA,0x55,0xD3]),
	'mediumpurple':('MediumPurple',[0x93,0x70,0xDB]),
	'mediumseagreen':('MediumSeaGreen',[0x3C,0xB3,0x71]),
	'mediumslateblue':('MediumSlateBlue',[0x7B,0x68,0xEE]),
	'mediumspringgreen':('MediumSpringGreen',[0x00,0xFA,0x9A]),
	'mediumturquoise':('MediumTurquoise',[0x48,0xD1,0xCC]),
	'mediumvioletred':('MediumVioletRed',[0xC7,0x15,0x85]),
	'midnightblue':('MidnightBlue',[0x19,0x19,0x70]),
	'mintcream':('MintCream',[0xF5,0xFF,0xFA]),
	'mistyrose':('MistyRose',[0xFF,0xE4,0xE1]),
	'moccasin':('Moccasin',[0xFF,0xE4,0xB5]),
	'navajowhite':('NavajoWhite',[0xFF,0xDE,0xAD]),
	'navy':('Navy',[0x00,0x00,0x80]),
	'oldlace':('OldLace',[0xFD,0xF5,0xE6]),
	'olive':('Olive',[0x80,0x80,0x00]),
	'olivedrab':('OliveDrab',[0x6B,0x8E,0x23]),
	'orange':('Orange',[0xFF,0xA5,0x00]),
	'orangered':('OrangeRed',[0xFF,0x45,0x00]),
	'orchid':('Orchid',[0xDA,0x70,0xD6]),
	'palegoldenrod':('PaleGoldenRod',[0xEE,0xE8,0xAA]),
	'palegreen':('PaleGreen',[0x98,0xFB,0x98]),
	'paleturquoise':('PaleTurquoise',[0xAF,0xEE,0xEE]),
	'palevioletred':('PaleVioletRed',[0xDB,0x70,0x93]),
	'papayawhip':('PapayaWhip',[0xFF,0xEF,0xD5]),
	'peachpuff':('PeachPuff',[0xFF,0xDA,0xB9]),
	'peru':('Peru',[0xCD,0x85,0x3F]),
	'pink':('Pink',[0xFF,0xC0,0xCB]),
	'plum':('Plum',[0xDD,0xA0,0xDD]),
	'powderblue':('PowderBlue',[0xB0,0xE0,0xE6]),
	'purple':('Purple',[0x80,0x00,0x80]),
	'rebeccapurple':('RebeccaPurple',[0x66,0x33,0x99]),
	'red':('Red',[0xFF,0x00,0x00]),
	'rosybrown':('RosyBrown',[0xBC,0x8F,0x8F]),
	'royalblue':('RoyalBlue',[0x41,0x69,0xE1]),
	'saddlebrown':('SaddleBrown',[0x8B,0x45,0x13]),
	'salmon':('Salmon',[0xFA,0x80,0x72]),
	'sandybrown':('SandyBrown',[0xF4,0xA4,0x60]),
	'seagreen':('SeaGreen',[0x2E,0x8B,0x57]),
	'seashell':('SeaShell',[0xFF,0xF5,0xEE]),
	'sienna':('Sienna',[0xA0,0x52,0x2D]),
	'silver':('Silver',[0xC0,0xC0,0xC0]),
	'skyblue':('SkyBlue',[0x87,0xCE,0xEB]),
	'slateblue':('SlateBlue',[0x6A,0x5A,0xCD]),
	'slategray':('SlateGray',[0x70,0x80,0x90]),
	'slategrey':('SlateGrey',[0x70,0x80,0x90]),
	'snow':('Snow',[0xFF,0xFA,0xFA]),
	'springgreen':('SpringGreen',[0x00,0xFF,0x7F]),
	'steelblue':('SteelBlue',[0x46,0x82,0xB4]),
	'tan':('Tan',[0xD2,0xB4,0x8C]),
	'teal':('Teal',[0x00,0x80,0x80]),
	'thistle':('Thistle',[0xD8,0xBF,0xD8]),
	'tomato':('Tomato',[0xFF,0x63,0x47]),
	'turquoise':('Turquoise',[0x40,0xE0,0xD0]),
	'violet':('Violet',[0xEE,0x82,0xEE]),
	'wheat':('Wheat',[0xF5,0xDE,0xB3]),
	'white':('White',[0xFF,0xFF,0xFF]),
	'whitesmoke':('WhiteSmoke',[0xF5,0xF5,0xF5]),
	'yellow':('Yellow',[0xFF,0xFF,0x00]),
	'yellowgreen':('YellowGreen',[0x9A,0xCD,0x32]),
	}

	
def strToColor(s,asFloat=True,defaultColor=[255,255,255,0]):
	"""
	convert an html color spec to a color array
	
	always returns an rgba[], regardless of input color being:
		#FFFFFF
		#FFFFFFFF
		rgb(128,12,23)
		rgba(234,33,23,0)
		yellow
		
	:param s: an html color string
	:param asFloat: always return a 0.0 to 1.0 floats verses a 0 to 255 bytes
	
	:returns: an rgba[]
	"""
	import struct
	if type(s)==None:
		ret=defaultColor
	if type(s) not in [str,unicode]:
		if type(s)==tuple:
			s=[ch for ch in s]
		ret=s
	else:
		s=s.strip().lower()
		if len(s)==0:
			if type(defaultColor) not in [str,unicode]:
				return defaultColor
			s=defaultColor
		if s in HTML_COLOR_NAMES:
			ret=HTML_COLOR_NAMES[s][1]
		else:
			if s.find('(')>=0:
				ret=[int(c.strip()) for c in s.split('(',1)[-1].rsplit(')',1)[0].split(',')]
			else:
				format='B'*int(len(s)/2)
				ret=[c for c in struct.unpack(format,s.split('#',1)[-1].decode('hex'))]
			while len(ret)<3:
				ret.append(ret[0])
			if len(ret)<4:
				ret.append(255)
	# force into float or int
	for i in range(len(ret)):
		if type(ret[i])!=int:
			if not asFloat:
				ret[i]=int(ret[i]*256)
		elif asFloat:
			ret[i]=ret[i]/256.0
	return np.array(ret)
	
	
def colorToStr(s,preferHex=True,alwaysHex=False,useNamed=False):
	"""
	:param s: the color to convert (If it is a string, it will be converted to a color, 
		then back.  Thus you can convert from one string format to another.)
	:param preferHex: return hex over rgb() but NOT over rgba()
	:param alwaysHex: always returns a hex string over rgb() or even rgba()
	:param useNamed: before anything else, check to see if there is a named color that matches
	"""
	s=strToColor(s)
	if useNamed:
		# return a name
		for n,v in HTML_COLOR_NAMES.values():
			if v==s:
				return n
	if alwaysHex or (preferHex and len(s)<3):
		# return a hex
		return '#'+(''.join(['%x02'%c for c in s]))
	# return a function
	if len(s)>3:
		return 'rgba('+(','.join(s))+')'
	return 'rgb('+(','.join(s))+')'

	
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
		print '  colors.py [options]'
		print 'Options:'
		print '   NONE'