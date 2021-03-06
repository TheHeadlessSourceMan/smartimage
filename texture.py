# -*- coding: utf-8 -*-
"""
This is a layer for creating procedural textures
"""
from imageTools import *
from smartimage.layer import *
from smartimage.errors import SmartimageError


class Texture(Layer):
    """
    This is a layer for creating procedural textures
    """

    def __init__(self,parent,xml):
        Layer.__init__(self,parent,xml)

    @property
    def type(self):
        """
        can be
            "voronoi" - a cell-like organic pattern
            "clock" - sweep waveform around like clock hands.
                Direction becomes where the highlight is pointing.
            "waveform" - [default] a waveform repeated across a given angle, or "circular"
            "clouds" - creates a cloud-like texture
            "random" - creates random confetti noise
        """
        return self._getProperty('type','waveform')

    @property
    def seed(self)->Union[int,None]:
        """
        random seed to ensure repeatability, especially when testing
        """
        seed=self._getProperty('seed',None)
        if seed is not None:
            seed=int(seed)
        return seed

    @property
    def waveform(self):
        """
        waveform to repeat.
        Can be
            "sine"
            "square"
            "triangle"
            "saw"
            or a custom SVG-style curve (default="sine")
        """
        return self._getProperty('waveform','sine')

    @property
    def frequency(self):
        """
        an "x,y" specifying how many times to repeat in each direction
        (default=1)
        """
        f=self._getProperty('frequency','1').split(',',1)
        f=[float(x) for x in f]
        if len(f)<2:
            f.append(f[0])
        return f

    @property
    def noise(self):
        """
        a percentage specifying the amount of noise.

        0.0 is simply the profile where 1.0 is all noise, no profile

        (default=0.2)
        """
        return self._getPropertyPercent('noise',0.2)

    @property
    def noiseBasis(self):
        """
        noise basis.  Can be "random","perlin","voronoi"
        """
        return self._getProperty('noiseBasis','perlin')

    @property
    def noiseOctaves(self):
        """
        how detailed the noise is [default=4]
        """
        return int(self._getProperty('noiseOctaves','4'))

    @property
    def noiseSoften(self):
        """
        a percent type where 0.0 is the raw noise and 1.0 is a blur
        """
        return self._getPropertyPercent('noiseSoften',0.0)

    @property
    def direction(self):
        """
        can be an angle value, or "circular" [default 0]
        """
        d=self._getProperty('direction','0')
        if d=='circular':
            return d
        return float(d)

    @property
    def numPoints(self):
        """
        for voronoi textures [default=20]
        """
        return int(self._getProperty('numPoints','20'))

    @property
    def invert(self):
        """
        for convenience, flip the blacks and whites
        """
        return self._getProperty('invert','f')[0] in ['t','T','1','y','Y']

    @property
    def image(self):
        import time
        start=time.time()
        if self.type=='voronoi':
            img=voronoi(self.size,self.numPoints,'simple',self.invert,seed=self.seed)
        elif self.type=='random':
            img=smoothNoise(self.size,1.0-self.noiseSoften,seed=self.seed)
        elif self.type=='clouds':
            img=turbulence(self.size,seed=self.seed)
        elif self.type=='waveform':
            img=waveformTexture(self.size,self.waveform,self.frequency,self.noise,
                self.noiseBasis,self.noiseOctaves,self.noiseSoften,self.direction,
                self.invert,seed=self.seed)
        elif self.type=='clock':
            img=clock2(self.size,self.waveform,self.frequency,self.noise,
            self.noiseBasis,self.noiseOctaves,self.noiseSoften,self.direction,
            self.invert,seed=self.seed)
        else:
            raise SmartimageError(self,'texture type "%s" not implemented'%self.type)
        img=pilImage(img)
        img.immutable=True # mark this image so that compositor will not alter it
        end=time.time()
        return img