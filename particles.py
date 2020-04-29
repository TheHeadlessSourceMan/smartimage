# -*- coding: utf-8 -*-
"""
This is a particles type layer
"""
import random
from typing import *
from smartimage.layer import *


class Particles(Layer):
    """
    This is a particles type layer
    """

    def __init__(self,parent:Layer,xml:str):
        Layer.__init__(self,parent,xml)

    @property
    def randomize(self)->dict:
        """
        additional randomizers from the file

        :return: a dict of child values to be randomized, where each can be
            a) a maximum float value
            b) a 2-tuple range of float values
            c) a list of choices
        """
        randies={}
        for kv in self._getProperty('randomize','').split(','):
            kv=kv.strip()
            if kv=='':
                continue
            kv=[item.strip() for item in kv.split('=',1)]
            if kv[1].find('..')>=0:
                kv[1]=kv[1].split('..')
                kv[1]=(kv[1][0],kv[1][1])
            elif kv[1].find('|'):
                kv[1]=kv[1].split('|')
            randies[kv[0]]=kv[1]
        return randies

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
    def dispersionMap(self)->Union[PilPlusImage,None]:
        """
        an image to define where particles are more likely to land
        """
        ref=self._getProperty('dispersionMap')
        try:
            img=self.root.imageByRef(ref)
        except FileNotFoundError as e:
            raise SmartimageError(self,'Missing dispersionMap resource "%s"'%e.filename)
        return img

    @property
    def qty(self)->int:
        """
        how many particles to create
        """
        return int(self._getProperty('qty','1'))

    def randomizedValues(self,valsToRandomize:Dict[str,Union[float,Tuple[float,float],
        List[str]]]=None)->Dict[str,Union[str,float]]:
        """
        Selects a set of randomized values

        :valsToRandomize: a dict of key,values to randomize where each value can be
            a) a maximum float value
            b) a 2-tuple range of float values
            c) a list of choices
        """
        vals={}
        if valsToRandomize is None:
            return vals
        for k,v in valsToRandomize.items():
            if isinstance(v,list): # choice
                v=random.choice(v)
            elif isinstance(v,tuple): # range
                v=random.uniform(float(v[0]),float(v[1]))
            else: # max value only
                v=random.uniform(0.0,float(v))
            vals[k]=v
        return vals

    def renderImage(self,renderContext:RenderingContext=None)->Union[PilPlusImage,None]:
        """
        render this layer to a final image

        renderContext - used to keep track for child renders
            (Used internally, so no need to specify this)

        WARNING: Do not modify the image without doing a .copy() first!
        """
        image=None
        if self.root.cacheRenderedLayers and not self.dirty:
            if self._lastRenderedImage is not None:
                return self._lastRenderedImage
        if renderContext is None:
            renderContext=RenderingContext()
        if self.seed is not None: # set the random seed if necessary
            random.seed(self.seed)
        valsToRandomize=self.randomize
        locations=self.dispersionMap
        if locations is not None:
            locations=np.argsort(self.dispersionMap.ndarray)
        # keep a layer variable backup
        varBak=self._variables.copy()
        for _ in range(self.qty):
            # pick what we are drawing
            childLayer=random.choice(self.children)
            # randomize its values
            if valsToRandomize:
                #childLayer.dirty=True
                for k,v in self.randomizedValues(valsToRandomize).items():
                    self._variables[k]=v
            # randomize the location
            dispersionMap=self.dispersionMap
            if dispersionMap is None:
                childLayer.x=int(random.random()*(self.w-1))
                childLayer.y=int(random.random()*(self.h-1))
            else:
                pick=abs(int(random.random()*len(location)-random.random()*len(location)))
                location=locations[pick]
                childLayer.x=int(location[0])
                childLayer.y=int(location[1])
            # now draw it
            childImage=childLayer.renderImage(renderContext)
            image=composite(childImage,image,
                opacity=childLayer.opacity,blendMode=childLayer.blendMode,mask=childLayer.mask,
                position=childLayer.location,resize=True)
        self._variables=varBak
        return image