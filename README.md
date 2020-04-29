# smartimage
![Status: Stable](https://img.shields.io/badge/status-stable-green.svg?style=plastic)
![Python Version: 2.7](https://img.shields.io/badge/Python%20Version-2.7-blue.svg?style=plastic)
![Release Version: 1.0](https://img.shields.io/badge/Release%20Version-1.0-green.svg?style=plastic)
[![webpage:click here](https://img.shields.io/badge/webpage-click%20here-blue.svg?style=plastic)](https://TheHeadlessSourceMan.wordpress.com)

License - UNDECIDED.  Probably something where it's open source / commercial use, but all changes have to go through me.  (Don't want anybody "embrace and extending" it to death!)

The future of image editor formats!  Smartimage is a powerful and intuitive format for non-destructively editing images.

Call it analogous to a photoshop .psd file, or gimp .xcf in that it contains all image layers and components.  Yet although it supports everything the other formats do, it has much more, including templates and rescaling smartly to fit different media.


Features:
---------

* Extensive layering system maintains editablility.
	Didn't like that blur operation you did 15 steps ago?  No problem!  You can adjust it now!
* Fully supports all common idioms such as layer visibility, blend modes, and masks.
* No need to worry about missing fonts since Text layers come complete with online font finding.
* No need to worry about missing plug-ins because they are stored with the image, rather than the application!
* Automatic region-of-interest-based image sizing.
	No need to rework the same image for Facebook, Pinterest, etc, etc.
	Specify the region of interest manually, or allow the tool to automatically create one.
* Support for generating images with textures, patterns, and particles.
* Basic support for pseudo-3d elements (normal maps, bump maps, simple lighting)
* Support for high dynamic range pixels, multi-page documents, slide shows, and animations.
* Find yourself creating the same things over and over again?  Try templates!
	With template forms it can either ask the user for input, or even auto-generate images from the command line, analogous to an xml-powered imagemagick!
	Of course, these can be designed graphically in the image editor.
* Math shorthand makes sophisticated image transformations a breeze.
	e.g. horizontally fade from red to blue with R=1-X,B=X
* Colorspaces are automatic!
	Ever try to erase on a layer with no transparency, it goes black, not clear, you have to undo, go up to image->mode->transparency->add alpha channel. Argh!
	Or what about trying to tweak the red channel of a black and white image?
	In smartimage, everything does what you want it to.
* Key building blocks like image morphology, colorspaces, and numberspaces (e.g. fft,wavelet,polar,...) are all built in.
* Modern zip+xml format (similar to .odf and the like) makes a file easily readable and modifiable by software or by hand.
	Yet despite all of the features, the format is simple and intuitive.
* XML Tags in a file are painted bottom-to-top order to mimic how we see layers in an editor.
* Has useful referencing features such as linking to other values and re-using layers
	@id @id.\_ and @id.attr can all be used to link to other values. (Has infinite loop safety mechanism.)
	And they're smart, too.  x="@layerId" knows that you mean x="@layerId.x"
* Comes with reference implementation and a draft gui program for viewing image structure.

FAQ:
----

Q. Is smartimage an image editor like Gimp or Photoshop?
A. Yes and no.  No, in that it is technically only a file format.  Yes in that an image can be created logically by hand.
	Consider that html is not a document editor as is MS Word, yet fully formatted documents can be still created with it.

Q. How can I open/save the smartimage format in my graphics app?
A. In addition to a provided editor and viewer, there will be plug-ins for popular programs such as Gimp, Photoshop, and Blender.  Given the versatility and os-independence of the reference implementation, adding more should be relatively simple)

Q. Which is better, a plug-in or a converter?
A. Generally, converting to another format will lose more features than a plug-in.
	For example OpenRaster does not support layer masks, so smartimage->OpenRaster->gimp would lose that feature where smartimage->gimp(via plugin) would not.

Q. How do I render smartimage to regular images from the command line?
A. The reference implementation has a full compliment of tools to do this, including the ability to fill in forms!
	Read the --help string for all the features, but to get you started:
		python smartimage.py myImage.simg --noui --set=name=value --save=outImage.jpg

Q. Is this non-gui image editing similar to Imagemagick?
A. Many of the same results of smartimage could be achieved using a combination of Imagemagick and shell scripts.
	However, not only would it grow unwieldy, but more importantly, it would not allow for interactive graphical editors.  Smartimage does both things!

Q. Is this like SVG?
A. Yes, in that it is a manually-editable XML-based format.
	No, in that SVG is primarily for vector drawings.
	Also features such as javascript were intentionally omitted to ease implementation. (How many SVG implementations can you name?)

Q. Why not .xcf of .psd format?
A. Not only do they not support key requirements (full operation editablility, region-of-interest, etc) but they are also binary and hard to edit.
	
Q. Why not OpenRaster format?
A. OpenRaster is a good idea, but Smartimage has a number of critical differences:
	* Smartimage encapsulates all of the features of an image editor. 
		For instance, OpenRaster doesn't even support layer masks!
	* Designed to be fit with the way a graphic editor works over conforming to established standards.
		For instance, OpenRaster only uses SVG blend modes, which are sometimes mathematically the same, and are not every blend mode that a Photoshop user expects.
	* Maintains full editablility
		OpenRaster has similar groups ("stacks", which is not a term familiar to users) but beyond that, everything is a compiled image - not suitable for going back and changing later!

Q. Can this work with OpenRaster?
A. There will be a converter to go to/from openraster. (NOTE: some features will be lost)
	In addition, it is entirely possible for a smartimage.xml to live inside an OpenRaster zip, making the possibility of a combined/hybrid format possible.
	This will be explored further.
		
Q. Can my webpage directly create/serve the results of a smartimage?
A. If your web platform is python-based like Django, you can access the python implementation directly.
	Otherwise, you can use its command-line interface instead.  This could theoretically be used directly from CGI, but in reality you'd want a lot more safety filtering than that.

Q. I'm comfortable with XML/HTML.  Can I edit a smartimage by hand?
A. Yes!  Simply unzip it, crack open smartimage.xml, and start playing around.
	In fact, the reference viewer was designed with this in mind.  It watches the file and reloads every time it sees you save.

Q. I use PIL in python.  How do I convert to PIL image?
A. Every Layer object should work as a PIL image directly.  Or you can get/set layer.image

Q. I use numpy in python.  How do I convert to numpy array?
A. Use layer.numpyArray to get/set that.

Q. Can I extend this format?
A. Read the section of the standard labeled "Extending".
	The short answer is you can play around with stuff in your basement, but not release it anywhere without gaining official approval.
	
Q. Can I use the reference implementation in my software?
A. Yes.  It's all open source and cuddly. (Just so long as you don't change the format itself!)
	
TODO:
-----

* need to have layers that extend beyond image for things like rotation
* need to translate font friendly names to file names \"Viner Hand ITC Regular\" -\> \"VINERITC.TTF\"
* may want modifiers to be less generic?
* gimp/photoshop plugin to read this format?
* dragdrop handler that uses auto-assign variables
