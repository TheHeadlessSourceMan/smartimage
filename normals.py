'''
Name: normap.py
Author: K. Sornen
Copyright: K. Sornen 2009
License: GPL, THIS SOFTWARE IS PROVIDED FREE "AS IS" WITHOUT 
ANY EXPRESSED OR IMPLIED WARRANTIES

From here:
https://blenderartists.org/t/ripples-waves-normalmaps-and-textures-with-numpy-scipy-and-matplotlib/454787/8
'''
try:
	# first try to use bohrium, since it could help us accelerate
	# https://bohrium.readthedocs.io/users/python/
	import bohrium as np
except ImportError:
	# if not, plain old numpy is good enough
	import numpy as np
from PIL import Image
from scipy.ndimage import filters


class Normalmap(object):
    def __init__(self, img):
        """ img is a gray scale image as a float64 matrix 
            to be turned into a normalmap """
        self.img = img.astype(np.float64) # convert to float64 just in case
        self.shape = self.img.shape
        
    def get(self, type = 'smooth', mode='reflect'):
        """ type can be 'smooth' or 'fine'
            mode can be 'reflect','constant','nearest','mirror', 'wrap' for handling borders """ 
        gradfn = {'smooth':self.prewittgrad, 'fine':self.basicgrad}[type]
        gradx, grady = gradfn()
        # x, y and z below are now the gradient matrices,
        # each entry from x,y,z is a gradient vector at an image point
        x = filters.convolve(self.img, gradx, mode=mode)
        y = filters.convolve(self.img, grady, mode=mode)
        # norm is the magnitude of the x,y,z vectors, 
        # each entry is the magnitude of the gradient at an image point and z*z = 1
        norm = np.sqrt(x*x+y*y+1)  
        # divide by the magnitude to normalise
        # as well scale to an image: negative 0-127, positive 127-255
        x,y = [a/norm*127.0+128.0 for a in (x,y)] 
        z = np.ones(self.shape)/norm # generate z, matrix of ones, then normalise
        z = z*255.0 # all positive
        # x, -y gives blender form 
        # convert to int, transpose to rgb and return the normal map        
        return np.array([x, -y, z]).transpose(1,2,0).astype(np.uint8) 
        
    def prewittgrad(self):
        """ prewitt gradient """
        gradx = np.array([1.0,1.0,1.0]).reshape(3,1)*np.array([1.0,0.0,-1.0])/3.0
        grady = np.array([1.0,0.0,-1.0]).reshape(3,1)*np.array([1.0,1.0,1.0])/3.0
        return gradx, grady
    
    def basicgrad(self):
        """ basic gradient """
        gradx = np.array([1,-1]).reshape(1,2)
        grady = np.array([1,-1]).reshape(2,1)
        return gradx, grady
   
if __name__ == '__main__':
    
    pmgc = plt.imread('sc.png').astype(np.float64)
    pmgc = pmgc.sum(axis=2)  # sum RGB to give gray scale 
    pmgf = plt.imread('sf.png').astype(np.float64)
    pmgf = pmgf.sum(axis=2)  # sum RGB to give gray scale 
    pmg = pmgc - pmgf/50.0 # subtract and scale images
    nmap = Normalmap(pmg)
    nimg = nmap.get('smooth')
    plt.imshow(nimg, origin = 'upper')
    plt.show()
    """ If you want to save the image uncomment these below """
    pilimg = Image.fromarray(nimg, 'RGB')
    pilimg.save('ns.png')
