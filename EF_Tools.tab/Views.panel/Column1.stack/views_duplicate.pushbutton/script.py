# -*- coding: utf-8 -*-

__title__ = "Duplicate views"
__author__ = "Erik Frits"
__doc__ = """Version = 1.2
Date    = 31.08.2020
_____________________________________________________________________
Description:

Duplicate multiple views at once.
_____________________________________________________________________
How-To:

1. Select views in Project Browser before running the script.
Otherwise, dialog box will be shown to select views.

2. Choose Duplicate Options and how many copies of each you want.

_____________________________________________________________________
TODO:
[FEATURE] - Set selection to duplicated views once its done
_____________________________________________________________________
Last Updates:
- [22.11.2021] Selection is update to new Views
- [01.06.2021] Added rules for Scheudles
- [01.06.2021] Added rules for Legends 
_____________________________________________________________________
"""


# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ==================================================
from Autodesk.Revit.DB import (View,
                               ViewPlan,
                               ViewSection,
                               View3D,
                               ViewSchedule,
                               ViewDuplicateOption,
                               Transaction,
                               ViewType,
                               ElementId)
# pyRevit
from pyrevit.forms import WPFWindow, alert

# Custom imports
from Snippets._selection import get_selected_views


# .NET Imports
from clr import AddReference
AddReference("System")
from System.Collections.Generic import List
from System.Diagnostics.Process import Start
from System.Windows.Window      import DragMove
from System.Windows.Input       import MouseButtonState


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ==================================================
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document

# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝ CLASSES
# ==================================================
class MyWindow(WPFWindow):
    """The dialog box that controls the whole script."""

    VIEW_TYPES = [ViewPlan, ViewSection, View3D,ViewSchedule, View]

    def __init__(self, xaml_file_name):
        self.form = WPFWindow.__init__(self, xaml_file_name)
        self.main_title.Text = __title__
        self.selected_views = get_selected_views(uidoc, exit_if_none=True, title=__title__)

        if self.selected_views:
            self.ShowDialog()


    # METHODS
    def duplicate_selected_views(self, options):
        """Function to duplicate views with given options.
        Possible options:
        - ViewDuplicateOption.Duplicate,
        - ViewDuplicateOption.WithDetailing,
        - ViewDuplicateOption.AsDependent"""
        new_views = []
        t = Transaction(doc, __title__)
        t.Start()
        try:

            for view in self.selected_views:
                # if doc.CanViewBeDuplicated(view):

                # SCHEDULES
                if type(view) == ViewSchedule:
                    for i in range(self.count):
                        view.Duplicate(ViewDuplicateOption.Duplicate)

                # LEGENDS
                if view.ViewType == ViewType.Legend:
                    for i in range(self.count):
                        view.Duplicate(ViewDuplicateOption.WithDetailing)

                # REGULAR VIEWS
                else:
                    for i in range(self.count):
                        new_view = view.Duplicate(options)
                        new_views.append(new_view)
        except:
            pass

        if new_views:
            uidoc.Selection.SetElementIds(List[ElementId]([]))
            uidoc.Selection.SetElementIds(List[ElementId](new_views))
        t.Commit()


#____________________________________________________________________ PROPERTIES

    # GUI INPUTS
    @property
    def count(self):
        try:
            return int(self.duplicate_count.Text)
        except:
            alert("Value error: Duplicate_count input should only contain integers.\nPlease, try again.", exitscript=True, title=__title__)

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


    def button_duplicate(self,sender,e):
        """Duplicate selected views and close the GUI."""
        self.Close()
        self.duplicate_selected_views(ViewDuplicateOption.Duplicate)

    def button_duplicate_detailing(self,sender,e):
        """Duplicate selected views with detailing and close the GUI."""
        self.Close()
        self.duplicate_selected_views(ViewDuplicateOption.WithDetailing)

    def button_duplicate_dependant(self, sender, e):
        """Duplicate selected views as dependant and close the GUI."""
        self.Close()
        self.duplicate_selected_views(ViewDuplicateOption.AsDependent)

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
# ==================================================
if __name__ == '__main__':
    MyWindow("Script.xaml")
