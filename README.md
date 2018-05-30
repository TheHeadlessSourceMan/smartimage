---
title: smartimage
---

smartimage Non-destructively constructed images that can be used as
templates and rescale smartly to fit different media.

Features:
---------

::: {.indent}
Works great with zipped, or non-zipped resources.

Automatic heatmap-based rescaling. NICE!

Solid color layers.

Image layers.

Modifier layers (not all modifiers finalized/tested).

Text layers.

Any file reference can be replaced with \#layerId

I love the way fonts work. It will try to download missing fonts
automagically!

@id @id.\_ and @id.attr links working. (Has infinite loop safety
mechanism.)

@templateName values working

Draft XSD format.

Blend modes are all working with some semblance of correctness.

Tags in file are painted bottom-to-top to mimic how we see layers in an
editor.

Draft gui program for viewing images.
:::

TODO:
-----

::: {.indent}
need to have layers that extend beyond image for things like rotation

need to translate font friendly names to file names \"Viner Hand ITC
Regular\" -\> \"VINERITC.TTF\"

may want modifiers to be less generic?

gimp/photoshop plugin to read this format?

dragdrop handler that uses auto-assign variables
:::