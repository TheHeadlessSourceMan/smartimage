from helper_routines import *
import scipy.ndimage
from PIL import Image, ImageDraw


HTML_COLOR_NAMES={
	'AliceBlue':'#F0F8FF',
	'AntiqueWhite':'#FAEBD7',
	'Aqua':'#00FFFF',
	'Aquamarine':'#7FFFD4',
	'Azure':'#F0FFFF',
	'Beige':'#F5F5DC',
	'Bisque':'#FFE4C4',
	'Black':'#000000',
	'BlanchedAlmond':'#FFEBCD',
	'Blue':'#0000FF',
	'BlueViolet':'#8A2BE2',
	'Brown':'#A52A2A',
	'BurlyWood':'#DEB887',
	'CadetBlue':'#5F9EA0',
	'Chartreuse':'#7FFF00',
	'Chocolate':'#D2691E',
	'Coral':'#FF7F50',
	'CornflowerBlue':'#6495ED',
	'Cornsilk':'#FFF8DC',
	'Crimson':'#DC143C',
	'Cyan':'#00FFFF',
	'DarkBlue':'#00008B',
	'DarkCyan':'#008B8B',
	'DarkGoldenRod':'#B8860B',
	'DarkGray':'#A9A9A9',
	'DarkGrey':'#A9A9A9',
	'DarkGreen':'#006400',
	'DarkKhaki':'#BDB76B',
	'DarkMagenta':'#8B008B',
	'DarkOliveGreen':'#556B2F',
	'DarkOrange':'#FF8C00',
	'DarkOrchid':'#9932CC',
	'DarkRed':'#8B0000',
	'DarkSalmon':'#E9967A',
	'DarkSeaGreen':'#8FBC8F',
	'DarkSlateBlue':'#483D8B',
	'DarkSlateGray':'#2F4F4F',
	'DarkSlateGrey':'#2F4F4F',
	'DarkTurquoise':'#00CED1',
	'DarkViolet':'#9400D3',
	'DeepPink':'#FF1493',
	'DeepSkyBlue':'#00BFFF',
	'DimGray':'#696969',
	'DimGrey':'#696969',
	'DodgerBlue':'#1E90FF',
	'FireBrick':'#B22222',
	'FloralWhite':'#FFFAF0',
	'ForestGreen':'#228B22',
	'Fuchsia':'#FF00FF',
	'Gainsboro':'#DCDCDC',
	'GhostWhite':'#F8F8FF',
	'Gold':'#FFD700',
	'GoldenRod':'#DAA520',
	'Gray':'#808080',
	'Grey':'#808080',
	'Green':'#008000',
	'GreenYellow':'#ADFF2F',
	'HoneyDew':'#F0FFF0',
	'HotPink':'#FF69B4',
	'IndianRed':'#CD5C5C',
	'Indigo':'#4B0082',
	'Ivory':'#FFFFF0',
	'Khaki':'#F0E68C',
	'Lavender':'#E6E6FA',
	'LavenderBlush':'#FFF0F5',
	'LawnGreen':'#7CFC00',
	'LemonChiffon':'#FFFACD',
	'LightBlue':'#ADD8E6',
	'LightCoral':'#F08080',
	'LightCyan':'#E0FFFF',
	'LightGoldenRodYellow':'#FAFAD2',
	'LightGray':'#D3D3D3',
	'LightGrey':'#D3D3D3',
	'LightGreen':'#90EE90',
	'LightPink':'#FFB6C1',
	'LightSalmon':'#FFA07A',
	'LightSeaGreen':'#20B2AA',
	'LightSkyBlue':'#87CEFA',
	'LightSlateGray':'#778899',
	'LightSlateGrey':'#778899',
	'LightSteelBlue':'#B0C4DE',
	'LightYellow':'#FFFFE0',
	'Lime':'#00FF00',
	'LimeGreen':'#32CD32',
	'Linen':'#FAF0E6',
	'Magenta':'#FF00FF',
	'Maroon':'#800000',
	'MediumAquaMarine':'#66CDAA',
	'MediumBlue':'#0000CD',
	'MediumOrchid':'#BA55D3',
	'MediumPurple':'#9370DB',
	'MediumSeaGreen':'#3CB371',
	'MediumSlateBlue':'#7B68EE',
	'MediumSpringGreen':'#00FA9A',
	'MediumTurquoise':'#48D1CC',
	'MediumVioletRed':'#C71585',
	'MidnightBlue':'#191970',
	'MintCream':'#F5FFFA',
	'MistyRose':'#FFE4E1',
	'Moccasin':'#FFE4B5',
	'NavajoWhite':'#FFDEAD',
	'Navy':'#000080',
	'OldLace':'#FDF5E6',
	'Olive':'#808000',
	'OliveDrab':'#6B8E23',
	'Orange':'#FFA500',
	'OrangeRed':'#FF4500',
	'Orchid':'#DA70D6',
	'PaleGoldenRod':'#EEE8AA',
	'PaleGreen':'#98FB98',
	'PaleTurquoise':'#AFEEEE',
	'PaleVioletRed':'#DB7093',
	'PapayaWhip':'#FFEFD5',
	'PeachPuff':'#FFDAB9',
	'Peru':'#CD853F',
	'Pink':'#FFC0CB',
	'Plum':'#DDA0DD',
	'PowderBlue':'#B0E0E6',
	'Purple':'#800080',
	'RebeccaPurple':'#663399',
	'Red':'#FF0000',
	'RosyBrown':'#BC8F8F',
	'RoyalBlue':'#4169E1',
	'SaddleBrown':'#8B4513',
	'Salmon':'#FA8072',
	'SandyBrown':'#F4A460',
	'SeaGreen':'#2E8B57',
	'SeaShell':'#FFF5EE',
	'Sienna':'#A0522D',
	'Silver':'#C0C0C0',
	'SkyBlue':'#87CEEB',
	'SlateBlue':'#6A5ACD',
	'SlateGray':'#708090',
	'SlateGrey':'#708090',
	'Snow':'#FFFAFA',
	'SpringGreen':'#00FF7F',
	'SteelBlue':'#4682B4',
	'Tan':'#D2B48C',
	'Teal':'#008080',
	'Thistle':'#D8BFD8',
	'Tomato':'#FF6347',
	'Turquoise':'#40E0D0',
	'Violet':'#EE82EE',
	'Wheat':'#F5DEB3',
	'White':'#FFFFFF',
	'WhiteSmoke':'#F5F5F5',
	'Yellow':'#FFFF00',
	'YellowGreen':'#9ACD32'}

