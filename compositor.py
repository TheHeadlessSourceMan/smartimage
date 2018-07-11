#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Implementation of photoshop/gimp blend modes in python.
"""
from PIL import Image, ImageChops, ImageEnhance
import numpy as np
from helper_routines import *


def adjustOpacity(image,amount=1.0):
	"""
	image: the image to be changed
	amount: 1.0=fully opaque 0.0=fully transparent

	returns: adjusted image

	IMPORTANT: the image bits may be altered.  To prevent this, set image.immutable=True
	"""
	if image==None or amount==1.0:
		return image
	if hasattr(image,'immutable') and image.immutable==True:
		image=image.copy()
	alpha=image.split()[3]
	alpha=ImageEnhance.Brightness(alpha).enhance(amount)
	image.putalpha(alpha)
	return image


def _blendArray(front,back,fn):
	"""
	:param fn: represents the B function from from the adobe blend modes documentation.
		It takes two parameters, Cb - the background pixels, and Cs - the source pixels
		The documentation originally appeared http://www.adobe.com/devnet/pdf/pdfs/blend_modes.pdf
		Copy included in source. (TODO: remove for copyright reasons?)

	NOTE: always creates new image
	"""
	shift=255.0
	useOpacity=False
	# find some common ground
	w=max(front.width,back.width)
	h=max(front.height,back.height)
	if front.width<w or front.height<h:
		front=extendImageCanvas(front,(0,0,w,h))
	if back.width<w or back.height<h:
		back=extendImageCanvas(back,(0,0,w,h))
	mode=maxMode(front,back)
	if front.mode!=mode:
		front=front.convert(mode)
	if back.mode!=mode:
		back=back.convert(mode)
	# convert to array
	front=np.asarray(front)/shift
	back=np.asarray(back)/shift
	# calculate the alpha channel
	opacity=1.0 # TODO: pass this in
	comp_alpha=np.maximum(np.minimum(front[:, :, 3], back[:, :, 3])*opacity,shift)
	new_alpha=front[:, :, 3] + (1.0 - front[:, :, 3])*comp_alpha
	np.seterr(divide='ignore',invalid='ignore')
	alpha=comp_alpha/new_alpha
	alpha[alpha==np.NAN]=0.0
	# blend the pixels
	combined=fn(front[:,:,:3],back[:,:,:3])*shift
	combined=np.clip(combined,0.0,255.0)
	# clean up and reassemble
	#ratio_rs =
	final=np.reshape(combined,[combined.shape[0],combined.shape[1],combined.shape[2]])
	#final = combined * ratio_rs + front[:, :, :3] * (1.0 - ratio_rs)
	if useOpacity:
		final=np.dstack((final,alpha))
	# convert back to PIL image
	if useOpacity:
		final=Image.fromarray(final.astype('uint8'),mode)
	else:
		final=Image.fromarray(final.astype('uint8'),'RGB')
	return final


def generalBlend(topImage,mathStr,botImage,opacity=1.0,position=(0,0),resize=True):
	"""
	mathstr -
		operators:
			basic math symbols ()*/%-+&|
			comparison operators == <= >= && || !=
			comma as combining operator
		functions: abs() sqrt() pow() min() max() count() sum() sin() cos() tan() if(condition,then,else)
		images: top, bot
		channel: RGB, CMYK, HSV, A
		~~~~~~~~~~~~~~~~~~~~~~~~~~~
		Notes:
			* Case sensitive
			* All values are percent values from 0..1
			* After this operation, values will be clipped to 0..1
			* Functions have two modes.
				They work between two channels if two given.
				If one given, they work on all values of that channel.
		~~~~~~~~~~~~~~~~~~~~~~~~~~~
		Examples:
			RGB=topRGB/bottomRGB ... simple divide blend mode
			RGB=min(topRGB,bottomRGB) ... min blend mode
			RGB=(topRGB-min(topRGB)) ... use min in the other mode to normalize black values
			A=1-topV ... extract inverted black levels to alpha channel
			RGBA=topRGB/bottomRGB,1-topV ... use commas to specify different operations for different channels
	"""
	shift=255.0
	mathStr=mathStr.replace('\n','').replace(' ','').replace('\t','')
	resultForm,equation=mathStr.split('=',1)
	# find some common ground
	w=max(topImage.width,botImage.width)
	h=max(topImage.height,botImage.height)
	if topImage.width<w or topImage.height<h:
		topImage=extendImageCanvas(topImage,(0,0,w,h))
	if botImage.width<w or botImage.height<h:
		botImage=extendImageCanvas(botImage,(0,0,w,h))
	mode='RGBA'#maxMode(topImage,botImage)
	if topImage.mode!=mode:
		topImage=topImage.convert(mode)
	if botImage.mode!=mode:
		botImage=botImage.convert(mode)
	# convert to arrays
	topRGBA=np.asarray(topImage)/shift
	for tag in 'HSV':
		if equation.find('top'+tag)>=0:
			topHSV=rgb2hsvArray(topRGBA)
			break
	for tag in 'CMYK':
		if equation.find('top'+tag)>=0:
			topCMYK=rgb2cmykArray(topRGBA)
			break
	botRGBA=np.asarray(botImage)/shift
	for tag in 'HSV':
		if equation.find('bot'+tag)>=0:
			botHSV=rgb2hsvArray(botRGBA)
			break
	for tag in 'CMYK':
		if equation.find('bot'+tag)>=0:
			botCMYK=rgb2cmykArray(botRGBA)
			break
	# convert the equation into python code
	import re
	tokenizer=re.compile(r"([!<>=|&]+|[,()%*-+/])")
	equation=tokenizer.split(equation)
	replacements={
		'min':'np.minimum','max':'np.maximum',
		'abs':'np.abs','sqrt':'np.sqrt','pow':'np.pow',
		'count':'np.count','sum':'np.sum',
		'sin':'np.sin','cos':'np.cos','tan':'np.tan',
		'if':'np.where',
		'topRGB':'topRGBA[:,:,:3]','topR':'topRGBA[:,:,0]','topR':'topRGBA[:,:,1]','topR':'topRGBA[:,:,2]','topA':'topRGBA[:,:,3]',
		'topCMY':'topCMYK[:,:,:3]','topC':'topCMYK[:,:,0]','topM':'topCMYK[:,:,1]','topY':'topCMYK[:,:,2]','topK':'topCMYK[:,:,3]',
		'topH':'topHSV[:,:,0]','topS':'topHSV[:,:,1]','topV':'topHSV[:,:,2]',
		'botRGB':'botRGBA[:,:,:3]','botR':'botRGBA[:,:,0]','botR':'botRGBA[:,:,1]','botR':'botRGBA[:,:,2]','botA':'botRGBA[:,:,3]',
		'botCMY':'botCMYK[:,:,:3]','botC':'botCMYK[:,:,0]','botM':'botCMYK[:,:,1]','botY':'botCMYK[:,:,2]','botK':'botCMYK[:,:,3]',
		'botH':'botHSV[:,:,0]','botS':'botHSV[:,:,1]','botV':'botHSV[:,:,2]',
	}
	for i in range(len(equation)):
		if len(equation[i])>0 and equation[i][0] not in r'0123456789,()%*-+/!<>=|&':
			if equation[i] not in replacements:
				raise Exception('ERR: illegal value in equation "'+equation[i]+'"')
			equation[i]=replacements[equation[i]]
	equation='('+(''.join(equation))+')'
	print equation
	# run the operation and join the results with dstack()
	final=None
	for channelSet in eval(equation):
		if type(final)==type(None):
			final=channelSet
		else:
			final=np.dstack((final,channelSet))
	# convert to RGB colorspace if necessary
	if resultForm=='HSV':
		final=hsv2rgbArray(final)
	elif resultForm=='CMYK':
		final=cmyk_to_rgb(final)
	final=final*shift
	# if alpha channel was missing, add one
	if len(final[0][1]<4):
		# calculate the alpha channel
		comp_alpha=np.maximum(np.minimum(topRGBA[:,:,3],botRGBA[:,:,3])*opacity,shift)
		new_alpha=topRGBA[:,:,3]+(1.0-topRGBA[:,:,3])*comp_alpha
		np.seterr(divide='ignore',invalid='ignore')
		alpha=comp_alpha/new_alpha
		alpha[alpha==np.NAN]=0.0
		# blend the pixels
		combined=final
		combined=np.clip(combined,0.0,255.0)
		# clean up and reassemble
		#ratio_rs=
		final=np.reshape(combined,[combined.shape[0],combined.shape[1],combined.shape[2]])
		#final=combined*ratio_rs+topRGBA[:,:,:3]*(1.0-ratio_rs)
		final=np.dstack((final,alpha))
	# convert the final result back into a PIL image
	final=Image.fromarray(final.astype('uint8'),mode)
	return final


def blend(image,blendMode,overImage,position=(0,0),resize=True):
	"""
	Blend two images with the given blend mode

	image - the image to be pasted on top (if None, returns overImage)
	blendMode - the mode to use when combining images
	overImage - the image will be pasted over the top of this image (if None, returns image)
	position - the position to place the new image, relative to overImage (can be negative)
	resize - allow the resulting image to be resized if overImage extends beyond its bounds

	Most comprehensive list:
		https://docs.krita.org/Blending_Modes
	Excellent description of blend modes:
		http://emptyeasel.com/2008/10/31/explaining-blending-modes-in-photoshop-and-gimp-multiply-divide-overlay-screen/
	How they're implemented in gimp:
		https://www.linuxtopia.org/online_books/graphics_tools/gimp_advanced_guide/gimp_guide_node55_002.html
	For another python implementation (not all supported):
		https://github.com/flrs/blend_modes/blob/master/blend_modes/blend_modes.py#L138

	IMPORTANT: the image bits may be altered.  To prevent this, set image.immutable=True
	"""
	def _normal(Cb,Cs):
		return Cs
	def _multiply(Cb,Cs):
		return Cb*Cs
	def _screen(Cb,Cs):
		return Cb+Cs-(Cb*Cs)
	def _dissolve(Cb,Cs):
		# TODO: there is a bug.  instead of randomly merging pixels, it randomly merges color values
		rand=np.random.random(Cb.shape)
		return np.where(rand>0.5,Cb,Cs)
	def _darken(Cb,Cs):
		return np.minimum(Cb,Cs)
	def _colorBurn(Cb,Cs):
		# NOTE: gimp "burn" is a colorBurn, not a linearBurn
		return 1.0-((1.0-Cs)/Cb)
	def _linearBurn(Cb,Cs):
		return Cb+Cs-1.0
	def _lighten(Cb,Cs):
		return np.maximum(Cb,Cs)
	def _colorDodge(Cb,Cs):
		# NOTE: gimp "dodge" is a colorDodge, not a linearDodge
		return Cs/(1.0-Cb)
	def _linearDodge(Cb,Cs):
		return Cs+Cb
	def _overlay(Cb,Cs):
		# TODO: the colors saturation comes out a little higher than gimp, but close
		return np.where(Cs<=0.5,2.0*Cb*Cs,1.0-2.0*(1.0-Cb)*(1.0-Cs))
	def _hardOverlay(Cb,Cs):
		# this is a krita thing
		return np.where(Cb>0.5,_multiply(Cs,2.0*Cb),_divide(Cs,2.0*Cb-1.0))
	def _hardLight(Cb,Cs):
		return np.where(Cb<=0.5,_multiply(Cs,2.0*Cb),_screen(Cs,2.0*Cb-1.0))
	def _vividLight(Cb,Cs):
		return np.where(Cs>0.5,_colorDodge(Cb,Cs),_colorBurn(Cb,Cs))
	def _linearLight(Cb,Cs):
		return np.where(Cs>0.5,_linearDodge(Cb,Cs),_linearBurn(Cb,Cs))
	def _pinLight(Cb,Cs):
		# NOTE: I think this is right...?
		return np.where(Cb>0.5,_darken(Cb,Cs),_lighten(Cb,Cs))
	def _hardMix(Cb,Cs):
		# NOTE: I think this is right...?
		return np.where(Cb>0.5,1.0,0.0)
	def _difference(Cb,Cs):
		return np.abs(Cb-Cs)
	def _softLight(Cb,Cs):
		# NOTE: strangely both algos do the same thing, but look different than gimp
		#	yet the last algo is deliberately backwards, and that's what gimp does.  Is gimp backwards??
		def D(x):
			return np.where(x<=0.25,((16*x-12)*x+4)*x,np.sqrt(x))
		#return np.where(Cs<=0.5,Cb-(1.0-2.0*Cs)*Cb*(1.0-Cb),Cb+(2.0*Cs-1)*(D(Cb)-Cb))
		#return (1.0-Cb)*Cb*Cs+Cb*(1.0-(1.0-Cb)*(1.0-Cs))
		return (1.0-Cs)*Cs*Cb+Cs*(1.0-(1.0-Cs)*(1.0-Cb))
	def _exclusion(Cb,Cs):
		return Cb+Cs-2.0*Cb*Cs
	def _subtract(Cb,Cs):
		# NOTE:  You'd think the first algo would be correct, but gimp has it the opposite way
		#return Cb-Cs
		return Cs-Cb
	def _grainExtract(Cb,Cs):
		# NOTE:  You'd think the first algo would be correct, but gimp has it the opposite way
		#return Cb-Cs+0.5
		return Cs-Cb+0.5
	def _grainMerge(Cb,Cs):
		return Cb+Cs-0.5
	def _divide(Cb,Cs):
		# NOTE:  You'd think the first algo would be correct, but gimp has it the opposite way
		#return Cb/Cs
		return Cs/Cb
	def _hue(Cb,Cs):
		CbH=rgb2hsvArray(Cb)
		CsH=rgb2hsvArray(Cs)
		return hsv2rgbArray(np.dstack((CbH[:,:,0],CsH[:,:,1:])))
	def _saturation(Cb,Cs):
		CbH=rgb2hsvArray(Cb)
		CsH=rgb2hsvArray(Cs)
		return hsv2rgbArray(np.dstack((CsH[:,:,0],CbH[:,:,1],CsH[:,:,2])))
	def _value(Cb,Cs):
		CbH=rgb2hsvArray(Cb)
		CsH=rgb2hsvArray(Cs)
		return hsv2rgbArray(np.dstack((CsH[:,:,:2],CbH[:,:,2])))
	def _color(Cb,Cs):
		# TODO: Very close, but seems to lose some blue values compared to gimp
		CbH=rgb2hsvArray(Cb)
		CsH=rgb2hsvArray(Cs)
		return hsv2rgbArray(np.dstack((CbH[:,:,:2],CsH[:,:,2])))

	#------------------------------------

	ret=None
	if blendMode=='normal':
		ret=paste(image,overImage,position,resize)
		#ret=_blendArray(image,overImage,_normal)
	elif blendMode=='dissolve':
		ret=_blendArray(image,overImage,_dissolve)
	elif blendMode=='behind':
		# this is a brush only blend mode, so not implemented
		# what it does is paint on just alpha
		raise NotImplementedError()
	elif blendMode=='clear':
		# this is a brush only blend mode, so not implemented
		# what it does is paint alpha on solid areas (aka, erase)
		raise NotImplementedError()
	elif blendMode=='darken' or blendMode=='darkenOnly':
		ret=_blendArray(image,overImage,_darken)
	elif blendMode=='multiply':
		#ret=ImageChops.multiply(image,overImage)
		ret=_blendArray(image,overImage,_multiply)
	elif blendMode=='colorBurn' or blendMode=='burn':
		ret=_blendArray(image,overImage,_colorBurn)
	elif blendMode=='linearBurn':
		ret=_blendArray(image,overImage,_linearBurn)
	elif blendMode=='lighten' or blendMode=='lightenOnly':
		ret=_blendArray(image,overImage,_lighten)
	elif blendMode=='screen':
		#ret=ImageChops.screen(image,overImage)
		ret=_blendArray(image,overImage,_screen)
	elif blendMode=='colorDodge' or blendMode=='dodge':
		ret=_blendArray(image,overImage,_colorDodge)
	elif blendMode=='linearDodge' or blendMode=='add':
		#ret=ImageChops.add(image,overImage)
		ret=_blendArray(image,overImage,_linearDodge)
	elif blendMode=='addMod':
		ret=ImageChops.add_modulo(image,overImage)
	elif blendMode=='overlay':
		ret=_blendArray(image,overImage,_overlay)
	elif blendMode=='hardOverlay':
		ret=_blendArray(image,overImage,_hardOverlay)
	elif blendMode=='softLight':
		ret=_blendArray(image,overImage,_softLight)
	elif blendMode=='hardLight':
		ret=_blendArray(image,overImage,_hardLight)
	elif blendMode=='vividLight':
		ret=_blendArray(image,overImage,_vividLight)
	elif blendMode=='linearLight':
		ret=_blendArray(image,overImage,_linearLight)
	elif blendMode=='pinLight':
		ret=_blendArray(image,overImage,_pinLight)
	elif blendMode=='hardMix':
		ret=_blendArray(image,overImage,_hardMix)
	elif blendMode=='difference':
		#ret=ImageChops.difference(image,overImage)
		ret=_blendArray(image,overImage,_difference)
	elif blendMode=='exclusion':
		ret=_blendArray(image,overImage,_exclusion)
	elif blendMode=='subtract':
		#ret=ImageChops.subtract(image,overImage)
		ret=_blendArray(image,overImage,_subtract)
	elif blendMode=='subtractMod':
		ret=ImageChops.subtract_mod(image,overImage)
	elif blendMode=='divide':
		ret=_blendArray(image,overImage,_divide)
	elif blendMode=='hue':
		ret=_blendArray(image,overImage,_hue)
	elif blendMode=='saturation':
		ret=_blendArray(image,overImage,_saturation)
	elif blendMode=='color':
		ret=_blendArray(image,overImage,_color)
	elif blendMode=='luminosity' or blendMode=='value':
		ret=_blendArray(image,overImage,_value)
	elif blendMode=='lighterColor' or blendMode=='lighter':
		ret=ImageChops.lighter(image,overImage)
	elif blendMode=='darkerColor' or blendMode=='darker':
		ret=ImageChops.darker(image,overImage)
	elif blendMode=='and':
		ret=ImageChops.logical_and(image,overImage)
	elif blendMode=='or':
		ret=ImageChops.logical_or(image,overImage)
	elif blendMode=='grainExtract':
		ret=_blendArray(image,overImage,_grainExtract)
	elif blendMode=='grainMerge':
		ret=_blendArray(image,overImage,_grainMerge)
	else:
		raise Exception('ERR: Unknown blend mode "'+blendMode+'"')
	return ret


def composite(image,overImage,opacity=1.0,blendMode='normal',mask=None,position=(0,0),resize=True):
	"""
	A full-fledged image compositor

	image - the image to be pasted on top (if None, returns overImage)
	overImage - the image will be pasted over the top of this image (if None, returns image)
	opacity - adjust the opacity of the overImage before blending
	blendMode - the mode to use when combining images
	position - the position to place the new image, relative to overImage (can be negative)
	resize - allow the resulting image to be resized if overImage extends beyond its bounds

	returns: a composited image, or None if both image and overImage are None

	IMPORTANT: the image bits may be altered.  To prevent this, set image.immutable=True
	"""
	if image==None or opacity<=0.0:
		return overImage
	if overImage==None:
		if opacity==1.0 and mask==None and position==(0,0):
			# there is nothing to change
			return image
		else:
			# create a blank background
			overImage=Image.new(maxMode(image,requireAlpha=True),(int(image.width+position[0]),int(image.height+position[1])))
	if mask!=None: # apply mask BEFORE opacity
		image=setAlpha(image,mask)
	if opacity!=1.0: # apply opacity before blending
		image=adjustOpacity(image,opacity)
	return blend(image,blendMode,overImage,position,resize)


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
		img1=None
		img2=None
		blendMode='normal'
		custom=None
		opacity=1.0
		mask=None
		for arg in sys.argv[1:]:
			if arg.startswith('-'):
				arg=[a.strip() for a in arg.split('=',1)]
				if arg[0] in ['-h','--help']:
					printhelp=True
				elif arg[0]=='--opacity':
					opacity=float(arg[1])
				elif arg[0]=='--blendMode':
					blendMode=arg[1].strip()
				elif arg[0]=='--mask':
					mask=Image.open(arg[1])
				elif arg[0]=='--eqn':
					custom=arg[1]
				elif arg[0]=='--save':
					print 'Compositing'
					if custom==None:
						final=composite(img1,img2,opacity,blendMode,mask)
					else:
						final=generalBlend(img1,custom,img2,opacity,position=(0,0),resize=True)
					print 'Saving'
					final.save(arg[1])
					print 'Done'
				elif arg[0]=='--show':
					print 'Compositing'
					if custom==None:
						final=composite(img1,img2,opacity,blendMode,mask)
					else:
						final=generalBlend(img1,custom,img2,opacity,position=(0,0),resize=True)
					print 'Showing'
					final.show()
					while True:
						import time
						time.sleep(0.5)
					print 'Done'
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				if img1==None:
					img1=Image.open(arg)
					print 'Loaded image A: '+arg
				else:
					img2=Image.open(arg)
					print 'Loaded image B: '+arg
	if printhelp:
		print 'Usage:'
		print '  blendModes.py image1 image2 [options]'
		print 'Options:'
		print '   --opacity=1.0 ......... set the opacity of the blend'
		print '   --blendMode=normal .... blend mode to use'
		print '   --eqn=equation ........ create a custom blendMode filter!'
		print '   --mask=filename ....... alpha mask to use'
		print '   --save=filename ....... save the current composited image'
		print '   --show ................ show the current composited image'