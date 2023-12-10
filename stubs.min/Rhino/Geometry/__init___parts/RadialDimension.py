class RadialDimension(AnnotationBase,IDisposable,ISerializable):
 """
 Represents a dimension of a circular entity that can be measured with radius or diameter.

    This entity refers to the geometric element that is independent from the document.

 

 RadialDimension(center: Point3d,arrowTip: Point3d,xAxis: Vector3d,normal: Vector3d,offsetDistance: float)

 RadialDimension(circle: Circle,arrowTip: Point3d,offsetDistance: float)
 """
 def ConstructConstObject(self,*args):
  """
  ConstructConstObject(self: CommonObject,parentObject: object,subobject_index: int)

   Assigns a parent object and a subobject index to this.

  

   parentObject: The parent object.

   subobject_index: The subobject index.
  """
  pass
 def Dispose(self):
  """
  Dispose(self: CommonObject,disposing: bool)

   For derived class implementers.

     This method is called with argument true when class 

    user calls Dispose(),while with argument false when

     the Garbage Collector invokes 

    the finalizer,or Finalize() method.You must reclaim all used unmanaged resources in both cases,

    and can use this chance to call Dispose on disposable fields if the argument is true.Also,you 

    must call the base virtual method within your overriding method.

  

  

   disposing: true if the call comes from the Dispose() method; false if it comes from the Garbage Collector 

    finalizer.
  """
  pass
 def NonConstOperation(self,*args):
  """
  NonConstOperation(self: CommonObject)

   For derived classes implementers.

     Defines the necessary implementation to free the 

    instance from being const.
  """
  pass
 def OnSwitchToNonConst(self,*args):
  """
  OnSwitchToNonConst(self: GeometryBase)

   Is called when a non-const operation occurs.
  """
  pass
 def __enter__(self,*args):
  """
  __enter__(self: IDisposable) -> object

  

   Provides the implementation of __enter__ for objects which implement IDisposable.
  """
  pass
 def __exit__(self,*args):
  """
  __exit__(self: IDisposable,exc_type: object,exc_value: object,exc_back: object)

   Provides the implementation of __exit__ for objects which implement IDisposable.
  """
  pass
 def __init__(self,*args):
  """ x.__init__(...) initializes x; see x.__class__.__doc__ for signaturex.__init__(...) initializes x; see x.__class__.__doc__ for signaturex.__init__(...) initializes x; see x.__class__.__doc__ for signature """
  pass
 @staticmethod
 def __new__(self,*__args):
  """
  __new__(cls: type,info: SerializationInfo,context: StreamingContext)

  __new__(cls: type,center: Point3d,arrowTip: Point3d,xAxis: Vector3d,normal: Vector3d,offsetDistance: float)

  __new__(cls: type,circle: Circle,arrowTip: Point3d,offsetDistance: float)
  """
  pass
 def __reduce_ex__(self,*args):
  pass
 IsDiameterDimension=property(lambda self: object(),lambda self,v: None,lambda self: None)
 """Gets a value indicating whether the value refers to the diameter,rather than the radius.



Get: IsDiameterDimension(self: RadialDimension) -> bool



"""


