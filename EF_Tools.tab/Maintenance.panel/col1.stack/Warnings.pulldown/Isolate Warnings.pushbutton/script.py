# -*- coding: utf-8 -*-
__title__ = "Isolate Warnings"
__version__ = 'Version = 1.0'
__doc__ = """Version = 1.0
Date    = 15.09.2022
_____________________________________________________________________
Description:
This tool will isolate elements related to your Warnings.

It can also Override Graphics to paint Warning and 
Context Elements in the given RGB values and change transparency.
_____________________________________________________________________
Last update:
- [02.10.2022] - V1.0 RELEASE
_____________________________________________________________________
To-Do:
- Paint Different Warning Types with different Colour in single view
_____________________________________________________________________
Author: Erik Frits"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ==================================================
from Autodesk.Revit.DB import *
from collections import defaultdict
from datetime import datetime

# pyRevit
from pyrevit import forms

# Custom Imports
from GUI.forms import my_WPF, ListItem
from Snippets._views import create_3D_view

# .NET Imports
import os, clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System")
from System.Collections.Generic import List
from System.Windows             import Visibility
from System.Windows.Media       import SolidColorBrush, Colors, ColorConverter
import wpf



# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application
today = datetime.now()
PATH_SCRIPT = os.path.dirname(__file__)

# Get Solid Pattern
all_patterns = FilteredElementCollector(doc).OfClass(FillPatternElement).ToElements()
solid_pattern = [i for i in all_patterns if i.GetFillPattern().IsSolidFill][0]

# COLORS
c_white   = SolidColorBrush(Colors.White)
c_gray    = SolidColorBrush(Colors.Gray)
c_magenta = SolidColorBrush(ColorConverter.ConvertFromString("#EE82EE"))

# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
# ==================================================

def flat_list(list_elements):
    """Flatten given List of Lists."""
    mylist = []
    for i in list_elements:
        if not isinstance(i, list):
            mylist.append(i)
        else:
            mylist.extend(flat_list(i))
    return mylist

# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝ CLASSES
# ==================================================
class IsolateWarnings(my_WPF):
    # DEFAULT VALUES
    context_mode   = 'show'
    view_mode      = 'multi'
    context_transp = 0
    context_color  = Color(255, 255, 255)
    warning_color  = Color(255,0,0)

    count_views_total = 1
    count_view_current     = 1

    def __init__(self):
        # LOAD XAML + RESOURCES
        self.add_wpf_resource()
        path_xaml_file = os.path.join(PATH_SCRIPT, 'IsolateWarnings.xaml')
        wpf.LoadComponent(self, path_xaml_file)

        # MAIN
        self.dict_warnings = self.get_warnings()
        self.List_warnings = self.get_List_warnings()

        # FILL DATA IN GUI
        self.main_title.Text     = __title__
        self.footer_version.Text = __version__
        self.UI_ListBox_Warnings.ItemsSource = self.List_warnings

        self.ShowDialog()

    #>>>>>>>>>> INHERIT WPF RESOURCES
    def add_wpf_resource(self):
        """Function to get resources from super()"""
        super(IsolateWarnings, self).add_wpf_resource()

    # ╔╦╗╔═╗╔╦╗╦ ╦╔═╗╔╦╗╔═╗
    # ║║║║╣  ║ ╠═╣║ ║ ║║╚═╗
    # ╩ ╩╚═╝ ╩ ╩ ╩╚═╝═╩╝╚═╝ METHODS
    # ==================================================

    def get_warnings(self):
        """Function to get all warnings in the project and sort it in a dict."""
        dict_all_warnings = defaultdict(list)

        # Sort in dict by warning name
        for w in doc.GetWarnings():
            description = w.GetDescriptionText()
            dict_all_warnings[description].append(w)
        return dict_all_warnings

    def get_List_warnings(self, sort_method = 'name'):
        """Createa a List of Warnings based on sorting method."""
        List_warnings = List[type(ListItem())]()

        sorted_warnings = None
        if sort_method == 'name':
            sorted_warnings = sorted(self.dict_warnings.items())

        elif sort_method == 'count':
            sorted_warnings = sorted(self.dict_warnings.items(), key=lambda k: len(k[1]), reverse=True)

        for name, warnings in sorted_warnings:
            count_name = '({}) {}'.format(len(warnings), name)
            List_warnings.Add(ListItem(count_name, warnings))

        return List_warnings

    def get_selected_warnings(self):
        """Get selected warning types from ListBox.
        :returns: list of lists of warning elements."""
        selected_items = []
        for item in self.UI_ListBox_Warnings.ItemsSource:
            if item.IsChecked:
                selected_items.append(item.element)

        # Make sure warnings selected
        if not selected_items:
            forms.alert('No Warnings were selected. \nPlease Try Again.',
                        title = __title__,
                        exitscript = True)

        return selected_items

    def color_from_text(self, text):
        # type:(str) -> Color
        """Function to create Color(r,g,b) from a 100,100,100 string.
        It needs refactoring, but who cares..."""

        def color_alert():
            """Helper function to show Alert if something goes wrong."""
            forms.alert('RGB Format is wrong!'
                        '\nNumbers can be between 0 and 255 and should be seperated with a comma'
                        '\nExample: 255,100,0'
                        '\nPlease Try Again.',
                        title=__title__, exitscript=True)

        try:
            # Split string into list of numbers
            rgb = text.split(',')
            if len(rgb) != 3:
                color_alert()

            # Get Values
            r = int(rgb[0])
            g = int(rgb[1])
            b = int(rgb[2])

            # Verify Values
            if any([r, g, b]) > 255 or any([r, g, b]) < 0:
                color_alert()
            return Color(r, g, b)

        except:
            color_alert()

    def paint(self, view, elements, color=None, trans=0):
        """Function to change graphic overrides of elements in a given view"""
        override_settings = OverrideGraphicSettings()

        # COLOR + PATTERN
        if color and type(color) == Color:
            override_settings.SetSurfaceForegroundPatternId(solid_pattern.Id)
            override_settings.SetSurfaceForegroundPatternColor(color)

            override_settings.SetCutForegroundPatternId(solid_pattern.Id)
            override_settings.SetCutForegroundPatternColor(color)

        # TRANSPARENCY
        if trans != 0:
            override_settings.SetSurfaceTransparency(trans)

        # OVERRIDE GRAPHICS
        for el in elements:
            view.SetElementOverrides(el.Id, override_settings)

    def do_stuff(self, warnings, view_mode=''):
        """This needs more refactoring, but I don't have time..."""
        # GET COLOURS
        self.context_color = self.color_from_text(self.UI_RGB.Text)
        self.warning_color = self.color_from_text(self.UI_RGB_warn.Text)


        warn_count = {}

        try:
            element_ids_warn = []
            for w in warnings:

                # WARNING TYPE
                if view_mode == 'multi':
                    # GET DESCRIPTION + CLEAN IT
                    txt = w.GetDescriptionText()
                    txt = ''.join(t for t in txt if t not in '\\:{}[]|;<>?`~')

                    # COUNT DESCRIPTION
                    if txt in warn_count: warn_count[txt] +=1
                    else:                 warn_count[txt] = 1
                else:
                    warn_count['All'] = 1

                # GET WARNING ELEMENT IDS
                element_ids = list(w.GetFailingElements()) + list(w.GetAdditionalElements())
                element_ids_warn += element_ids

            List_element_ids_warn = List[ElementId](element_ids_warn)
            warning_elements = [doc.GetElement(e_id) for e_id in List_element_ids_warn]

            # Create 3D View + Hide Categories
            date      = today.strftime("%y%m%d")
            warn_type = max(warn_count, key=warn_count.get)

            # CREATE 3D VIEW
            view_name = 'EF_Warnings_{}_{}'.format(date, warn_type)
            view = create_3D_view(uidoc, view_name)

            # Remove Default ViewTemplate from 3D View
            if view.ViewTemplateId != ElementId(-1):
                view.ViewTemplateId = ElementId(-1)

            view.SetCategoryHidden(ElementId(BuiltInCategory.OST_Levels), True)  # Hide Levels
            view.SetCategoryHidden(ElementId(BuiltInCategory.OST_VolumeOfInterest), True)  # Hide ScopeBoxes


            print('[{}/{}] Created View: {}'.format(self.count_view_current,
                                               self.count_views_total,
                                               view.Name))
            self.count_view_current += 1

            # GET CONTEXT ELEMENTS
            context_elements = FilteredElementCollector(doc, view.Id).Excluding(List_element_ids_warn).WhereElementIsNotElementType().ToElements()
            context_elements = [e for e in context_elements if e.CanBeHidden(view)]



            # PAINT WARNING ELEMENTS
            if self.UI_warnings_override.IsChecked:
                self.paint(view, warning_elements, self.warning_color)

            # PAINT CONTEXT ELEMENTS (if shown)
            if self.context_mode == 'show':
                if self.UI_context_override.IsChecked:
                    self.paint(view, context_elements, self.context_color, self.context_transp)
                else:
                    self.paint(view, context_elements, None, self.context_transp)

            # HIDE CONTEXT
            elif self.context_mode == 'hide':
                context_ids = [e.Id for e in context_elements]
                view.HideElements(List[ElementId](context_ids))

        except:
            import traceback
            print(traceback.format_exc())

    # ╔═╗╦  ╦╔═╗╔╗╔╔╦╗╔═╗
    # ║╣ ╚╗╔╝║╣ ║║║ ║ ╚═╗
    # ╚═╝ ╚╝ ╚═╝╝╚╝ ╩ ╚═╝ EVENTS
    #==================================================
    def UIe_filter_updated(self, sender, e):
        """Function to filter items in the UI_ListBox_Warnings."""
        # FILTER KEYWORD + CONTAINER
        filtered_list_of_items = List[type(ListItem())]()
        filter_keyword = self.UI_filter.Text

        #RESTORE ORIGINAL LIST IF EMPTY
        if not filter_keyword:
            self.UI_ListBox_Warnings.ItemsSource = self.List_warnings
            return

        # FILTER ITEMS
        for item in self.List_warnings:
            if filter_keyword.lower() in item.Name.lower():
                filtered_list_of_items.Add(item)

        # UPDATE LIST OF ITEMS
        self.UI_ListBox_Warnings.ItemsSource = filtered_list_of_items

    def UIe_slider(self, sender, e):
        self.UI_slider_value.Text = str(int(sender.Value)) +'%'
        self.context_transp       = int(sender.Value)

    def UIe_context(self,sender,e):
        if sender.Name == 'UI_context_show':
            self.context_mode = 'show'
            self.UI_context_hide.IsChecked = False

        elif sender.Name == 'UI_context_hide':
            self.context_mode = 'hide'
            self.UI_context_show.IsChecked = False


    def UIe_context_un(self, sender, e):
        if sender.Name == 'UI_context_show':
            self.context_mode = 'hide'
            self.UI_context_hide.IsChecked = True

            # COLOURS
            self.UI_txt_trans.Foreground        = c_gray
            self.UI_slider_value.Foreground     = c_gray
            self.UI_context_override.Foreground = c_gray
            self.UI_RGB.Foreground              = c_gray

        elif sender.Name == 'UI_context_hide':
            self.context_mode = 'show'
            self.UI_context_show.IsChecked = True

            # COLOURS
            self.UI_txt_trans.Foreground        = c_white
            self.UI_context_override.Foreground = c_white
            self.UI_slider_value.Foreground     = c_magenta
            self.UI_RGB.Foreground              = c_magenta

    def UIe_views(self,sender,e):
        if sender.Name == 'UI_views_multi':
            self.UI_views_single.IsChecked = False
            self.view_mode = 'multi'

        elif sender.Name == 'UI_views_single':
            self.UI_views_multi.IsChecked = False
            self.view_mode = 'single'

    def UIe_views_un(self, sender,e):
        if sender.Name == 'UI_views_multi':
            self.UI_views_single.IsChecked = True
            self.view_mode = 'single'


        elif sender.Name == 'UI_views_single':
            self.UI_views_multi.IsChecked = True
            self.view_mode = 'multi'

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
        for item in self.UI_ListBox_Warnings.ItemsSource:
            item.IsChecked = checked
            list_of_items.Add(item)

        self.UI_ListBox_Warnings.ItemsSource = list_of_items

    def btn_select_all(self, sender, e):
        """Set Selection of all visible items in ListBox to All"""
        self.select_mode(mode='all')

    def btn_select_none(self, sender, e):
        """Set Selection of all visible items in ListBox to None"""
        self.select_mode(mode='none')

    def btn_sort(self,sender,e):
        """Button Event to Resort warnings in the ListBox by Name/Count."""
        if sender.Content == 'Sort by Count':
            sender.Content = 'Sort by Name'
            self.List_warnings = self.get_List_warnings(sort_method='count')

        elif sender.Content == 'Sort by Name':
            sender.Content = 'Sort by Count'
            self.List_warnings = self.get_List_warnings(sort_method='name')

        self.UIe_filter_updated(None, None)

    # ╦═╗╦ ╦╔╗╔
    # ╠╦╝║ ║║║║
    # ╩╚═╚═╝╝╚╝
    #==================================================
    def button_run(self, sender, e):
        self.Close()

        # GET WARNINGS
        selected_warnings = self.get_selected_warnings()

        # SINGLE VIEW
        if self.view_mode == 'single':
            warnings = flat_list(selected_warnings)
            self.do_stuff(warnings)

        # MULTI VIEWS
        elif self.view_mode =='multi':
            self.count_views_total = len(selected_warnings)

            for warnings in selected_warnings:
                self.do_stuff(warnings, view_mode='multi')


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
# ==================================================
if __name__ == '__main__':
    with Transaction(doc,__title__) as t:
        t.Start()
        x = IsolateWarnings()
        t.Commit()
