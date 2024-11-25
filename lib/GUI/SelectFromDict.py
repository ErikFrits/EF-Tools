# -*- coding: utf-8 -*-

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#====================================================================================================
import os

#>>>>>>>>>> pyRevit
from pyrevit import forms # Needed for wpf import to work.

# Custom Imports
from GUI.forms import my_WPF

#>>>>>>>>>> .NET IMPORTS
import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System")
from System.Collections.Generic import List
from System.Windows             import Visibility
import wpf

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

class ListItem:
    """Helper Class for displaying selected sheets in my custom GUI."""
    def __init__(self,  Name='Unnamed', element = None, checked = False):
        self.Name       = Name
        self.IsChecked  = checked
        self.element    = element

# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝ CLASSES
#====================================================================================================
class SelectFromDict(my_WPF):
    def __init__(self, items,
                 title = '__title',
                 label = "Select Elements:" ,
                 button_name = 'Select',
                 version = 'version= 1.0',
                 SelectMultiple = True):
        self.SelectMultiple = SelectMultiple
        self.given_dict_items = {k:v for k,v in items.items() if k}

        self.items          = self.generate_list_items()
        self.selected_items = []
        #>>>>>>>>>> SET RESOURCES FOR WPF
        self.add_wpf_resource()
        path_xaml_file = os.path.join(PATH_SCRIPT, 'SelectFromDict.xaml')
        wpf.LoadComponent(self, path_xaml_file )

        # UPDATE GUI ELEMENTS
        self.main_title.Text        = title
        self.text_label.Content     = label
        self.button_main.Content    = button_name
        self.footer_version.Text    = version
        if not SelectMultiple:
            self.UI_Buttons_all_none.Visibility = Visibility.Collapsed


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



    #>>>>>>>>>> INHERIT WPF RESOURCES
    def add_wpf_resource(self):
        """Function to get resources from super()"""
        super(SelectFromDict, self).add_wpf_resource()


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
            self.main_ListBox.ItemsSource = self.items

            return

        # FILTER ITEMS
        for item in self.items:
            if filter_keyword.lower() in item.Name.lower():
                filtered_list_of_items.Add(item)

        # UPDATE LIST OF ITEMS
        self.main_ListBox.ItemsSource = filtered_list_of_items


    def UIe_ItemChecked(self, sender, e):
        # SINGLE SELECTIOn
        if not self.SelectMultiple:
            filtered_list_of_items = List[type(ListItem())]()
            for item in self.main_ListBox.Items:
                item.IsChecked = True if item.Name == sender.Content.Text else False
                filtered_list_of_items.Add(item)
            self.main_ListBox.ItemsSource = filtered_list_of_items

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
        # Reset Filter
        self.textbox_filter.Text = ''
        self.Close()



        selected_items = []
        for item in self.main_ListBox.ItemsSource:
            if item.IsChecked:
                selected_items.append(item.element)
        self.selected_items = selected_items




# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝MAIN
#====================================================================================================
def select_from_dict(elements_dict,
                     title          = '__title__',
                     label          = "Select Elements:" ,
                     button_name    = 'Select',
                     version        = 'Version: 1.0',
                     SelectMultiple = True):
    #type:(any, str,str,str,str,bool) -> list
    """Function to present a DialogBox to a user to select elements from the list based on the dict keys.
    :param elements_dict:   Dictonary or list of elements {name : element}.
                                if list is provided it will be converted to dict {i:i}.
    :param title:           Title of the window.
    :param label:           Label that is displayed above ListBox
    :param button_name:     Text in Button
    :param version:         Version of the script for footer.
    :param SelectMultiple:  By default it allows multiple selection. Set False if you need only single item selection.
    :return:                Selected elements. (dict values)"""

    # CONVERT LIST TO DICT
    if isinstance(elements_dict,list):
        elements_dict = {i:i for i in elements_dict}

    GUI_select = SelectFromDict(items          = elements_dict,
                                title          = title,
                                label          = label,
                                button_name    = button_name,
                                version        = version,
                                SelectMultiple = SelectMultiple)
    return list(GUI_select)
