# -*- coding: utf-8 -*-

__title__ = "Find and Replace in Sheets"  # Name of the button displayed in Revit
__author__ = "Erik Frits"
__doc__ = """Version = 1.0
Date    = 28.07.2020
_____________________________________________________________________
Description:

Rename selected sheet with Find/Replace/Prefix/Suffix options.
_____________________________________________________________________
How-to:

-> Select sheets in ProjectBrowser
-> Click the button
-> Set your criterias
-> Rename
_____________________________________________________________________
Prerequisite:

You have to select sheets in ProjectBrowser.
_____________________________________________________________________
Last update:
- 
_____________________________________________________________________
To-do:
- 
_____________________________________________________________________
"""





import sys
sys.path.append("C:\Users\ef\AppData\Roaming\pyRevit-Master\pyrevitlib")
import os.path as op
from pyrevit import revit
from pyrevit import forms
from pyrevit.forms import WPFWindow
from pyrevit import script
import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB import *

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document


from Autodesk.Revit.Exceptions import ArgumentException


# .NET IMPORTS
from clr import AddReference
AddReference("System")
from System.Diagnostics.Process import Start
from System.Windows.Window import DragMove
from System.Windows.Input import MouseButtonState



def update_project_browser():
    """Function to close and reopen ProjectBrowser so changes to Sheetnumber would become visible."""
    from Autodesk.Revit.UI import DockablePanes, DockablePane
    project_browser_id = DockablePanes.BuiltInDockablePanes.ProjectBrowser
    project_browser = DockablePane(project_browser_id)
    project_browser.Hide()
    project_browser.Show()


###__________________________________________________________________________________________________APPLICATION______________###

class MyWindow(forms.WPFWindow):
    """GUI for ViewSheet renaming tool."""
    def __init__(self, xaml_file_name):
        self.form = forms.WPFWindow.__init__(self, xaml_file_name)
        self.main_title.Text = __title__





    def rename(self):
        t = Transaction(doc, "py:Viewname find and replace")
        t.Start()
        self.rename_sheet_name()
        self.rename_sheet_number()
        update_project_browser()
        t.Commit()


    def rename_sheet_name(self):
        """Function to rename SheetName if it is different to current one."""

        for sheet in self.selected_sheets:
            sheet_name_new = self.sheet_name_prefix + sheet.Name.replace(self.sheet_name_find, self.sheet_name_replace) + self.sheet_name_suffix
            fail_count = 0

            while fail_count < 5:
                fail_count += 1

                try:
                    if sheet.Name != sheet_name_new:
                        sheet.Name = sheet_name_new
                        break
                except ArgumentException:
                    sheet_name_new += "*"
                except:
                    sheet_name_new += "_"



    def rename_sheet_number(self):

        for sheet in self.selected_sheets:
            sheet_number_new = self.sheet_number_prefix + sheet.SheetNumber.replace(self.sheet_number_find, self.sheet_number_replace) + self.sheet_number_suffix

            fail_count = 0
            while fail_count < 5:
                fail_count += 1

                try:
                    if sheet.SheetNumber != sheet_number_new:
                        sheet.SheetNumber = sheet_number_new
                        break
                except ArgumentException:
                    sheet_number_new += "*"

                except:
                    sheet_number_new += "_"







    # sheet.ViewName = sheet.ViewName

    @property
    def selected_sheets(self):
        """Property that retrieves selected views or promt user to select some from the dialog box."""

        # FILTER SHEETS FROM SELECTION
        selected_sheets = [doc.GetElement(element_id) for element_id in uidoc.Selection.GetElementIds() if type(doc.GetElement(element_id)) == ViewSheet]

        # SELECT SHEETS IF NONE SELECTED IN UI
        if not selected_sheets :
            selected_sheets  = forms.select_sheets(title="Select sheets to rename.",
                                                button_name="Rename selected sheets",
                                                width=1000)  # FIXME replace with custom view selection box later...
            if not selected_sheets:
                forms.alert("No views were selected.\nPlease, try again.", exitscript=True, title=__title__)
        return selected_sheets


    ### GUI PROPERTIES

    # SHEETNUMBER PROPERTIES
    @property
    def sheet_number_find(self):
        return self.input_sheet_number_find.Text

    @property
    def sheet_number_replace(self):
        return self.input_sheet_number_replace.Text

    @property
    def sheet_number_prefix(self):
        return self.input_sheet_number_prefix.Text

    @property
    def sheet_number_suffix(self):
        return self.input_sheet_number_suffix.Text




    # SHEETNAME PROPERTIES
    @property
    def sheet_name_find(self):
        return self.input_sheet_name_find.Text

    @property
    def sheet_name_replace(self):
        return self.input_sheet_name_replace.Text

    @property
    def sheet_name_prefix(self):
        return self.input_sheet_name_prefix.Text

    @property
    def sheet_name_suffix(self):
        return self.input_sheet_name_suffix.Text






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

        self.Close()
        self.rename()

if __name__ == '__main__':
    MyWindow("Script.xaml").ShowDialog()
