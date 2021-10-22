# -*- coding: utf-8 -*-
__title__ = "Find and Replace in Views"
__author__ = "Erik Frits"
__helpurl__ = ""
__doc__ = """Version = 1.0
Date    = 10.11.2020
_____________________________________________________________________
Description:

Rename multiple views at once with Find/Replace/Suffix/Prefix logic.
_____________________________________________________________________
How-to:

- Select views in ProjectBrowser
- Run the script
- Type Find/Replace/Prefix/Suffix as needed.
_____________________________________________________________________
Last update:

- [10.05.2021] - 1.0 RELESE
- [10.05.2021] - ViewSchedule, ViewDrafting added.
- [10.05.2021] - GUI Updated
_____________________________________________________________________
"""

#____________________________________________________________________ IMPORTS

from pyrevit import forms
from Autodesk.Revit.DB import ( Transaction,
                                View,
                                ViewPlan,
                                ViewSection,
                                View3D,
                                ViewSchedule,
                                ViewDrafting)
from Autodesk.Revit.Exceptions import ArgumentException

# .NET IMPORTS
from clr import AddReference
AddReference("System")
from System.Diagnostics.Process import Start
from System.Windows.Window import DragMove
from System.Windows.Input import MouseButtonState

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
#____________________________________________________________________ FUNCTIONS
def view_rename(selected_views, FIND, REPLACE, PREFIX, SUFFIX ):
    #type:(list,str,str,str,str) -> None
    """ Function to rename given views based on given criterias."""
    t = Transaction(doc, __title__)
    t.Start()
    for view in selected_views:

        # GENERATE NEW NAME
        view_new_name = PREFIX + view.Name.replace(FIND, REPLACE) + SUFFIX

        # [FAILSAVE] ENSURE THAT VIEW NAME IS UNIQUE BY ADDING <*> IF NEEDED.
        fail_count =0
        while fail_count < 10:
            fail_count += 1
            try:
                if view.Name != view_new_name:
                    view.Name = view_new_name
                    break
            except ArgumentException:
                view_new_name +=  "*"
            except:
                view_new_name += "_"
    t.Commit()

#____________________________________________________________________ GUI

class MyWindow(forms.WPFWindow):
    """GUI for [Views: Find and Replace]"""
    def __init__(self, xaml_file_name):
        self.form = forms.WPFWindow.__init__(self, xaml_file_name)
        self.main_title.Text = __title__

    @property
    def find(self):
        return self.input_find.Text

    @property
    def replace(self):
        return self.input_replace.Text

    @property
    def prefix(self):
        return self.input_prefix.Text

    @property
    def suffix(self):
        return self.input_suffix.Text


    # GUI EVENT HANDLERS:
    def button_close(self,sender,e):
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
        view_rename(selected_views,self.find,self.replace, self.prefix, self.suffix)
        self.Close()

#____________________________________________________________________ MAIN

# GET SELECTED ELEMENTS
UI_selected = uidoc.Selection.GetElementIds()

# FILTER SELECTION
VIEW_TYPES = [  View,
                ViewPlan,
                ViewSection,
                View3D,
                ViewSchedule,
                ViewDrafting]
selected_views = [doc.GetElement(view_id) for view_id in UI_selected if type(doc.GetElement(view_id)) in VIEW_TYPES]

# RUN
if selected_views:
    MyWindow("Script.xaml").ShowDialog()
else:
    forms.alert("No views were selected.\nPlease, try again.", exitscript=True, title="Script Cancelled.")
