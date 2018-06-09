#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Implementation of photoshop/gimp blend modes in python.
"""
from PIL import Image, ImageChops, ImageEnhance
import numpy as np


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


def applyMask(image,mask):
	"""
	image: the image to be changed
	mask: a mask image to use to cut out the image it can be:
		image with alpha channel to steal
		-or-
		grayscale (white=opaque, black=transparent)

	returns: adjusted image

	IMPORTANT: the image bits may be altered.  To prevent this, set image.immutable=True
	"""
	if image==None or mask==None:
		return image
	if hasattr(image,'immutable') and image.immutable==True:
		image=image.copy()
	if hasAlpha(image):
		if mask.width>image.width or mask.height>image.height:
			image=extendImageCanvas(image,(mask.width,mask.height),extendColor=(0,0,0,0))
		elif mask.width<image.width or mask.height<image.height:
			mask=extendImageCanvas(mask,(image.width,image.height),extendColor=0)
		channels=np.asarray(image)
		alpha=np.minimum(channels[:,:,-1],mask) # Darken blend mode
		channels=np.dstack((channels[:,:,0:-1],alpha))
		image=Image.fromarray(channels.astype('uint8'),image.mode)
	else:
		image.putalpha(mask)
	return image


def hasAlpha(imgMode):
	"""
	can pass in a mode string or an image
	"""
	if type(imgMode)!=str:
		imgMode=imgMode.mode
	return imgMode[-1]=='A'


def isColor(imgMode):
	"""
	can pass in a mode string or an image
	"""
	if type(imgMode)!=str:
		imgMode=imgMode.mode
	return imgMode[0]!='L'


def maxMode(mode1,mode2='L',requireAlpha=False):
	"""
	Finds the maximum color mode.

	mode1, mode2 can either one be a textual image mode, or an image

	returns: textual image mode
	"""
	if isColor(mode1) or isColor(mode2):
		ret='RGB'
	else:
		ret='L'
	if requireAlpha or hasAlpha(mode1) or hasAlpha(mode2):
		ret=ret+'A'
	return ret


def extendImageCanvas(pilImage,newBounds,extendColor=(128,128,128,0)):
	"""
	Make pilImage the correct canvas size/location.

	:param pilImage: the image to move
	:param newBounds - (w,h) or (x,y,w,h) or Bounds object
	:extendColor: color to use when extending the canvas (automatically choses image mode based on this color)

	NOTE: always creates a new image, so no original bits are altered
	"""
	if type(newBounds)==tuple:
		if len(newBounds)>2:
			x,y,w,h=newBounds
		else:
			x,y=0,0
			w,h=newBounds
	else:
		x,y,w,h=newBounds.x,newBounds.y,newBounds.w,newBounds.h
	if w<pilImage.width or h<pilImage.height:
		raise Exception('Cannot "extend" canvas to smaller size. ('+str(pilImage.width)+','+str(pilImage.height)+') to ('+str(w)+','+str(h)+')')
	if type(extendColor) not in [list,tuple] or len(extendColor)<2:
		mode="L"
	elif len(extendColor)<4:
		mode="RGB"
	else:
		mode="RGBA"
	mode=maxMode(mode,pilImage)
	img=Image.new(mode,(int(w),int(h)),extendColor)
	x=max(0,w/2-pilImage.width/2)
	y=max(0,h/2-pilImage.height/2)
	if hasAlpha(mode):
		if not hasAlpha(pilImage):
			pilImage=pilImage.convert(maxMode(pilImage,requireAlpha=True))
		img.alpha_composite(pilImage,dest=(int(x),int(y)))
	else:
		img.paste(pilImage,box=(int(x),int(y)))
	return img


def paste(image,overImage,position=(0,0),resize=True):
	"""
	A simple, dumb, paste operation like PIL's paste, only automatically uses alpha

	image - the image to be pasted on top (if None, returns overImage)
	overImage - the image will be pasted over the top of this image (if None, returns image)
	position - the position to place the new image, relative to overImage (can be negative)
	resize - allow the resulting image to be resized if overImage extends beyond its bounds

	returns: a combined image, or None if both image and overImage are None

	NOTE: this is effectively the same as doing blend(image,'normal',overImage,position,resize)

	IMPORTANT: the image bits may be altered.  To prevent this, set image.immutable=True
	"""
	if image==None:
		return overImage
	if overImage==None:
		if position==(0,0): # no change
			return image
		else:
			# create a blank background
			overImage=Image.new(maxMode(image,requireAlpha=True),(int(image.width+position[0]),int(image.height+position[1])))
	elif (image.width+position[0]>overImage.width) or (image.height+position[1]>overImage.height):
		# resize the overImage if necessary
		newImg=Image.new(
			size=(int(max(image.width+position[0],overImage.width)),int(max(image.height+position[1],overImage.height))),
			mode=maxMode(image,overImage,requireAlpha=True))
		paste(overImage,newImg)
		overImage=newImg
	elif hasattr(overImage,'immutable') and overImage.immutable==True:
		# if it is flagged immutable, create a copy that we are allowed to change
		overImage=overImage.copy()
	# do the deed
	if hasAlpha(image):
		# TODO: which of these two lines is best?
		#overImage.paste(image,position,image) # NOTE: (image,(x,y),alphaMask)
		if overImage.mode!=image.mode:
			overImage=overImage.convert(image.mode)
		overImage.alpha_composite(image,dest=(int(position[0]),int(position[1])))
	else:
		overImage.paste(image,(int(position[0]),int(position[1])))
	return overImage


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


def rgb_to_hsv(rgb):
	"""
	This comes from scikit-image:
		https://github.com/scikit-image/scikit-image/blob/master/skimage/color/colorconv.py
	"""
	out = np.empty_like(rgb)
	# -- V channel
	out_v = rgb.max(-1)
	# -- S channel
	delta = rgb.ptp(-1)
	# Ignore warning for zero divided by zero
	old_settings = np.seterr(invalid='ignore')
	out_s = delta / out_v
	out_s[delta == 0.] = 0.
	# -- H channel
	# red is max
	idx = (rgb[:, :, 0] == out_v)
	out[idx, 0] = (rgb[idx, 1] - rgb[idx, 2]) / delta[idx]
	# green is max
	idx = (rgb[:, :, 1] == out_v)
	out[idx, 0] = 2. + (rgb[idx, 2] - rgb[idx, 0]) / delta[idx]
	# blue is max
	idx = (rgb[:, :, 2] == out_v)
	out[idx, 0] = 4. + (rgb[idx, 0] - rgb[idx, 1]) / delta[idx]
	out_h = (out[:, :, 0] / 6.) % 1.
	out_h[delta == 0.] = 0.
	np.seterr(**old_settings)
	# -- output
	out[:, :, 0] = out_h
	out[:, :, 1] = out_s
	out[:, :, 2] = out_v
	# remove NaN
	out[np.isnan(out)] = 0
	return out


def hsv_to_rgb(hsv):
	"""
	This comes from scikit-image:
		https://github.com/scikit-image/scikit-image/blob/master/skimage/color/colorconv.py
	"""
	hi = np.floor(hsv[:, :, 0] * 6)
	f = hsv[:, :, 0] * 6 - hi
	p = hsv[:, :, 2] * (1 - hsv[:, :, 1])
	q = hsv[:, :, 2] * (1 - f * hsv[:, :, 1])
	t = hsv[:, :, 2] * (1 - (1 - f) * hsv[:, :, 1])
	v = hsv[:, :, 2]
	hi = np.dstack([hi, hi, hi]).astype(np.uint8) % 6
	out = np.choose(hi, [np.dstack((v, t, p)),
		 np.dstack((q, v, p)),
		 np.dstack((p, v, t)),
		 np.dstack((p, q, v)),
		 np.dstack((t, p, v)),
		 np.dstack((v, p, q))])
	return out


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
			topHSV=rgb_to_hsv(topRGBA)
			break
	for tag in 'CMYK':
		if equation.find('top'+tag)>=0:
			topCMYK=rgb_to_cmyk(topRGBA)
			break
	botRGBA=np.asarray(botImage)/shift
	for tag in 'HSV':
		if equation.find('bot'+tag)>=0:
			botHSV=rgb_to_hsv(botRGBA)
			break
	for tag in 'CMYK':
		if equation.find('bot'+tag)>=0:
			botCMYK=rgb_to_cmyk(botRGBA)
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
		final=hsv_to_rgb(final)
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
		CbH=rgb_to_hsv(Cb)
		CsH=rgb_to_hsv(Cs)
		return hsv_to_rgb(np.dstack((CbH[:,:,0],CsH[:,:,1:])))
	def _saturation(Cb,Cs):
		CbH=rgb_to_hsv(Cb)
		CsH=rgb_to_hsv(Cs)
		return hsv_to_rgb(np.dstack((CsH[:,:,0],CbH[:,:,1],CsH[:,:,2])))
	def _value(Cb,Cs):
		CbH=rgb_to_hsv(Cb)
		CsH=rgb_to_hsv(Cs)
		return hsv_to_rgb(np.dstack((CsH[:,:,:2],CbH[:,:,2])))
	def _color(Cb,Cs):
		# TODO: Very close, but seems to lose some blue values compared to gimp
		CbH=rgb_to_hsv(Cb)
		CsH=rgb_to_hsv(Cs)
		return hsv_to_rgb(np.dstack((CbH[:,:,:2],CsH[:,:,2])))

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
		image=applyMask(image,mask)
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