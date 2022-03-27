# -*- coding: utf-8 -*-
__title__ = "Rename Materials"
__author__ = "Erik Frits"
__version__ = 'Version 1.0'
__doc__ = """Version = 1.0
Date    = 03.03.2022
_____________________________________________________________________
Description:

Rename multiple selected materials at once with 
Find/Replace/Suffix/Prefix logic.
_____________________________________________________________________
How-to:

- Run the script
- Select Materials
- Write desired Find/Replace/Prefix/Suffix Settings
- Rename selected Materials
_____________________________________________________________________
Last update:

- [09.03.2022] - 1.0 RELEASE
_____________________________________________________________________
"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
# ==================================================
import os, traceback
from Autodesk.Revit.DB import (FilteredElementCollector, Material,)
from pyrevit import forms

#>>>>>>>>>> .NET IMPORTS
import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System")
from System.Collections.Generic import List
import wpf

# LIB IMPORTS
from GUI.forms import my_WPF, ListItem
from Autodesk.Revit.Exceptions import ArgumentException
from Snippets._context_manager import ef_Transaction, try_except

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ==================================================
uidoc       = __revit__.ActiveUIDocument
doc         = __revit__.ActiveUIDocument.Document
PATH_SCRIPT = os.path.dirname(__file__)

# ╔═╗╦ ╦╦
# ║ ╦║ ║║
# ╚═╝╚═╝╩ GUI
#==================================================
class RenameMaterials(my_WPF):
    """GUI for [Views: Find and Replace]"""
    def __init__(self):
        self.List_materials          = self.generate_List_materials()

        #>>>>>>>>>> SET RESOURCES FOR WPF AND LOAD GUI
        self.add_wpf_resource()
        xaml_file = os.path.join(PATH_SCRIPT, 'RenameMaterials.xaml')
        wpf.LoadComponent(self, xaml_file)

        # UPDATE TEXT ELEMENTS
        self.main_title.Text    = __title__
        self.UI_footer_version  = __version__

        # ADD MATERIALS
        self.UI_ListBox_Materials.ItemsSource = self.List_materials

        self.ShowDialog()
    #>>>>>>>>>> INHERIT WPF RESOURCES
    def add_wpf_resource(self):
        """Function to get resources from super()"""
        super(RenameMaterials, self).add_wpf_resource()

    # ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
    # ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
    # ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
    #==================================================
    def select_mode(self, mode):
        """Helper function for following buttons:
        - UI_btn_select_all
        - UI_btn_select_none"""
        list_of_items = List[type(ListItem())]()
        checked = True if mode=='all' else False
        for item in self.UI_ListBox_Materials.ItemsSource:
            item.IsChecked = checked
            list_of_items.Add(item)
        self.UI_ListBox_Materials.ItemsSource = list_of_items

    def generate_List_materials(self):
        """Function to create a List<ListItem> to pass to ListBox in GUI"""
        list_of_items = List[type(ListItem())]()

        all_materials = FilteredElementCollector(doc).OfClass(Material).ToElements()
        dict_materials = {mat.Name: mat for mat in all_materials}

        for mat_name, mat in sorted(dict_materials.items()):
            list_of_items.Add(ListItem(mat_name, mat, False))
        return list_of_items

    def get_selected_materials(self):
        selected_items = []
        for item in self.UI_ListBox_Materials.ItemsSource:
            if item.IsChecked:
                selected_items.append(item.element)
        return selected_items

    # ╔═╗╦═╗╔═╗╔═╗╔═╗╦═╗╔╦╗╦╔═╗╔═╗
    # ╠═╝╠╦╝║ ║╠═╝║╣ ╠╦╝ ║ ║║╣ ╚═╗
    # ╩  ╩╚═╚═╝╩  ╚═╝╩╚═ ╩ ╩╚═╝╚═╝ PROPERTIES
    #==================================================
    @property
    def find(self):     return self.UI_find.Text
    @property
    def replace(self):  return self.UI_replace.Text
    @property
    def prefix(self):   return self.UI_prefix.Text
    @property
    def suffix(self):   return self.UI_suffix.Text

    # ╔═╗╦ ╦╦  ╔═╗╦  ╦╔═╗╔╗╔╔╦╗╔═╗
    # ║ ╦║ ║║  ║╣ ╚╗╔╝║╣ ║║║ ║ ╚═╗
    # ╚═╝╚═╝╩  ╚═╝ ╚╝ ╚═╝╝╚╝ ╩ ╚═╝ GUI EVENTS
    #==================================================
    def text_filter_updated(self, sender, e):
        """Function to filter items in the main_ListBox."""
        filtered_List_materials = List[type(ListItem())]()
        filter_keyword = self.UI_filter.Text

        #RESTORE ORIGINAL LIST
        if not filter_keyword:
            self.UI_ListBox_Materials.ItemsSource = self.List_materials
            return

        # FILTER ITEMS
        for item in self.List_materials:
            if filter_keyword.lower() in item.Name.lower():
                filtered_List_materials.Add(item)

        # UPDATE LIST OF ITEMS
        self.UI_ListBox_Materials.ItemsSource = filtered_List_materials

    def UI_btn_select_all(self, sender, e):
        """Function to select all materials in ListBox"""
        self.select_mode(mode='all')

    def UI_btn_select_none(self, sender, e):
        """Function to deselect all materials in ListBox"""
        self.select_mode(mode='none')

    # ╦═╗╔═╗╔╗╔╔═╗╔╦╗╔═╗
    # ╠╦╝║╣ ║║║╠═╣║║║║╣
    # ╩╚═╚═╝╝╚╝╩ ╩╩ ╩╚═╝ RENAME
    #==================================================
    def button_run(self, sender, e):
        """Rename selected Materials"""
        selected_materials = self.get_selected_materials()

        with ef_Transaction(doc,__title__):
            for mat in selected_materials:
                try:
                    current_name = mat.Name
                    new_name = self.prefix + mat.Name.replace(self.find,self.replace) + self.suffix
                    mat.Name = new_name
                    if self.UI_report.IsChecked:
                        print('{} -> {}'.format(current_name, new_name))
                except ArgumentException:
                    print("Failed to rename Material [{}].New name is already in use [{}]. Material skipped.".format(
                        mat.Name, new_name))
                except:
                    print(traceback.format_exc())

            if self.UI_report.IsChecked:
                print('-'*50)
        # UPDATE CURRENT MATERIALS
        self.List_materials                   = self.generate_List_materials()
        self.UI_ListBox_Materials.ItemsSource = self.List_materials
        self.text_filter_updated(None, None)

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#==================================================
if __name__ == '__main__':
    GUI = RenameMaterials()