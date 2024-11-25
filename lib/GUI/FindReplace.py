# -*- coding: utf-8 -*-
# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#====================================================================================================

import os, sys
from pyrevit import forms
from Autodesk.Revit.DB import ( Transaction,
                                View,
                                ViewPlan,
                                ViewSection,
                                View3D,
                                ViewSchedule,
                                ViewDrafting)
from Autodesk.Revit.Exceptions import ArgumentException

#CUSTOM
from GUI.forms import my_WPF

# .NET IMPORTS
from clr import AddReference
AddReference("System")
from System.Diagnostics.Process import Start
from System.Windows.Window import DragMove
from System.Windows.Input import MouseButtonState
import wpf



# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#====================================================================================================
PATH_SCRIPT = os.path.dirname(__file__)

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝MAIN
#====================================================================================================
class FindReplace(my_WPF):
    """GUI for [Views: Find and Replace]"""
    run = False

    def __init__(self, title, label = "Find and Replace", button_name = "Rename"):
        self.add_wpf_resource()

        path_xaml_file = os.path.join(PATH_SCRIPT, 'FindReplace.xaml')
        wpf.LoadComponent(self, path_xaml_file)
        # self.form = forms.WPFWindow.__init__(self, path_xaml_file)

        self.UI_label.Content       = label
        self.UI_main_button.Content = button_name
        self.main_title.Text        = title
        self.ShowDialog()


    def find_replace(self, name):
        #type:(str) -> str
        """Function to create new name with FindReplace logic.
        :param name: String of ucrrent name
        :return: Updated name
        """
        return self.prefix + str(name).replace(self.find, self.replace) + self.suffix


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
        sys.exit()

    def Hyperlink_RequestNavigate(self, sender, e):
        """Forwarding for a Hyperlink"""
        Start(e.Uri.AbsoluteUri)

    def header_drag(self,sender,e):
        """Drag window by holding LeftButton on the header."""
        if e.LeftButton == MouseButtonState.Pressed:
            DragMove(self)

    def button_run(self, sender, e):
        """Button action: Rename view with given """
        # view_rename(selected_views,self.find,self.replace, self.prefix, self.suffix)
        self.Close()
