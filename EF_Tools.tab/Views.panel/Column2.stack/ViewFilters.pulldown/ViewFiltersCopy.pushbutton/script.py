# -*- coding: utf-8 -*-
__title__ = "ViewFilters: Copy to Another View"
__author__ = "Erik Frits"
__version__ = "Version: 1.1"
__doc__ = """Version = 1.1
Date    = 15.11.2022
_____________________________________________________________________
Description:

Copy Filters from another View/ViewTemplate with an option
to add them or override(replace current with new ones only)
_____________________________________________________________________
How-to:

-> Click on the button
-> Select Source View/ViewTemplate
-> Select Filters
-> Select Destination Views/ViewTemplates
_____________________________________________________________________
Last update:
[17.01.2023] - 1.1 Release
[17.01.2023] - Bug: ViewPlan.GetOrderedFilters() isn't available 
before RVT 21
[22.09.2022] - 1.0 Release
_____________________________________________________________________
To-Do:
- Add View/ViewTemplate different in the second menu.
_____________________________________________________________________
Author: Erik Frits"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ====================================================================================================
import os, traceback
from Autodesk.Revit.DB import *

#pyRevit
from pyrevit import forms

# Custom Imports
from GUI.forms                  import select_from_dict
from Snippets._context_manager  import ef_Transaction
from GUI.forms                  import my_WPF, ListItem

# .NET IMPORTS
import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System")
from System.Collections.Generic import List
from System.Windows.Controls import ComboBoxItem
import wpf

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ====================================================================================================
PATH_SCRIPT = os.path.dirname(__file__)

uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application
doc   = __revit__.ActiveUIDocument.Document
app_year = int(app.VersionNumber)

active_view = doc.ActiveView

# VIEWS
all_views = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).ToElements()

all_views_with_filters      = [v for v in all_views if v.GetFilters() and not v.IsTemplate]
all_templates_with_filters  = [v for v in all_views if v.GetFilters() and v.IsTemplate]
all_with_filters            = all_views_with_filters + all_templates_with_filters

if not all_with_filters:
    forms.alert("There are no Views or ViewTemplates with Filters applied to them! "
                "\nPlease add some View Filters and Try Again.", exitscript=True)

def get_dict_views(mode='all'):
    """ Function to get and sort Views in a dict based on a mode setting.
    :param mode: modes( 'all', 'views', 'viewtempaltes'
    :return:     dict of views with [ViewType] as a prefix."""

    all_views = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).ToElements()
    dict_views = {}

    for view in all_views:
        if view.ViewType == ViewType.FloorPlan:
            dict_views['[FLOOR] {}'.format(view.Name)] = view

        elif view.ViewType == ViewType.CeilingPlan:
            dict_views['[CEIL] {}'.format(view.Name)] = view

        elif view.ViewType == ViewType.ThreeD:
            dict_views['[3D] {}'.format(view.Name)] = view

        elif view.ViewType == ViewType.Section:
            dict_views['[SEC] {}'.format(view.Name)] = view

        elif view.ViewType == ViewType.Elevation:
            dict_views['[EL] {}'.format(view.Name)] = view

        elif view.ViewType ==ViewType.DraftingView:
            dict_views['[DRAFT] {}'.format(view.Name)] = view

        elif view.ViewType == ViewType.AreaPlan:
            dict_views['[AREA] {}'.format(view.Name)] = view

        elif view.ViewType == ViewType.Rendering:
            dict_views['[CAM] {}'.format(view.Name)] = view

        elif view.ViewType == ViewType.Legend:
            dict_views['[LEG] {}'.format(view.Name)] = view

        elif view.ViewType == ViewType.EngineeringPlan:
            dict_views['[STR] {}'.format(view.Name)] = view

        elif view.ViewType == ViewType.Walkthrough:
            dict_views['[WALK] {}'.format(view.Name)] = view

        else:
            dict_views['[?] {}'.format(view.Name)] = view

    return dict_views


# Create Dict of Views
dict_all_views   = get_dict_views()
dict_views_f     = {k:v for k,v in dict_all_views.items() if not v.IsTemplate and v.GetFilters() }
dict_templates_f = {k:v for k,v in dict_all_views.items() if     v.IsTemplate and v.GetFilters() }

dict_views_and_templates_f = dict_views_f.copy()
dict_views_and_templates_f.update(dict_templates_f)



# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
def select_source_view():
    """Function to select Source View/ViewTemplate"""
    src_view = select_from_dict(dict_views_and_templates_f,
                                title           = __title__,
                                label           = 'Select Source View/ViewTemplate',
                                version         = __version__,
                                SelectMultiple  = False)


    if not src_view:
        forms.alert("No Source View/ViewTemplate was Selected.\n"
                    "Please Try Again.", exitscript=True)

    return src_view[0]


def select_filters(view):
    """Function to get Applied Filters from given View."""
    filter_ids = view.GetOrderedFilters()
    filters = [doc.GetElement(e_id) for e_id in filter_ids]

    dict_filters = {f.Name: f for f in filters}

    selected_filters = select_from_dict(dict_filters,
                                        title   = __title__,
                                        label   = 'Select Filters',
                                        version = __version__)
    if not selected_filters:
        forms.alert("No Filters were Selected.\n"
                    "Please Try Again.", exitscript=True)
    return selected_filters


def select_destination_views(dict_views):
    """Function to select Destination Views/ViewTemplates."""
    dest_views = None

    try:
        dest_views = select_from_dict(dict_all_views,
                                      title   = __title__,
                                      label   = 'Select Destination View/ViewTemplates',
                                      button_name= 'Copy View Filters',
                                      version = __version__)
    except:
        forms.alert('No Destination Views/ViewTemplates were selected. \nPlease Try Again', exitscript=True)

    if not dest_views:
        forms.alert("No Destination Views were Selected.\n"
                    "Please Try Again.", exitscript=True)

    return dest_views


def create_List(dict_elements):
    """Function to create a List<ListItem> to parse it in GUI ComboBox.
    :param dict_elements:   dict of views ({name:view})
    :return:                List<ListItem>"""
    list_of_views = List[type(ListItem())]()
    for name, view in sorted(dict_elements.items()):
        list_of_views.Add(ListItem(name, view))
    return list_of_views

# Convert Dict into List[ListItem]() for ListBox
List_all_views_and_templates = create_List(dict_views_and_templates_f)
List_all_views               = create_List(dict_views_f)
List_all_templates           = create_List(dict_templates_f)



# ╔═╗╦  ╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝


class SelectFilters(my_WPF):
    src_view = None
    views    = List_all_views_and_templates
    filters  = {}

    def __init__(self):
        # Load Resources
        self.add_wpf_resource()
        path_xaml_file = os.path.join(PATH_SCRIPT, 'CopyFilters.xaml')
        wpf.LoadComponent(self, path_xaml_file)

        # Update Text
        self.main_title.Text     = __title__
        self.footer_version.Text = __version__

        # Update ListBoxes
        self.UI_ListBox_Src_Views.ItemsSource = self.views


        # REVIT
        # self.drafting_view_type = self.get_drafting_view_type()
        self.ShowDialog()


    #>>>>>>>>>> INHERIT WPF RESOURCES
    def add_wpf_resource(self):
        """Function to get resources from super()"""
        super(SelectFilters, self).add_wpf_resource()

    # ╔═╗╦ ╦╦  ╔═╗╦  ╦╔═╗╔╗╔╔╦╗╔═╗
    # ║ ╦║ ║║  ║╣ ╚╗╔╝║╣ ║║║ ║ ╚═╗
    # ╚═╝╚═╝╩  ╚═╝ ╚╝ ╚═╝╝╚╝ ╩ ╚═╝
    #==================================================
    def UI_event_checked_views(self, sender, e):
        """EventHandler to filter Views and ViewTemplate in the ListBox when checkboxes clicked."""
        #VIEWS + TEMPLATE
        if self.UI_checkbox_views.IsChecked and self.UI_checkbox_view_templates.IsChecked:
            self.views = List_all_views_and_templates

        #VIEWS
        elif self.UI_checkbox_views.IsChecked:
            self.views = List_all_views

        #TEMPLATES
        elif self.UI_checkbox_view_templates.IsChecked:
            self.views = List_all_templates

        #NONE
        else:
            self.views = {}

        #UPDATE LISTBOX
        self.UI_ListBox_Src_Views.ItemsSource = self.views
        # self.UI_text_filter_updated(0,0)

    def UI_text_filter_updated(self, sender, e):
        """Function to filter items in the UI_ListBox_Views."""
        filtered_list_of_items = List[type(ListItem())]()
        filter_keyword = self.textbox_filter.Text

        #RESTORE ORIGINAL LIST
        if not filter_keyword:
            self.UI_ListBox_Src_Views.ItemsSource = self.views
            return

        # FILTER ITEMS
        for item in self.views:
            if filter_keyword.lower() in item.Name.lower():
                filtered_list_of_items.Add(item)

        # UPDATE LIST OF ITEMS
        self.UI_ListBox_Src_Views.ItemsSource = filtered_list_of_items


    def UIe_ViewUnchecked(self, sender, e):
        self.UI_ListBox_Filters.ItemsSource = []


    def UIe_ViewChecked(self, sender, e):
        # Clear Selected Filters
        self.filters = {}


        filtered_list_of_items = List[type(ListItem())]()


        # Single Selection
        for item in self.UI_ListBox_Src_Views.Items:
            if sender.Content.Text != item.Name:
                item.IsChecked = False
            else:
                item.IsChecked = True
                self.src_view = item.element
            filtered_list_of_items.Add(item)
        self.UI_ListBox_Src_Views.ItemsSource = filtered_list_of_items

        # Update Filter's ListBox

        filter_ids = []
        if app_year >= 2021:
            filter_ids = self.src_view.GetOrderedFilters()
        else:
            filter_ids = self.src_view.GetFilters()


        filters      = [doc.GetElement(e_id) for e_id in filter_ids]
        dict_filters = {f.Name: f for f in filters}
        List_filters = create_List(dict_filters)
        self.UI_ListBox_Filters.ItemsSource = List_filters

    def UIe_FilterChecked(self, sender, e):
        for item in self.UI_ListBox_Filters.Items:
            if sender.Content.Text == item.Name:
                f = item.element
                break
        self.filters[sender.Content.Text] = f

    def UIe_FilterUnchecked(self, sender, e):
        self.filters.pop(sender.Content.Text, None)

    def select_mode(self, mode):
        """Helper function for following buttons:
        - button_select_all
        - button_select_none"""

        list_of_items = List[type(ListItem())]()
        checked = True if mode=='all' else False
        for item in self.UI_ListBox_Filters.ItemsSource:
            item.IsChecked = checked
            list_of_items.Add(item)

        self.UI_ListBox_Filters.ItemsSource = list_of_items

    def button_select_all(self, sender, e):
        """ """
        self.select_mode(mode='all')

        for item in self.UI_ListBox_Filters.ItemsSource:
            self.filters[item.Name] = item.element

    def button_select_none(self, sender, e):
        """ """
        self.select_mode(mode='none')
        self.filters = {}
    # ╦═╗╦ ╦╔╗╔
    # ╠╦╝║ ║║║║
    # ╩╚═╚═╝╝╚╝ RUN
    #==================================================

    def button_run(self, sender, e):
        self.Close()


        dest_views = select_destination_views(dict_all_views)


        print('*** Source View: {} ***'.format(self.src_view.Name))
        print('*** Selected Filters: ***')
        for f_name in self.filters.keys():
            print('- {}'.format(f_name))


        with ef_Transaction(doc,__title__, debug=True):

            print('*** Destination Views/ViewTemplates:')
            for view in dest_views:
                print('- {}'.format(view.Name))

                for filter in self.filters.values():
                    try:
                        overrides = self.src_view.GetFilterOverrides(filter.Id)
                        view.SetFilterOverrides(filter.Id, overrides)
                    except:
                        print(traceback.format_exc())

        print('\nExecution Completed.')

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝  MAIn
if __name__ == '__main__':
    SelectFilters()