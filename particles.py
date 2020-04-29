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
    def randomize(self)->NoReturn:
        """
        randomize the particle locations
        """
        randies={}
        for r in self._getProperty('randomize','').split(','):
            r=[kv.strip() for kv in r.split('=',1)]
            if r[1].find('|')>=0:
                r[1]=r[1].split('|')
            randies[r[0]]=r[1]
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
        an image to define where particles can land
        """
        self._getImageProperty('dispersionMap')

    @property
    def qty(self)->int:
        """
        how many particles to create
        """
        return int(self._getProperty('qty','1'))

    def nextRandomSet(self)->List[Tuple[float,float]]:
        """
        Returns the next set of randomize values
        """
        values={}
        for k,v in list(self.randomize.items()):
            if isinstance(v,list):
                v=random.choice(v,seed=self.seed)
            v=v.split('..',1)
            if v:
                v=random.uniform(float(v[0]),v[1],seed=self.seed)
            values[k]=v
        return values

    @property
    def image(self)->Union[PilPlusImage,None]:
        """
        Image generated from random particles
        """
        for i in range(self.qty):
            variables=self.nextRandomSet()
            child=random.choice(self.children,seed=self.seed)
            # TODO: Need to re-set the local variables and draw each child layer
            raise NotImplementedError()
        return img