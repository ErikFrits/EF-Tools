# -*- coding: utf-8 -*-
__title__ = "Text: Transform"   # Name of the button displayed in Revit
__author__ = "Erik Frits"
__doc__ = """Version = 1.0
Date    = 14.07.2021
_____________________________________________________________________
Description:

This tool has multiple controls over selected TextNote elements:
_____________________________________________________________________
How-to:

Select a few TextBlock and run the script to transform text.
_____________________________________________________________________
Last update:

- [14.07.2021] - 1.0 RELEASE
- [14.07.2021] - GUI
- [14.07.2021] - Find Replace added
- [14.07.2021] - Text transformers added. (upper,lower,title...)
_____________________________________________________________________
"""

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> IMPORTS
import os
from pyrevit import forms
from Autodesk.Revit.DB import  Transaction, TextNote

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> .NET IMPORTS
from clr import AddReference
AddReference("System")
from System.Windows             import Application, Window
from System.Diagnostics.Process import Start
from System.Windows.Window      import DragMove
from System.Windows.Input       import MouseButtonState
import wpf
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> CUSTOM IMPORTS
from Snippets._selection import get_selected_elements

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VARIABLES
doc     = __revit__.ActiveUIDocument.Document
uidoc   = __revit__.ActiveUIDocument
app     = __revit__.Application

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> MAIN
class MyWindow(Window):
    def __init__(self):
        wpf.LoadComponent(self, os.path.dirname(__file__) + '/Script.xaml')
        self.selected_text_notes = self.get_selected_text_notes()
        if self.selected_text_notes:
            self.main_title.Text = __title__
            self.ShowDialog()

        # self.form = WPFWindow.__init__(self, xaml_file_name)


    def get_selected_text_notes(self):
        selected_elements = get_selected_elements(uidoc)
        selected_text_notes = [element for element in selected_elements if type(element) == TextNote]

        if not selected_text_notes:
            forms.alert('No TextNotes were selected. Please try again.', exitscript=True)
        return selected_text_notes

    def button_upper(self, sender, e):
        t = Transaction(doc, __title__)
        t.Start()
        for TN in self.selected_text_notes:
            TN.Text = str(TN.Text).upper()
        t.Commit()

    def button_lower(self, sender, e):
        t = Transaction(doc, __title__)
        t.Start()
        for TN in self.selected_text_notes:
            TN.Text = str(TN.Text).lower()
        t.Commit()

    def button_title(self, sender, e):
        t = Transaction(doc, __title__)
        t.Start()

        for TN in self.selected_text_notes:
            TN.Text = str(TN.Text).title()
        t.Commit()

    def button_capitalize(self, sender, e):
        t = Transaction(doc, __title__)
        t.Start()
        for TN in self.selected_text_notes:
            TN.Text = str(TN.Text).capitalize()
        t.Commit()

    def button_swapcase(self, sender, e):
        t = Transaction(doc, __title__)
        t.Start()
        for TN in self.selected_text_notes:
            TN.Text = str(TN.Text).swapcase()
        t.Commit()

    def button_reverse(self, sender, e):
        t = Transaction(doc, __title__)
        t.Start()
        for TN in self.selected_text_notes:
            TN.Text = str(TN.Text)[::-1]
        t.Commit()

    def button_strip(self, sender, e):
        t = Transaction(doc, __title__)
        t.Start()
        for TN in self.selected_text_notes:
            TN.Text = str(TN.Text).strip()
        t.Commit()

    def button_find_replace(self, sender, e):
        t = Transaction(doc, __title__)
        t.Start()
        for TN in self.selected_text_notes:
            TN.Text = self.prefix + str(TN.Text).replace(self.find, self.replace) + self.suffix
        t.Commit()


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

    def header_drag(self,sender,e):
        """Drag window by holding LeftButton on the header."""
        if e.LeftButton == MouseButtonState.Pressed:
            DragMove(self)

    def button_open_dwg(self,sender,e):
        """Open DWG in a default application and close the GUI."""
        print('button_open_dwg()')

    def button_open_folder(self,sender,e):
        """Open parent folder of DWG file and close the GUI."""
        print('button_open_folder()')

    def button_copy_clipboard(self, sender, e):
        """Add DWG filepath to the copy clipboard."""
        print('button_copy_clipboard()')

    def Hyperlink_RequestNavigate(self, sender, e):
        """Forwarding for a Hyperlink"""
        Start(e.Uri.AbsoluteUri)

if __name__ == '__main__':

    MyWindow()