def strToColor(s):
	"""
	convert an html color spec to a color array
	
	always returns an rgba[] in 0-255, regardless of input color being:
		#FFFFFF
		#FFFFFFFF
		rgb(128,12,23)
		rgba(234,33,23,0)
		
	:param s: an html color string
	
	:returns: an rgba[] in 0-255
	"""
	import struct
	if type(s) not in [str,unicode]:
		return s
	if s in HTML_COLOR_NAMES:
		s=HTML_COLOR_NAMES[s]
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
	
	
def colorToStr(c):
	"""
	convert a color array to a html string
	
	:param c: an rgba[] in 0-255
	
	:returns: an html color string
	"""
	if (type(c)==tuple) or (type(c)==list and type(c[0])==list) or (type(c)==np.ndarray and len(c.shape)>1):
		colors=[]
		for cx in c:
			colors.append(colorToStr(cx))
		return colors
	if type(c[0])!=int:
		c=c*255.0
	if len(c)==1:
		return '#%02X'%c[0]
	if len(c)==3:
		return '#%02X%02X%02X'%(c[0],c[1],c[2])
	if len(c)==4:
		return 'rgba(%d,%d,%d,%f)'%(c[0],c[1],c[2],c[3]/255)
	raise Exception('Bogus color string:',c)

	
def pickColor(img,location,pickMode='average'):
	"""
	pick a color at a given location
	
	:param img: can be a pil image, numpy array, etc
	:param location: can be a single point or an [x,y,w,h] to average
	:param pickMode: what to do with multiple pixels
		choices are average,range,or all
	:return: 
		if a single point or "average", return one color
		if "range" return (minColor,maxColor)
		if "all" return [all colors]
	"""
	ret=None
	img=numpyArray(img)
	if len(location)<4:
		# if it's a single pixel, easy peasy
		ret=img[location[0],location[1]]
	else:
		region=img[location[0]:location[0]+location[2]+1,location[0]:location[0]+location[2]+1]
		if pickMode=='average':
			ret=[]
			for i in range(img.shape[-1]):
				ret.append(np.mean(region[:,:,i]))
		elif pickMode=='range':
			ret=(np.min(region,axis=(0,1)),np.max(region,axis=(0,1)))
		elif pickMode=='all':
			ret=region.reshape(-1,region.shape[-1])
			ret=np.unique(ret,axis=0)
	return ret
	
	
