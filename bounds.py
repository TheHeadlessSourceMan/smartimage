class Bounds(object):
	def __init__(self,vals):
		self.clear()
		self.assign(**vals)
		
	def clear(self):
		self.x=None
		self.y=None
		self.w=None
		self.h=None
		
	def assign(self,vals):
		self.clear()
		self.maximize(cornerPoints)
		
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
			if type(morebounds[0]) in (int,float,double):
				for i in range(len(morebounds)): # array of x,y points
					if i%2==0:
						if morebounds[i]<self.x:
							self.x=morebounds[i]
						if morebounds[i]>self.x2:
							self.x2=morebounds[i]
					else:
						if morebounds[i]<self.y:
							self.y=morebounds[i]
						if morebounds[i]>self.y2:
							self.y2=morebounds[i]
			else:
				for b in morebounds:
					self.maximize(morebounds)
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
		return self.x+self.w
	@property
	def y2(self):
		return self.y+self.h
	@x2.setter
	def x2(self,x2):
		self.w=x2-self.x
	@y2.setter
	def y2(self,y2):
		self.h=y2-self.y
		
	@property
	def cornerPoints(self):
		x=self.x
		y=self.y
		x2=self.x2
		y2=self.y2
		return ((x,y),(x2,y),(x2,y2),(x,y2))
	@cornerPoints.setter
	def cornerPoints(self,cornerPoints):
		self.assign(cornerPoints)
		
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
	def center(self):
		return (self.x+self.w/2,self.y+self.h/2)
	@center.setter
	def center(self,center):
		self.x=center[0]+self.w/2
		self.y=center[0]+self.y/2
		
	def pointTest(self,point):
		"""
		check to see if any point is within these bounds
		
		point can be a single point or a list of points
		"""
		if type(point)==list:
			for p in point:
				if self.pointTest(p):
					return True
			return False
		return point[0]>=x and point[0]<=x2 and point[1]>=y and point[1]<=y2
		
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
		return otherBounds.pointTest(self.cornerPoints)
		
	def move(self,deltaX,deltaY):
		self.x+=deltaX
		self.y+=deltaY
		
	def pivot(self):
		"""
		flip these bounds 90 degrees, by swapping x and y values
		"""
		self.y,self.x=(self.x,self.y)
		self.h,self.w=(self.w,self.h)
		
	@staticmethod
	def findCenter(self,points):
		"""
		Utility to find the geographic center of a group of points tuples
		"""
		return Bounds(points).center
		
	@staticmethod
	def rotatedPoints(self,points,center=None):
		"""
		Utility to return a set of point tuples based on an existing set of point tuples, only rotated.
		
		If center=None, will findcenter(points) first
		"""
		if center==None:
			center=Bounds.findCenter(points)
		ret=[]
		angle=math.radians(angle)
		sin_a,cos_a=abs(math.sin(angle)),abs(math.cos(angle))
		for point in points:
			ret.append(
				(point[0]-center[0])*cos_a+(point[1]-center[1])*sin_a,
				(point[0]-center[0])*sin_a+(point[1]-center[1])*cos_a)
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
		self.assign(Bounds.rotate(self.cornerPoints,self.center))