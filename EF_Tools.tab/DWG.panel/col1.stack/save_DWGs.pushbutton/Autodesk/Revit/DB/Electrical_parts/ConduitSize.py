class ConduitSize(object,IDisposable):
 """
 Stores the basic size information for a conduit.

 

 ConduitSize(nominalDiameter: float,innerDiameter: float,outerDiameter: float,bendRadius: float,usedInSizeLists: bool,usedInSizing: bool)
 """
 def Dispose(self):
  """ Dispose(self: ConduitSize) """
  pass
 def ReleaseUnmanagedResources(self,*args):
  """ ReleaseUnmanagedResources(self: ConduitSize,disposing: bool) """
  pass
 def __enter__(self,*args):
  """ __enter__(self: IDisposable) -> object """
  pass
 def __exit__(self,*args):
  """ __exit__(self: IDisposable,exc_type: object,exc_value: object,exc_back: object) """
  pass
 def __init__(self,*args):
  """ x.__init__(...) initializes x; see x.__class__.__doc__ for signaturex.__init__(...) initializes x; see x.__class__.__doc__ for signaturex.__init__(...) initializes x; see x.__class__.__doc__ for signature """
  pass
 @staticmethod
 def __new__(self,nominalDiameter,innerDiameter,outerDiameter,bendRadius,usedInSizeLists,usedInSizing):
  """ __new__(cls: type,nominalDiameter: float,innerDiameter: float,outerDiameter: float,bendRadius: float,usedInSizeLists: bool,usedInSizing: bool) """
  pass
 def __repr__(self,*args):
  """ __repr__(self: object) -> str """
  pass
 BendRadius=property(lambda self: object(),lambda self,v: None,lambda self: None)
 """Minimum bend radius



Get: BendRadius(self: ConduitSize) -> float



"""

 InnerDiameter=property(lambda self: object(),lambda self,v: None,lambda self: None)
 """Inner diameter



Get: InnerDiameter(self: ConduitSize) -> float



"""

 IsValidObject=property(lambda self: object(),lambda self,v: None,lambda self: None)
 """Specifies whether the .NET object represents a valid Revit entity.



Get: IsValidObject(self: ConduitSize) -> bool



"""

 NominalDiameter=property(lambda self: object(),lambda self,v: None,lambda self: None)
 """Nominal diameter



Get: NominalDiameter(self: ConduitSize) -> float



"""

 OuterDiameter=property(lambda self: object(),lambda self,v: None,lambda self: None)
 """Outer diameter



Get: OuterDiameter(self: ConduitSize) -> float



"""

 UsedInSizeLists=property(lambda self: object(),lambda self,v: None,lambda self: None)
 """Whether it is used in size lists.



Get: UsedInSizeLists(self: ConduitSize) -> bool



"""

 UsedInSizing=property(lambda self: object(),lambda self,v: None,lambda self: None)
 """Whether is used in sizing.



Get: UsedInSizing(self: ConduitSize) -> bool



"""


