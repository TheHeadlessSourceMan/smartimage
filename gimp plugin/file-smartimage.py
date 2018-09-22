#!/usr/bin/env python
"""
Gimp plugin for loading/saving the smartimage file format
"""
import os
from gimpfu import *


# Some common info about this file type
fileTypeName='smartimage'
fileExtensions=['simg','simt']
fileMimeType='image/smartimage+xml' # TODO: is this correct?
fileLocationProtocols='http:,ftp:,https:,sftp:,file:'
descriptionLoad='load a '+fileTypeName+' ('+(', '.join(fileExtensions))+') file'
descriptionSave='save a '+fileTypeName+' ('+(', '.join(fileExtensions))+') file'
canLoad=True
canSave=True
author='KC Eilander'
copyrightHolder=author
copyrightYear=2018

	
# ------------ Saving
if canSave:
	
	def saveFile(img,drawable,filename,raw_filename):
		raise NotImplementedError()
	
	# when we are queried, specify that we are a save handler
	def register_save_handlers():
		gimp.register_save_handler('file-'+fileTypeName+'-save',','.join(fileExtensions),fileLocationProtocols)
	
	# register all that
	register(
		'file-'+fileTypeName+'-save',
		descriptionSave,
		descriptionSave,
		author,
		copyrightHolder,
		str(copyrightYear),
		fileTypeName,
		'*',
		[
			(PF_IMAGE,"image","Input image",None),
			(PF_DRAWABLE,"drawable","Input drawable",None),
			(PF_STRING,"filename","The name of the file",None),
			(PF_STRING,"raw-filename","The name of the file",None),
		],
		[],
		saveFile,
		on_query=register_save_handlers,
		menu='<Save>'
	)

	
# ------------ Loading
if canLoad:
	
	def getThumbnail(filename,thumb_size):
		raise NotImplementedError()

	def loadFile(filename,raw_filename):
		raise NotImplementedError()

	# when we are queried, specify that we are a load handler
	def register_load_handlers():
		gimp.register_load_handler('file-'+fileTypeName+'-load',','.join(fileExtensions),fileLocationProtocols)
		pdb['gimp-register-file-handler-mime']('file-'+fileTypeName+'-load',fileMimeType)
		pdb['gimp-register-thumbnail-loader']('file-'+fileTypeName+'-load','file-'+fileTypeName+'-load-thumb')
	
	# register all that
	register(
		'file-'+fileTypeName+'-load',
		descriptionLoad,
		descriptionLoad,
		author,
		copyrightHolder,
		str(copyrightYear),
		fileTypeName,
		None,
		[
			(PF_STRING,'filename','The name of the file to load',None),
			(PF_STRING,'raw-filename','The name entered',None),
		],
		[(PF_IMAGE,'image','Output image')],#results. Format (type,name,description)
		loadFile,
		on_query=register_load_handlers,
		menu="<Load>",
	)
	register(
		'file-'+fileTypeName+'-load-thumb',
		descriptionLoad,
		descriptionLoad,
		author,
		copyrightHolder,
		str(copyrightYear),
		None,
		None,
		[
			(PF_STRING,'filename','The name of the file to load',None),
			(PF_INT,'thumb-size','Preferred thumbnail size',None),
		],
		[
			(PF_IMAGE,'image','Thumbnail image'),
			(PF_INT,'image-width','Width of full-sized image'),
			(PF_INT,'image-height','Height of full-sized image')
		],
		getThumbnail,
	)


main()
