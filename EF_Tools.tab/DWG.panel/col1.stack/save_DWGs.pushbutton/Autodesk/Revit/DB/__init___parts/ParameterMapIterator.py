class ParameterMapIterator(APIObject,IDisposable,IEnumerator):
 """
 An iterator to a map relating a parameter name (the key,a String) to a parameter.

 

 ParameterMapIterator()
 """
 def Dispose(self):
  """ Dispose(self: ParameterMapIterator,A_0: bool) """
  pass
 def MoveNext(self):
  """
  MoveNext(self: ParameterMapIterator) -> bool

  

   Move the iterator one item forward.

   Returns: Returns True if the iterator was successfully moved forward one item and the 

    Current

     property will return a valid item. False will be returned 

    it the iterator has reached the end of

     the map.
  """
  pass
 def next(self,*args):
  """ next(self: object) -> object """
  pass
 def ReleaseManagedResources(self,*args):
  """ ReleaseManagedResources(self: APIObject) """
  pass
 def ReleaseUnmanagedResources(self,*args):
  """ ReleaseUnmanagedResources(self: ParameterMapIterator) """
  pass
 def Reset(self):
  """
  Reset(self: ParameterMapIterator)

   Bring the iterator back to the start of the map.
  """
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
 def __iter__(self,*args):
  """ __iter__(self: IEnumerator) -> object """
  pass
 Current=property(lambda self: object(),lambda self,v: None,lambda self: None)
 """Retrieves the item that is the current focus of the iterator.



Get: Current(self: ParameterMapIterator) -> object



"""

 Key=property(lambda self: object(),lambda self,v: None,lambda self: None)
 """Retrieves the key that is the current focus of the iterator.



Get: Key(self: ParameterMapIterator) -> str



"""

