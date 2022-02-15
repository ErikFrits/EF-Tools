# -*- coding: utf-8 -*-

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#====================================================================================================

import os, sys

from pyrevit import revit, forms
# from Snippets._selection import get_selected_rooms
from Snippets._context_manager import ef_Transaction
from Autodesk.Revit.DB import (BuiltInParameter,
                               SpatialElementBoundaryOptions,
                               FilteredElementCollector,
                               ElementCategoryFilter,
                               BuiltInCategory,
                               Element,
                               CurveLoop,
                               Transaction,
                               CurveArray,
                               CurveElement,
                               Line,
                               XYZ)

#>>>>>>>>>> .NET IMPORTS
import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System")
from System.Diagnostics.Process import Start
from System.Collections.Generic import List
from System.Windows.Window      import DragMove
from System.Windows.Input       import MouseButtonState
import wpf
from System.Windows import Application, Window, ResourceDictionary
from System import Uri



# LIB IMPORTS
from GUI.forms import my_WPF

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#====================================================================================================
PATH_SCRIPT = os.path.dirname(__file__)

uidoc   = __revit__.ActiveUIDocument
app     = __revit__.Application
doc     = __revit__.ActiveUIDocument.Document

active_view_id      = doc.ActiveView.Id
active_view         = doc.GetElement(active_view_id)
active_view_level   = active_view.GenLevel

# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝ CLASSES
#====================================================================================================


class ListItem:
    """Helper Class for displaying selected sheets in my custom GUI."""
    def __init__(self,  Name='Unnamed', element = None):
        self.Name       = Name
        self.IsChecked  = False
        self.element    = element



class Test(my_WPF):
    def __init__(self, xaml_file, items, title = '__title', label = "Select Elements:" ,button_name = 'Select', version = 'version= 1.0'):
        self.given_dict_items = {k:v for k,v in items.items() if k}

        self.items          = self.generate_list_items()
        self.selected_items = []
        #>>>>>>>>>> SET RESOURCES FOR WPF
        self.add_wpf_resource()
        wpf.LoadComponent(self, xaml_file)

        # UPDATE GUI ELEMENTS
        self.main_title.Text        = title
        self.text_label.Content     = label
        self.button_main.Content    = button_name
        self.footer_version         = version

        self.main_ListBox.ItemsSource = self.items
        self.ShowDialog()


    def __iter__(self):
        """Return selected items."""
        return iter(self.selected_items )

    def generate_list_items(self):
        """Function to create a ICollection to pass to ListBox in GUI"""

        list_of_items = List[type(ListItem())]()
        first = True
        for type_name, floor_type in sorted(self.given_dict_items.items()):
            checked = True if first else False
            first = False
            list_of_items.Add(ListItem(type_name, floor_type))
        return list_of_items

    def update_list_items(self, new_list):
        # if new_list:
        #     self.main_ListBox.ItemsSource = new_list
        #     return
        #
        # self.main_ListBox.ItemsSource = self.items
        self.main_ListBox.ItemsSource = new_list



    #>>>>>>>>>> INHERIT WPF RESOURCES
    def add_wpf_resource(self):
        """Function to get resources from super()"""
        super(Test, self).add_wpf_resource()


    # ╔═╗╦ ╦╦  ╔═╗╦  ╦╔═╗╔╗╔╔╦╗╔═╗
    # ║ ╦║ ║║  ║╣ ╚╗╔╝║╣ ║║║ ║ ╚═╗
    # ╚═╝╚═╝╩  ╚═╝ ╚╝ ╚═╝╝╚╝ ╩ ╚═╝ GUI EVENTS
    #==================================================
    def text_filter_updated(self, sender, e):
        """Function to filter items in the main_ListBox."""
        filtered_list_of_items = List[type(ListItem())]()
        filter_keyword = self.textbox_filter.Text

        #RESTORE ORIGINAL LIST
        if not filter_keyword:
            self.update_list_items(self.items)
            return

        # FILTER ITEMS
        for item in self.items:
            if filter_keyword.lower() in item.Name.lower():
                filtered_list_of_items.Add(item)

        # UPDATE LIST OF ITEMS
        self.update_list_items(filtered_list_of_items)

    # ╔╗ ╦ ╦╔╦╗╔╦╗╔═╗╔╗╔╔═╗
    # ╠╩╗║ ║ ║  ║ ║ ║║║║╚═╗
    # ╚═╝╚═╝ ╩  ╩ ╚═╝╝╚╝╚═╝ BUTTONS
    #==================================================
    def select_mode(self, mode):
        """Helper function for following buttons:
        - button_select_all
        - button_select_none"""

        list_of_items = List[type(ListItem())]()
        checked = True if mode=='all' else False
        for item in self.main_ListBox.ItemsSource:
            item.IsChecked = checked
            list_of_items.Add(item)

        self.main_ListBox.ItemsSource = list_of_items


    def button_select_all(self, sender, e):
        """ """
        self.select_mode(mode='all')

    def button_select_none(self, sender, e):
        """ """
        self.select_mode(mode='none')


    def button_select(self, sender, e):
        """Button to finilize selection"""

        selected_items = []
        for item in self.main_ListBox.ItemsSource:
            if item.IsChecked:
                selected_items.append(item.element)
        self.selected_items = selected_items
        self.Close()




# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝MAIN
#====================================================================================================
def select_from_dict(elements_dict,
                     title          = '__title__',
                     label          = "Select Elements:" ,
                     button_name    = 'Select',
                     version        = 'version= 1.0'):
    """TODO Write good docs
    :param elements_dict: Dictonary of elements {name : element}. If list is provided it will be converted to dict {i:i}
    :param label:   Label that is displayed above ListBox
    :param button_name: Text in Button
    :param version: Version of the script for footer.
    :return:
    """
    if isinstance(elements_dict,list):
        elements_dict = {i:i for i in elements_dict}


    path_xaml_file = os.path.join(PATH_SCRIPT,'SelectFromDict.xaml')
    GUI_select = Test(xaml_file     = path_xaml_file,
                      items         = elements_dict,
                      title         = title,
                      label         = label,
                      button_name   = button_name,
                      version       = version
                      )
    return list(GUI_select)
