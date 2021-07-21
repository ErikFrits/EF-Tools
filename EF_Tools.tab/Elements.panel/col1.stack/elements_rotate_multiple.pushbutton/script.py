# -*- coding: utf-8 -*-
__title__ = "Elements: Rotate"
__author__ = "Erik Frits"
__doc__ = """Version = 1.0
Date    = 31.08.2020
_____________________________________________________________________
Description:

Rotate selected elements with given ammount of degrees.
_____________________________________________________________________
How-to:

-> Select elements to rotate
-> Click the button
-> Give degrees
-> Rotate
_____________________________________________________________________
Last update:
- [18.07.2021] 1.0 RELEASE
- [18.07.2021] GUI created
_____________________________________________________________________
To-do:
- GUI for TitleBlock Selection
- Restrict textfield to integers only
_____________________________________________________________________
Rotate function is based on afunction taken from Jeremy Tammik's blog
_____________________________________________________________________
"""

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> IMPORTS
from Autodesk.Revit.DB import (Line, XYZ, ElementTransformUtils)
from pyrevit import forms, revit
import math

#>>>>>>>>>> CUSTOM
from Snippets.selection import get_selected_elements

#>>>>>>>>>> .NET IMPORTS
from clr import AddReference
AddReference("System")
from System.Diagnostics.Process import Start
from System.Windows.Window      import DragMove
from System.Windows.Input       import MouseButtonState

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VARIABLES
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> FUNCTIONS
def rotateSelectedElement(elem, degrees_to_rotate):
    """Function to rotate given element around its center axis.
    Function is based on an article found on Jeremy Tammik's blog - https://thebuildingcoder.typepad.com/blog/2018/12/rotate-picked-element-around-bounding-box-centre-in-python.html"""
    #>>>>>>>>>> RADIANS
    converted_value = float(degrees_to_rotate) * (math.pi / 180.0)
    #>>>>>>>>>> BOUNDING BOX
    el_bb        = elem.get_BoundingBox(doc.ActiveView)
    el_bb_center = (el_bb.Max + el_bb.Min) / 2
    #>>>>>>>>>> VECTOR FROM BB CENTER
    p1     = XYZ(el_bb_center[0], el_bb_center[1], 0)
    p2     = XYZ(el_bb_center[0], el_bb_center[1], 1)
    myLine = Line.CreateBound(p1, p2)
    #>>>>>>>>>> ROTATE
    ElementTransformUtils.RotateElement(doc, elem.Id, myLine, converted_value)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GUI
class MyWindow(forms.WPFWindow):
    """GUI"""
    def __init__(self, xaml_file_name):
        self.form = forms.WPFWindow.__init__(self, xaml_file_name)
        self.main_title.Text = __title__

        if self.selected_elements: self.ShowDialog()
    #>>>>>>>>>>>>>>>>>>>> PROPERTIES
    @property
    def selected_elements(self):
        return get_selected_elements()

    @property
    def degrees(self):
        try:    return int(self.input_degrees.Text)
        except: return 0

    #>>>>>>>>>>>>>>>>>>>> GUI EVENT HANDLERS:
    def button_close(self, sender, e):
        """Stop application by clicking on a <Close> button in the top right corner."""
        self.Close()

    def Hyperlink_RequestNavigate(self, sender, e):
        """Forwarding for a Hyperlink"""
        Start(e.Uri.AbsoluteUri)

    def header_drag(self,sender,e):
        """Drag window by holding LeftButton on the header."""
        if e.LeftButton == MouseButtonState.Pressed:
            DragMove(self)
    def button_run(self, sender, e):
        """Button action: Rename view with given """
        self.roate()
        self.Close()

    #>>>>>>>>>>>>>>>>>>>> MAIN
    def roate(self):
        # >>>>>>>>>> ROTATE ELEMENTS
        with revit.Transaction(__title__):
            for element in self.selected_elements:
                try:    rotateSelectedElement(element, self.degrees)
                except: print("Could not rotate element - {}".format(element.Id))

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> MAIN
if __name__ == '__main__':
    MyWindow("Script.xaml")



