# smartimage
![Status: Stable](https://img.shields.io/badge/status-stable-green.svg?style=plastic)
![Python Version: 2.7](https://img.shields.io/badge/Python%20Version-2.7-blue.svg?style=plastic)
![Release Version: 1.0](https://img.shields.io/badge/Release%20Version-1.0-green.svg?style=plastic)
[![webpage:click here](https://img.shields.io/badge/webpage-click%20here-blue.svg?style=plastic)](https://TheHeadlessSourceMan.wordpress.com)

License - UNDECIDED.  Probably something where it's open source / commercial use, but all changes have to go through me.  (Don't want anybody "embrace and extending" it to death!)

The future of image editor formats!

Smartimage is a format for non-destructively constructed images that can be used as templates and rescale smartly to fit different media.

It is mainly analgous to a photoshop .psd file, or gimp .xcf in that it contains all image layers and components.

It is different in the regard that:
* it is all self-congtained
* modern zip+xml format (similar to .odf and the like) makes it easily modifiable
* It can also do templates and auto-generate images based on input, so it is analgous to an xml-powered imagemagick.  
* contains advanced features such as interlinking values and re-using layers

Features:
---------

* Works great with zipped, or non-zipped resources.
* Automatic heatmap-based rescaling. NICE!
* Solid color layers.
* Image layers.
* Modifier layers (not all modifiers finalized/tested).
* Text layers.
* Any file reference can be replaced with \#layerId
* I love the way fonts work. It will try to download missing fonts automagically!
* @id @id.\_ and @id.attr links working. (Has infinite loop safety mechanism.)
* @templateName values working
* Draft XSD format.
* Blend modes are all working with some semblance of correctness.
* Tags in file are painted bottom-to-top to mimic how we see layers in an editor.
* Draft gui program for viewing images.


TODO:
-----

* need to have layers that extend beyond image for things like rotation
* need to translate font friendly names to file names \"Viner Hand ITC Regular\" -\> \"VINERITC.TTF\"
* may want modifiers to be less generic?
* gimp/photoshop plugin to read this format?
* dragdrop handler that uses auto-assign variables