def matchColorToImage(color,img):
	"""
	match the color to the image mode
	"""
	imgChan=img.shape[-1]
	colChan=len(color)
	if imgChan>colChan:
		raise NotImplementedError("Don't know how to convert color["+str(len(color))+"] to image pixel["+str(img.shape[-1])+"]")
	elif imgChan<colChan:
		color=color[0:imgChan]
	imgFloat=isFloat(img)
	colFloat=isFloat(color)
	if imgFloat!=colFloat:
		if imgFloat:
			color=np.array(color)/255.0
		else:
			color=np.int(np.array(color)*255)
	return color
	
	
def selectByColor(img,color,tolerance=0,soften=10,smartSoften=True,colorspace='RGB'):
	"""
	Select all pixels of a given color

	:param img: can be a pil image, numpy array, etc
	:param color: (in colorspace units) can be anything that pickColor returns:
		a color int array
		a color string to decode
		a color range (colorLow,colorHigh)
		an array of any of these
	:param tolerance: how close the selection must be
	:param soften: apply a soften radius to the edges of the selection
	:param smartSoften: multiply the soften radius by how near the pixel is to the selection color
	:param colorspace: change the given img (assumed to be RGB) into another corlorspace before matching
	
	:returns: black and white image in a numpy array (usable as a selection or a mask)
	"""
	img=numpyArray(img)
	img=changeColorspace(img)
	if (type(color)==list and type(color[0])==list) or (type(color)==np.ndarray and len(color.shape)>1):
		# there are multiple colors, so select them all one at a time
		# TODO: this could possibly be made faster with array operations??
		ret=None
		for c in color:
			if type(ret)==type(None):
				ret=selectByColor(img,c,tolerance,soften,smartSoften)
			else:
				ret=ret+selectByColor(img,c,tolerance,soften,smartSoften)
		ret=clampImage(ret)
	elif type(color)==tuple:
		# color range - select all colors "between" these two in the given color space
		color=(matchColorToImage(color[0],img),matchColorToImage(color[1],img))
		matches=np.logical_and(img>=color[0],img<=color[1])
		ret=np.where(matches.all(axis=2),1.0,0.0)
	else:
		# a single color (or a series of colors that have been averaged down to one)
		color=matchColorToImage(color,img)
		if isFloat(color):
			imax=1.0
			imin=0.0
		else:
			imax=255
			imin=0
		numColors=img.shape[-1]
		avgDelta=np.sum(np.abs(img[:,:]-color),axis=-1)/numColors
		ret=np.where(avgDelta<=tolerance,imax,imin)
		if soften>0:
			ret=gaussianBlur(ret,soften)
			if smartSoften:
				ret=np.minimum(imax,ret/avgDelta)
	return ret
	
	
def selectByPoint(img,location,tolerance=0,soften=10,smartSoften=True,colorspace='RGB',pickMode='average'):
	"""
	Works like the "magic wand" selection tool.
	It is different than selectByColor(img,pickColor(img,location)) in that only a contiguious
		region is selected

	:param img: can be a pil image, numpy array, etc
	:param location: can be a single point or an [x,y,w,h]
	:param tolerance: how close the selection must be
	:param soften: apply a soften radius to the edges of the selection
	:param smartSoften: multiply the soften radius by how near the pixel is to the selection color
	:param colorspace: change the given img (assumed to be RGB) into another corlorspace before matching
	
	:returns: black and white image in a numpy array (usable as a selection or a mask)
	"""
	img=numpyArray(img)
	img=changeColorspace(img)
	# selectByColor, but the 
	selection=selectByColor(img,pickColor(img,location,pickMode),tolerance,soften,smartSoften,colorspace=imageMode(img))
	# now identify islands from selection
	labels,_=scipy.ndimage.label(selection)
	# grab only the named islands within the original location
	if len(location)<4:
		labelsInSel=[labels[location[0],location[1]]]
	else:
		labelsInSel=np.unique(labels[location[0]:location[0]+location[2]+1,location[0]:location[0]+location[2]+1])
	# only keep portions of selection within our islands
	selection=np.where(np.isin(labels,labelsInSel),selection,0.0)
	return selection
	
	
