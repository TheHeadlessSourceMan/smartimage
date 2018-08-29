import math


class Bounds(object):
	"""
	A rectangular bounds representation with lots of unnecessary "cleverness".
	"""

	def __init__(self,*vals):
		self.clear()
		self.assign(vals)

	def clear(self):
		self.x=None
		self.y=None
		self.w=None
		self.h=None

	def repr(self):
		return str(self.points)

	def __len__(self):
		return len(self.points)

	def __getitem__(self,key):
		return self.points[key]

	def __iter__(self):
		return self.points.__iter__()

	def assign(self,points):
		self.clear()
		self.maximize(points)

	def copyBounds(self):
		"""
		create a copy of these bounds
		"""
		return Bounds(self)

	def maximize(self,morebounds):
		"""
		expands these bounds to encoumpass morebounds

		NOTE: if you don't want this object modified, use copyBounds() first
		"""
		if type(morebounds) in (list,tuple):
			if type(morebounds[0]) in (int,float):
				for i in range(len(morebounds)): # array of x,y points
					if i%2==0:
						if self.x==None or morebounds[i]<self.x:
							self.x=morebounds[i]
						if self.x2==None or morebounds[i]>self.x2:
							self.x2=morebounds[i]
					else:
						if self.y==None or morebounds[i]<self.y:
							self.y=morebounds[i]
						if self.y2==None or morebounds[i]>self.y2:
							self.y2=morebounds[i]
			else:
				for bounds in morebounds:
					self.maximize(bounds)
		else:
			if morebounds.x<self.x:
				self.x=morebounds.x
			if morebounds.x2>self.x2:
				self.x2=morebounds.x2
			if morebounds.y<self.y:
				self.y=morebounds.y
			if morebounds.y2>self.y2:
				self.y2=morebounds.y2

	@property
	def x2(self):
		if self.x==None or self.w==None:
			return None
		return self.x+self.w
	@property
	def y2(self):
		if self.y==None or self.h==None:
			return None
		return self.y+self.h
	@x2.setter
	def x2(self,x2):
		self.w=x2-self.x
	@y2.setter
	def y2(self,y2):
		self.h=y2-self.y

	@property
	def points(self):
		x=self.x
		y=self.y
		x2=self.x2
		y2=self.y2
		return ((x,y),(x2,y),(x2,y2),(x,y2))
	@points.setter
	def points(self,points):
		self.assign(points)

	@property
	def location(self):
		return (self.x,self.y)
	@location.setter
	def location(self,location):
		self.x,self.y=location

	@property
	def size(self):
		return (self.w,self.h)
	@size.setter
	def size(self,size):
		self.w,self.h=size
		
	@property
	def offset(self):
		return (self.x,self.y)
	@offset.setter
	def offset(self,offset):
		self.x,self.y=offset

	@property
	def center(self):
		return (self.x+self.w/2,self.y+self.h/2)
	@center.setter
	def center(self,center):
		self.x=center[0]+self.w/2
		self.y=center[0]+self.y/2

	def __contains__(self,points):
		"""
		so you can do something like
			if (10,10) in bounds:
		"""
		return self.pointTest(points)
	def pointTest(self,points):
		"""
		check to see if any point is within these bounds

		point can be a single point or a list of points
		"""
		if type(points)==list:
			for point in points:
				if self.pointTest(point):
					return True
			return False
		return points[0]>=x and points[0]<=x2 and points[1]>=y and points[1]<=y2

	def isEndlosedBy(self,otherBounds):
		"""
		check to see if we are totally enclosed by otherBounds
		"""
		if not isinstance(otherBounds,Bounds):
			otherBounds=Bounds(otherBounds)
		return otherBounds.encloses(self)

	def encloses(self,otherBounds):
		"""
		check to see if we totally enclose otherBounds
		"""
		if not isinstance(otherBounds,Bounds):
			otherBounds=Bounds(otherBounds)
		return otherBounds.x>=self.x and otherBounds.x2<=self.x2 and otherBounds.y>=self.y and otherBounds.y2<=self.y2

	def overlaps(self,otherBounds):
		"""
		check to see if any point of these bounds overlaps otherBounds
		"""
		if not isinstance(otherBounds,Bounds):
			otherBounds=Bounds(otherBounds)
		return otherBounds.pointTest(self.points)

	def move(self,deltaX,deltaY):
		self.x+=deltaX
		self.y+=deltaY

	def pivot(self):
		"""
		flip these bounds 90 degrees, by swapping x and y values
		"""
		self.y,self.x=(self.x,self.y)
		self.h,self.w=(self.w,self.h)

	@classmethod
	def findCenter(self,points):
		"""
		Utility to find the geographic center of a group of points tuples
		"""
		return Bounds(points).center

	@classmethod
	def rotatedPoints(self,points,angle,center=None):
		"""
		Utility to return a set of point tuples based on an existing set of point tuples, only rotated.

		If center=None, will findcenter(points) first
		"""
		if center==None:
			center=self.findCenter(points)
		ret=[]
		angle=math.radians(angle)
		sin_a,cos_a=abs(math.sin(angle)),abs(math.cos(angle))
		for point in points:
			ret.append(
					(
					(point[0]-center[0])*cos_a+(point[1]-center[1])*sin_a,
					(point[0]-center[0])*sin_a+(point[1]-center[1])*cos_a
					)
				)
		return ret

	def rotateFit(self,angle):
		"""
		calculate the new bounds to fit a roatated version of these bounds

		angle - in degrees

		NOTE: The algorithm is to rotate each corner point about a given center,
			then create new corner points based on min/max x and y location
		"""
		if self.w<=0 or self.h<=0 or angle%180==0: # nothing will change, so save some math
			return
		if angle%90==0: # this is a simple x/y value swap
			self.pivot()
		self.assign(Bounds.rotatedPoints(self.points,angle,self.center))