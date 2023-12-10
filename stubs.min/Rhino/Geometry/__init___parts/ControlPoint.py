class ControlPoint(object,IEpsilonComparable[ControlPoint]):
 """
 Represents control-point geometry with three-dimensional position and weight.

 

 ControlPoint(x: float,y: float,z: float)

 ControlPoint(x: float,y: float,z: float,weight: float)

 ControlPoint(pt: Point3d)

 ControlPoint(pt: Point3d,weight: float)

 ControlPoint(pt: Point4d)
 """
 def EpsilonEquals(self,other,epsilon):
  """
  EpsilonEquals(self: ControlPoint,other: ControlPoint,epsilon: float) -> bool

  

   Check that all values in other are within epsilon of the values in this
  """
  pass
 def __init__(self,*args):
  """ x.__init__(...) initializes x; see x.__class__.__doc__ for signaturex.__init__(...) initializes x; see x.__class__.__doc__ for signaturex.__init__(...) initializes x; see x.__class__.__doc__ for signature """
  pass
 @staticmethod
 def __new__(self,*__args):
  """
  __new__[ControlPoint]() -> ControlPoint

  

  __new__(cls: type,x: float,y: float,z: float)

  __new__(cls: type,x: float,y: float,z: float,weight: float)

  __new__(cls: type,pt: Point3d)

  __new__(cls: type,pt: Point3d,weight: float)

  __new__(cls: type,pt: Point4d)
  """
  pass
 def __reduce_ex__(self,*args):
  pass
 def __repr__(self,*args):
  """ __repr__(self: object) -> str """
  pass
 def __str__(self,*args):
  pass
 Location=property(lambda self: object(),lambda self,v: None,lambda self: None)
 """Gets or sets the location of the control point. 

   Internally,Rhino stores the location of a weighted control-point 

   as a pre-multiplied coordinate,but RhinoCommon always provides 

   Euclidean coordinates for control-points,regardless of weight.



Get: Location(self: ControlPoint) -> Point3d



Set: Location(self: ControlPoint)=value

"""

 Weight=property(lambda self: object(),lambda self,v: None,lambda self: None)
 """Gets or sets the weight of this control point.



Get: Weight(self: ControlPoint) -> float



Set: Weight(self: ControlPoint)=value

"""


 Unset=None

