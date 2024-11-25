class AnalysisDisplayVectorSettings(object,IDisposable):
 """
 Contains vector settings for analysis display style element.

 

 AnalysisDisplayVectorSettings()

 AnalysisDisplayVectorSettings(other: AnalysisDisplayVectorSettings)
 """
 def Dispose(self):
  """ Dispose(self: AnalysisDisplayVectorSettings) """
  pass
 def IsEqual(self,other):
  """
  IsEqual(self: AnalysisDisplayVectorSettings,other: AnalysisDisplayVectorSettings) -> bool

  

   Compares two vector settings objects.

  

   other: Vector settings object to compare with.

   Returns: True if objects are equal,false otherwise.
  """
  pass
 def ReleaseUnmanagedResources(self,*args):
  """ ReleaseUnmanagedResources(self: AnalysisDisplayVectorSettings,disposing: bool) """
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
 def __new__(self,other=None):
  """
  __new__(cls: type)

  __new__(cls: type,other: AnalysisDisplayVectorSettings)
  """
  pass
 def __repr__(self,*args):
  """ __repr__(self: object) -> str """
  pass
 ArrowheadScale=property(lambda self: object(),lambda self,v: None,lambda self: None)
 """Type of arrow head scaling.



Get: ArrowheadScale(self: AnalysisDisplayVectorSettings) -> AnalysisDisplayStyleVectorArrowheadScale



Set: ArrowheadScale(self: AnalysisDisplayVectorSettings)=value

"""

 ArrowLineWeight=property(lambda self: object(),lambda self,v: None,lambda self: None)
 """Line weight assigned to arrow lines for vectors.



Get: ArrowLineWeight(self: AnalysisDisplayVectorSettings) -> int



Set: ArrowLineWeight(self: AnalysisDisplayVectorSettings)=value

"""

 IsValidObject=property(lambda self: object(),lambda self,v: None,lambda self: None)
 """Specifies whether the .NET object represents a valid Revit entity.



Get: IsValidObject(self: AnalysisDisplayVectorSettings) -> bool



"""

 Rounding=property(lambda self: object(),lambda self,v: None,lambda self: None)
 """Increment to which numeric values of analysis results are rounded in vectors.



Get: Rounding(self: AnalysisDisplayVectorSettings) -> float



Set: Rounding(self: AnalysisDisplayVectorSettings)=value

"""

 TextTypeId=property(lambda self: object(),lambda self,v: None,lambda self: None)
 """Element id of text associated with the settings.



Get: TextTypeId(self: AnalysisDisplayVectorSettings) -> ElementId



Set: TextTypeId(self: AnalysisDisplayVectorSettings)=value

"""

 VectorOrientation=property(lambda self: object(),lambda self,v: None,lambda self: None)
 """Vector orientation.



Get: VectorOrientation(self: AnalysisDisplayVectorSettings) -> AnalysisDisplayStyleVectorOrientation



Set: VectorOrientation(self: AnalysisDisplayVectorSettings)=value

"""

 VectorPosition=property(lambda self: object(),lambda self,v: None,lambda self: None)
 """Vector position.



Get: VectorPosition(self: AnalysisDisplayVectorSettings) -> AnalysisDisplayStyleVectorPosition



Set: VectorPosition(self: AnalysisDisplayVectorSettings)=value

"""

 VectorTextType=property(lambda self: object(),lambda self,v: None,lambda self: None)
 """Type of vector text visualization.



Get: VectorTextType(self: AnalysisDisplayVectorSettings) -> AnalysisDisplayStyleVectorTextType



Set: VectorTextType(self: AnalysisDisplayVectorSettings)=value

"""