def gaussianBlur(img,sizeX,sizeY=None,edge='clamp'):
	"""
	perform a gaussian blur on an image
	
	:param img: can be a pil image, numpy array, etc
	:param sizeX: the x radius of the blur
	:param sizeY: the y radius of the blur (if None, use same as X)
	:param edge: what to do for more pixels when we reach an edge 
		can be: "clamp","mirror","wrap", or a color 
		default is "clamp"
	
	:returns: image in a numpy array
	"""
	if sizeY==None:
		sizeY=sizeX
	if edge=='clamp':
		mode='nearest'
		cval=0.0
	elif edge=='mirror':
		mode='mirror'
		cval=0.0
	elif edge=='wrap':
		mode='wrap'
		cval=0.0
	else:
		mode='constant'
		cval=np.array(strToColor(edge))
	img=numpyArray(img)
	img=scipy.ndimage.gaussian_filter(img,(sizeY,sizeX),mode=mode,cval=cval)
	return img


def morphology(func,img,amount,edge='clamp',shape=None):
	"""
	perform a morphological operation on an image
		"open","close","dilate",or "erode"
	
	For a definition of what those things mean:
		https://en.wikipedia.org/wiki/Mathematical_morphology
	
	:param func: morphological function to perform
	:param img: can be a pil image, numpy array, etc
	:param amount: how wide in pixels the operator is
	:param edge: what to do for more pixels when we reach an edge 
		can be: "clamp","mirror","wrap", or a color 
		default is "clamp"
	:param shape: a b+w shape to sweep along the img outline
		disables amount value
	
	:returns: image in a numpy array
	"""
	if edge=='clamp':
		mode='nearest'
		cval=0.0
	elif edge=='mirror':
		mode='mirror'
		cval=0.0
	elif edge=='wrap':
		mode='wrap'
		cval=0.0
	else:
		mode='constant'
		cval=np.array(strToColor(edge))
	amount=int(amount) # they don't like floats
	if amount<0:
		# if they specify a negative amount, flip the operation!
		amount=-amount
		if func=='dilate':
			func='erode'
		elif func=='erode':
			func='dilate'
		elif func=='open':
			func='close'
		elif func=='close':
			func='open'
	img=numpyArray(img)
	if func=='erode':
		img=scipy.ndimage.grey_erosion(img,(amount),shape,mode=mode,cval=cval)
	elif func=='dilate':
		img=scipy.ndimage.grey_dilation(img,(amount),shape,mode=mode,cval=cval)
	elif func=='open':
		img=scipy.ndimage.grey_opening(img,(amount),shape,mode=mode,cval=cval)
	elif func=='close':
		img=scipy.ndimage.grey_closing(img,(amount),shape,mode=mode,cval=cval)
	elif func=='gradient' or func=='outline':
		img=scipy.ndimage.morphological_gradient(img,(amount),shape,mode=mode,cval=cval)
	elif func=='tophat' or func=='whitehat':
		img=scipy.ndimage.white_tophat(img,(amount),shape,mode=mode,cval=cval)
	elif func=='blackhat':
		img=scipy.ndimage.black_tophat(img,(amount),shape,mode=mode,cval=cval)
	return img

	
def selectionToPath(img,midpoint=0.5):
	"""
	convert a black and white selection (or mask) into a path
	
	:param img: a pil image, numpy array, etc
	:param midpoint: for grayscale images, this is the cuttoff point for yes/no
	
	:return: a closed polygon [(x,y)]
	
	TODO: I resize the image to give laplace a border to lock onto, but
		do I need to scale the points back down again??
	"""
	img=imageBorder(img,1,0)
	img=numpyArray(img)
	img=np.where(img>=midpoint,1.0,0.0)
	img=scipy.ndimage.laplace(img)
	points=np.nonzero(img) # returns [[y points],[x points]]
	points=np.transpose(points)
	# convert to a nice point-pair representation
	points=[(point[1],point[0]) for point in points]
	return points
	
def pathToSelection(path,filled=True,outlineWidth=0):
	"""
	by using fill=False and outlineWidth=n you can create a border selection
	"""
	if outlineWidth>0:
		borderColor=1
	else:
		borderColor=0
	if filled:
		backgroundColor=1
	else:
		backgroundColor=0
	return renderPath(path,None,1,borderColor,backgroundColor)
	
