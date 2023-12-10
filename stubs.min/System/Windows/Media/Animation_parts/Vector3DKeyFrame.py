class Vector3DKeyFrame(Freezable,ISealable,IKeyFrame):
 """ Abstract class that,when implemented,defines an animation segment with its own target value and interpolation method for a System.Windows.Media.Animation.Vector3DAnimationUsingKeyFrames. """
 def CloneCore(self,*args):
  """
  CloneCore(self: Freezable,sourceFreezable: Freezable)

   Makes the instance a clone (deep copy) of the specified System.Windows.Freezable using base 

    (non-animated) property values.

  

  

   sourceFreezable: The object to clone.
  """
  pass
 def CloneCurrentValueCore(self,*args):
  """
  CloneCurrentValueCore(self: Freezable,sourceFreezable: Freezable)

   Makes the instance a modifiable clone (deep copy) of the specified System.Windows.Freezable 

    using current property values.

  

  

   sourceFreezable: The System.Windows.Freezable to be cloned.
  """
  pass
 def CreateInstance(self,*args):
  """
  CreateInstance(self: Freezable) -> Freezable

  

   Initializes a new instance of the System.Windows.Freezable class.

   Returns: The new instance.
  """
  pass
 def CreateInstanceCore(self,*args):
  """
  CreateInstanceCore(self: Freezable) -> Freezable

  

   When implemented in a derived class,creates a new instance of the System.Windows.Freezable 

    derived class.

  

   Returns: The new instance.
  """
  pass
 def FreezeCore(self,*args):
  """
  FreezeCore(self: Freezable,isChecking: bool) -> bool

  

   Makes the System.Windows.Freezable object unmodifiable or tests whether it can be made 

    unmodifiable.

  

  

   isChecking: true to return an indication of whether the object can be frozen (without actually freezing it); 

    false to actually freeze the object.

  

   Returns: If isChecking is true,this method returns true if the System.Windows.Freezable can be made 

    unmodifiable,or false if it cannot be made unmodifiable. If isChecking is false,this method 

    returns true if the if the specified System.Windows.Freezable is now unmodifiable,or false if 

    it cannot be made unmodifiable.
  """
  pass
 def GetAsFrozenCore(self,*args):
  """
  GetAsFrozenCore(self: Freezable,sourceFreezable: Freezable)

   Makes the instance a frozen clone of the specified System.Windows.Freezable using base 

    (non-animated) property values.

  

  

   sourceFreezable: The instance to copy.
  """
  pass
 def GetCurrentValueAsFrozenCore(self,*args):
  """
  GetCurrentValueAsFrozenCore(self: Freezable,sourceFreezable: Freezable)

   Makes the current instance a frozen clone of the specified System.Windows.Freezable. If the 

    object has animated dependency properties,their current animated values are copied.

  

  

   sourceFreezable: The System.Windows.Freezable to copy and freeze.
  """
  pass
 def InterpolateValue(self,baseValue,keyFrameProgress):
  """
  InterpolateValue(self: Vector3DKeyFrame,baseValue: Vector3D,keyFrameProgress: float) -> Vector3D

  

   Returns the interpolated value of a specific key frame at the progress increment provided.

  

   baseValue: The value to animate from.

   keyFrameProgress: A value between 0.0 and 1.0,inclusive,that specifies the percentage of time that has elapsed 

    for this key frame.

  

   Returns: The output value of this key frame given the specified base value and progress.
  """
  pass
 def InterpolateValueCore(self,*args):
  """
  InterpolateValueCore(self: Vector3DKeyFrame,baseValue: Vector3D,keyFrameProgress: float) -> Vector3D

  

   Calculates the value of a key frame at the progress increment provided.

  

   baseValue: The value to animate from; typically the value of the previous key frame.

   keyFrameProgress: A value between 0.0 and 1.0,inclusive,that specifies the percentage of time that has elapsed 

    for this key frame.

  

   Returns: The output value of this key frame given the specified base value and progress.
  """
  pass
 def OnChanged(self,*args):
  """
  OnChanged(self: Freezable)

   Called when the current System.Windows.Freezable object is modified.
  """
  pass
 def OnFreezablePropertyChanged(self,*args):
  """
  OnFreezablePropertyChanged(self: Freezable,oldValue: DependencyObject,newValue: DependencyObject,property: DependencyProperty)

   This member supports the Windows Presentation Foundation (WPF) infrastructure and is not 

    intended to be used directly from your code.

  

  

   oldValue: The previous value of the data member.

   newValue: The current value of the data member.

   property: The property that changed.

  OnFreezablePropertyChanged(self: Freezable,oldValue: DependencyObject,newValue: DependencyObject)

   Ensures that appropriate context pointers are established for a 

    System.Windows.DependencyObjectType data member that has just been set.

  

  

   oldValue: The previous value of the data member.

   newValue: The current value of the data member.
  """
  pass
 def OnPropertyChanged(self,*args):
  """
  OnPropertyChanged(self: Freezable,e: DependencyPropertyChangedEventArgs)

   Overrides the System.Windows.DependencyObject implementation of 

    System.Windows.DependencyObject.OnPropertyChanged(System.Windows.DependencyPropertyChangedEventAr

    gs) to also invoke any System.Windows.Freezable.Changed handlers in response to a changing 

    dependency property of type System.Windows.Freezable.

  

  

   e: Event data that contains information about which property changed,and its old and new values.
  """
  pass
 def ReadPreamble(self,*args):
  """
  ReadPreamble(self: Freezable)

   Ensures that the System.Windows.Freezable is being accessed from a valid thread. Inheritors of 

    System.Windows.Freezable must call this method at the beginning of any API that reads data 

    members that are not dependency properties.
  """
  pass
 def ShouldSerializeProperty(self,*args):
  """
  ShouldSerializeProperty(self: DependencyObject,dp: DependencyProperty) -> bool

  

   Returns a value that indicates whether serialization processes should serialize the value for 

    the provided dependency property.

  

  

   dp: The identifier for the dependency property that should be serialized.

   Returns: true if the dependency property that is supplied should be value-serialized; otherwise,false.
  """
  pass
 def WritePostscript(self,*args):
  """
  WritePostscript(self: Freezable)

   Raises the System.Windows.Freezable.Changed event for the System.Windows.Freezable and invokes 

    its System.Windows.Freezable.OnChanged method. Classes that derive from System.Windows.Freezable 

    should call this method at the end of any API that modifies class members that are not stored as 

    dependency properties.
  """
  pass
 def WritePreamble(self,*args):
  """
  WritePreamble(self: Freezable)

   Verifies that the System.Windows.Freezable is not frozen and that it is being accessed from a 

    valid threading context. System.Windows.Freezable inheritors should call this method at the 

    beginning of any API that writes to data members that are not dependency properties.
  """
  pass
 def __init__(self,*args):
  """ x.__init__(...) initializes x; see x.__class__.__doc__ for signaturex.__init__(...) initializes x; see x.__class__.__doc__ for signaturex.__init__(...) initializes x; see x.__class__.__doc__ for signature """
  pass
 @staticmethod
 def __new__(self,*args): #cannot find CLR constructor
  """
  __new__(cls: type)

  __new__(cls: type,value: Vector3D)

  __new__(cls: type,value: Vector3D,keyTime: KeyTime)
  """
  pass
 KeyTime=property(lambda self: object(),lambda self,v: None,lambda self: None)
 """Gets or sets the time at which the key frame's target System.Windows.Media.Animation.Vector3DKeyFrame.Value should be reached.



Get: KeyTime(self: Vector3DKeyFrame) -> KeyTime



Set: KeyTime(self: Vector3DKeyFrame)=value

"""

 Value=property(lambda self: object(),lambda self,v: None,lambda self: None)
 """Gets or sets the key frame's target value.



Get: Value(self: Vector3DKeyFrame) -> Vector3D



Set: Value(self: Vector3DKeyFrame)=value

"""


 KeyTimeProperty=None
 ValueProperty=None

