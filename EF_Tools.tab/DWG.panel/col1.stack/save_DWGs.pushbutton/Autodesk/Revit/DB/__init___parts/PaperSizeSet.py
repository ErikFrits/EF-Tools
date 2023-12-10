class PaperSizeSet(APIObject,IDisposable,IEnumerable):
 """
 A set that can contain any number of paper size objects.

 

 PaperSizeSet()
 """
 def Clear(self):
  """
  Clear(self: PaperSizeSet)

   Removes every item from the set,rendering it empty.
  """
  pass
 def Contains(self,item):
  """
  Contains(self: PaperSizeSet,item: PaperSize) -> bool

  

   Tests for the existence of an item within the set.

  

   item: The item to be searched for.

   Returns: The Contains method returns True if the item is within the set,otherwise False.
  """
  pass
 def Dispose(self):
  """ Dispose(self: PaperSizeSet,A_0: bool) """
  pass
 def Erase(self,item):
  """
  Erase(self: PaperSizeSet,item: PaperSize) -> int

  

   Removes a specified object from the set.

  

   item: The item to be erased.

   Returns: The number of items that were erased from the set.
  """
  pass
 def ForwardIterator(self):
  """
  ForwardIterator(self: PaperSizeSet) -> PaperSizeSetIterator

  

   Retrieve a forward moving iterator to the set.

   Returns: Returns a forward moving iterator to the set.
  """
  pass
 def GetEnumerator(self):
  """
  GetEnumerator(self: PaperSizeSet) -> IEnumerator

  

   Retrieve a forward moving iterator to the set.

   Returns: Returns a forward moving iterator to the set.
  """
  pass
 def Insert(self,item):
  """
  Insert(self: PaperSizeSet,item: PaperSize) -> bool

  

   Insert the specified item into the set.

  

   item: The item to be inserted into the set.

   Returns: Returns whether the item was inserted into the set.
  """
  pass
 def ReleaseManagedResources(self,*args):
  """ ReleaseManagedResources(self: APIObject) """
  pass
 def ReleaseUnmanagedResources(self,*args):
  """ ReleaseUnmanagedResources(self: PaperSizeSet) """
  pass
 def ReverseIterator(self):
  """
  ReverseIterator(self: PaperSizeSet) -> PaperSizeSetIterator

  

   Retrieve a backward moving iterator to the set.

   Returns: Returns a backward moving iterator to the set.
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
  """ __iter__(self: IEnumerable) -> object """
  pass
 IsEmpty=property(lambda self: object(),lambda self,v: None,lambda self: None)
 """Test to see if the set is empty.



Get: IsEmpty(self: PaperSizeSet) -> bool



"""

 Size=property(lambda self: object(),lambda self,v: None,lambda self: None)
 """Returns the number of objects that are in the set.



Get: Size(self: PaperSizeSet) -> int



"""


