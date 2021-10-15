# -*- coding: utf-8 -*-

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#====================================================================================================
from abc import ABCMeta, abstractmethod, abstractproperty
from pyrevit import forms

# .NET IMPORTS
from clr import AddReference
AddReference("System")
from System.Diagnostics.Process import Start
from System.Windows.Window import DragMove
from System.Windows.Input import MouseButtonState

import os

# ╔╗ ╔═╗╔═╗╔═╗  ╔═╗╦  ╔═╗╔═╗╔═╗
# ╠╩╗╠═╣╚═╗║╣   ║  ║  ╠═╣╚═╗╚═╗
# ╚═╝╩ ╩╚═╝╚═╝  ╚═╝╩═╝╩ ╩╚═╝╚═╝ BASE CLASS
#====================================================================================================

class BaseRenaming(forms.WPFWindow):
    """GUI for [Views: Find and Replace]"""
    def start(self, title):
        xaml_dir_abs_path = os.path.abspath(os.path.dirname(__file__))
        xaml_file_name = os.path.join(xaml_dir_abs_path,"GUI_BaseRename.xaml")

        self.form = forms.WPFWindow.__init__(self, xaml_file_name)
        self.main_title.Text = title
        self.selected_elements = self.get_selected_elements()

        if self.selected_elements:
            self.ShowDialog()
        else:
            forms.alert("No matching elements for renaming were selected. \nPlease Try again.", exitscript=True, title="Script Cancelled.")

    # ╔═╗╔╗ ╔═╗╔╦╗╦═╗╔═╗╔═╗╔╦╗
    # ╠═╣╠╩╗╚═╗ ║ ╠╦╝╠═╣║   ║
    # ╩ ╩╚═╝╚═╝ ╩ ╩╚═╩ ╩╚═╝ ╩ ABSTRACT PART
    # ====================================================================================================

    @abstractproperty
    def uidoc(self):
        """docs is passed this way so it will be updated in case user uses the end tool in multiple open projects."""
        pass

    @abstractproperty
    def doc(self):
        """docs is passed this way so it will be updated in case user uses the end tool in multiple open projects."""
        pass

    @abstractproperty
    def element_types(self):
        """Abstract property of a list of types that should be filtered from selection."""
        pass

    @abstractmethod
    def rename_elements(self):
        """This is an abstract method that will be replaced with a function that contains renaming logic for given elements."""
        pass

    def get_selected_elements(self):
        return [self.doc.GetElement(elem_id) for elem_id in self.uidoc.Selection.GetElementIds() if type(self.doc.GetElement(elem_id)) in self.element_types]

    # ╔═╗╦ ╦╦  ╔═╗╦═╗╔═╗╔═╗╔═╗╦═╗╔╦╗╦╔═╗╔═╗
    # ║ ╦║ ║║  ╠═╝╠╦╝║ ║╠═╝║╣ ╠╦╝ ║ ║║╣ ╚═╗
    # ╚═╝╚═╝╩  ╩  ╩╚═╚═╝╩  ╚═╝╩╚═ ╩ ╩╚═╝╚═╝ GUI PROPERTIES
    # ====================================================================================================

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

    # ╔═╗╦ ╦╦  ╔═╗╦  ╦╔═╗╔╗╔╔╦╗╔═╗
    # ║ ╦║ ║║  ║╣ ╚╗╔╝║╣ ║║║ ║ ╚═╗
    # ╚═╝╚═╝╩  ╚═╝ ╚╝ ╚═╝╝╚╝ ╩ ╚═╝ GUI EVENTS (BUTTONS)
    # ====================================================================================================
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
        self.rename_elements()
        self.Close()