def renderPath(path,intoImg=None,borderSize=1,borderColor=None,backgroundColor=None):
	"""
	render a path into an image
	
	:param intoImg: if not specified, a new one will be created
	"""
	if intoImg==None:
		w=0
		h=0
		for pt in path:
			if pt[0]>w:
				w=pt[0]
			if pt[1]>h:
				h=pt[1]
		intoImg=Image.new('L',(w,h),0)
		if borderColor==None:
			borderColor=1
		if backgroundColor==None:
			backgroundColor=0
	else:
		if borderColor==None:
			borderColor=(255,0,0,128)
		if backgroundColor==None:
			backgroundColor=(255,0,0,128)
	ImageDraw.Draw(intoImg).polygon(path,outline=borderColor,fill=backgroundColor)
	return intoImg

def skin(img):
	"""
	sample color selection
	returns a skintone mask
	
	This is a match on HS colorspace, which, against popular rumor, performs better than other color spaces.
		"Color Space for Skin Detection - A Review"
			by Nikhil Rasiwasia, 
			Fondazione Graphitech,
			University of Trento, (TN) Italy
		"Comparison  of  Five  Color  Models  in  Skin  Pixel  Classification"
			by Benjamin D. Zarit, Boaz J. Super, Francis K. H. Quek
			Electrical Engineering and Computer Science
			University of Illinois at Chicago
	
	:param img: image to match
	:return: a black and white mask
	
	TODO: doesn't work :P
	"""
	return selectByColor(img,((0,48,80),(20,255,255)),colorspace='HSV')
	

#------------------ main entry point for external fun


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
		selection=None
		selectionTolerance=0.10
		soften=0
		smartSoften=True
		pickMode='average'
		for arg in sys.argv[1:]:
			if arg.startswith('-'):
				arg=[a.strip() for a in arg.split('=',1)]
				if arg[0] in ['-h','--help']:
					printhelp=True
				elif arg[0]=='--selectionTolerance':
					selectionTolerance=float(arg[1])
				elif arg[0]=='--selectByColor':
					selection=selectByColor(img,arg[1],selectionTolerance,soften,smartSoften)
				elif arg[0]=='--selectByPoint':
					selection=selectByPoint(img,[int(x) for x in arg[1].split(',')],selectionTolerance,soften,smartSoften,pickMode=pickMode)
				elif arg[0]=='--pickMode':
					pickMode=arg[1]
				elif arg[0]=='--soften':
					soften=float(arg[1])
				elif arg[0]=='--smartSoften':
					smartSoften=arg[1][0] in ['t','T','y','Y','1']
				elif arg[0]=='--pickColor':
					color=pickColor(img,[int(x) for x in arg[1].split(',')],pickMode)
					print colorToStr(color)
				elif arg[0]=='--showSelection':
					pilImage(selection).show()
				elif arg[0]=='--showPath':
					points=selectionToPath(selection)
					iout=img.copy()
					iout=renderPath(points,iout)
					pilImage(iout).show()
				elif arg[0] in ['--erode','--dilate','--open','--close']:
					selection=morphology(arg[0][2:],selection,float(arg[1]))
				elif arg[0]=='--skin':
					iout=skin(img)
					#iout=setAlpha(img,iout)
					pilImage(iout).show()
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				img=defaultLoader(arg)
	if printhelp:
		print 'Usage:'
		print '  selectionsAndPaths.py image.jpg [options]'
		print 'Options:'
		print '   --selectionTolerance=0.5 . set tolerance for subsequent selection operations'
		print '   --selectByColor=RGB ...... select by a given color'
		print '   --soften=r ............... radius to soften the selection'
		print '   --smartSoften=true ....... modify softenss based on similarity'
		print '   --pickMode=mode .......... when picking an area "average","all",or "range"'
		print '   --pickColor=x,y[,w,h] .... pick colors'
		print '   --showSelection .......... show only the selected portion of the image'
		print '   --showPath ............... show selection as a path on top of the original image'
		print '   --erode=amt .............. erode the selection'
		print '   --dilate=amt ............. dilate the selection'
		print '   --open=amt ............... "open" the selection'
		print '   --close=amt .............. "close" the selection'
		print 'Notes:'
		print '   * All filenames can also take file:// http:// https:// ftp:// urls'