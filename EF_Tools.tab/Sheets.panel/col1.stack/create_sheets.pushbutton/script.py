# -*- coding: utf-8 -*-
__title__ = "Create Sheets"
__author__ = "Erik Frits"
__doc__ = """Version = 1.0
Date    = 31.08.2020
_____________________________________________________________________
Description:

Rename selected sheet with Find/Replace/Prefix/Suffix options.
_____________________________________________________________________
How-to:

-> Click the button
-> Select TitleBlock
-> Set parameters
-> Create Sheets
_____________________________________________________________________
Last update:
- [11.07.2021] GUI created
- [11.07.2021] Refactored
_____________________________________________________________________
To-do:
- GUI for TitleBlock Selection
- Restrict textfield to integers only
_____________________________________________________________________
"""



#______________________________ IMPORTS
import sys
from Autodesk.Revit.DB import (FilteredElementCollector,
                               BuiltInParameter,
                               BuiltInCategory,
                               ViewSheet,
                               Transaction)
from pyrevit.forms import SelectFromList
from pyrevit import forms

# .NET IMPORTS
import clr
from clr import AddReference
AddReference("System")
from System.Diagnostics.Process import Start
from System.Windows.Window import DragMove
from System.Windows.Input import MouseButtonState

# VARIABLES
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application



# FUNCTIONS
from Snippets._selection import select_title_block

def create_sheets(n_copies, prefix, start_count):
    """Function to create sheets"""
    for n in range(n_copies):
        Sheet = ViewSheet.Create(doc, selected_title_block)
        count = "{:02d}".format(start_count)
        sheet_number = prefix + count

        fail_count = 0
        while True:
            fail_count+=1
            if fail_count >10:
                break
            try:
                Sheet.SheetNumber = sheet_number
                break
            except:
                sheet_number+= "*"

        start_count += 1


class MyWindow(forms.WPFWindow):
    """GUI"""
    def __init__(self, xaml_file_name):
        self.form = forms.WPFWindow.__init__(self, xaml_file_name)
        self.main_title.Text = __title__

    @property
    def n_copies(self):
        try:
            return int(self.input_n_copies.Text)
        except:
            print("n_copies have to an integer value!")
    @property
    def prefix(self):
        return self.input_prefix.Text

    @property
    def start_count(self):
        return int(self.input_start_count.Text)



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
        create_sheets(self.n_copies, self.prefix, self.start_count)
        self.Close()


if __name__ == '__main__':
    selected_title_block = select_title_block(uidoc, exitscript=True)
    t = Transaction(doc, __title__)
    t.Start()
    if selected_title_block:
        MyWindow("Script.xaml").ShowDialog()
    t.Commit()






