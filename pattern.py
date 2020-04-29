# -*- coding: utf-8 -*-
"""
This is a layer for creating repeating patterns
"""
from imageTools import *
from smartimage.layer import *


class Pattern(Layer):
    """
    This is a layer for creating repeating

    TODO: this could/should overlap with gradients, as in the CSS magic:
        http://lea.verou.me/2010/12/checkered-stripes-other-background-patterns-with-css3-gradients/
        http://lea.verou.me/2011/04/css3-patterns-gallery-and-a-new-pattern/
    """

    def __init__(self,parent:Layer,xml:str):
        Layer.__init__(self,parent,xml)

    @property
    def mortarThickness(self):
        """
        how thick the mortar is
        """
        return self._getProperty('mortarThickness','0')

    @property
    def repeat(self)->Tuple[str,str]:
        """
        an "x,y" value that can be:
            "once" - show only once (same as "top" or "left")
            "all" - [default] repeat all the way across
            "stretch" - display once stretched to the maximum size
            "center" or "middle" - display once centererd in the size
            "top","left","right", or "bottom" - display once at that particular edge
            "maintainAspect" - keep the same aspect ratio based on whatever the opposite value is
            "maximize"-a lone value, maximizes pattern just large enough that all screen is covered
            "minimize"- a lone value, makes the
            "bricks" - tessalate in a brick wall pattern
            "isometric" - tessalate on an isometric triangle grid
                (for instance, like a honeycomb pattern)

        always returns [repeatX,repeatY]
        """
        repeat=self._getProperty('repeat','all')
        repeat=repeat.replace(' ','').split(',',1)
        if len(repeat)<2:
            repeat.append(repeat[0])
        return repeat

    @property
    def image(self)->Union[PilPlusImage,None]:
        """
        final image generated from the given pattern
        """
        raise NotImplementedError()
