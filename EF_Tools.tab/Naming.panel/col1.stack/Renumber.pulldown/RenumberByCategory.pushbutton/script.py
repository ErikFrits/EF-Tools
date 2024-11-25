# -*- coding: utf-8 -*-
__title__ = "Renumber With Spline[By Category]"
__author__ = "Erik Frits"
__version__ = "Version 1.0"
__doc__ = """Version = 1.0
Date    = 22.05.2023
_____________________________________________________________________
Description:
Renumber parameter values for elements from selected categories 
using Spline curve for order.

It will only allow you to select Text Parameters 
that are not ReadOnly!
_____________________________________________________________________
How-to:
-> Click on Button
_____________________________________________________________________
Last update:
- [22.05.2023] - 1.0 RELEASE
_____________________________________________________________________
TO-DO:

_____________________________________________________________________
Author:  Erik Frits"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
#==================================================
import os, traceback
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *

# pyRevit
from pyrevit import forms


# Custom
from GUI.forms                  import my_WPF, ListItem, select_from_dict
from Snippets._selection        import pick_curve
from Snippets._lines            import get_points_along_a_curve
from Snippets._boundingbox      import is_point_in_BB_2D
from Snippets._context_manager  import ef_Transaction

#>>>>>>>>>> .NET IMPORTS
import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System")
from System.Collections.Generic import List
from System.Windows.Controls import ComboBoxItem
import wpf

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application
rvt_year = int(app.VersionNumber)
PATH_SCRIPT = os.path.dirname(__file__)

# ╔═╗╦  ╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝
#==================================================
class UI(my_WPF):
    p_name = None
    count  = None
    prefix = None
    suffix = None

    def __init__(self, params):
        self.params = params
        # >>>>>>>>>> SET RESOURCES FOR WPF
        self.add_wpf_resource()
        path_xaml_file = os.path.join(PATH_SCRIPT, 'RenumberByCategory.xaml')
        wpf.LoadComponent(self, path_xaml_file)

        # UPDATE GUI ELEMENTS
        self.main_title.Text = __title__
        self.footer_version.Text = __version__
        self.ComboBox_add_items()
        self.ShowDialog()

    # >>>>>>>>>> INHERIT WPF RESOURCES
    def add_wpf_resource(self):
        """Function to get resources from super()"""
        super(UI, self).add_wpf_resource()

    def ComboBox_add_items(self):
        """Function to Add Project Titles to ComboBoxes on the start of the GUI."""
        for p_name in self.params:
            item  = ComboBoxItem()
            item.Content    = p_name
            item.IsSelected = False
            self.UI_combo_p_name.Items.Add(item)

    # def UIe_ComboBox_Changed(self,sender,e):
    #     for item in sender.Items:
    #         if item.IsSelected:
    #             self.p_name = item.Content

    def input_replace_PreviewTextInput(self, sender, e):
        if not e.Text.isdigit():
            e.Handled = True

    def button_run(self, sender, e):
        """Button to finilize selection"""
        # Reset Filter
        self.Close()

        # self.p_name = self.input_p_name.Text
        self.count  = self.input_count.Text
        self.prefix = self.input_prefix.Text
        self.suffix = self.input_suffix.Text
        for item in self.UI_combo_p_name.Items:
            if item.IsSelected:
                self.p_name = item.Content


# ╔═╗╔═╗╔╦╗  ╔═╗╔═╗╔╦╗╔═╗╔═╗╔═╗╦═╗╦╔═╗╔═╗
# ║ ╦║╣  ║   ║  ╠═╣ ║ ║╣ ║ ╦║ ║╠╦╝║║╣ ╚═╗
# ╚═╝╚═╝ ╩   ╚═╝╩ ╩ ╩ ╚═╝╚═╝╚═╝╩╚═╩╚═╝╚═╝ GET CATEGORIES
#==================================================
# Extra Categories

def check_cat(cat):
    """Helper function to check Categories.
    Revit 2021 had an error for category.BuiltInCategory, so I needed try/except."""
    try:
        if rvt_year > 2022:
            if cat.BuiltInCategory == BuiltInCategory.INVALID:
                return False

        if cat.CategoryType == CategoryType.Model:                  # Filter Model Categories
            return True

    except:
        # print(traceback.format_exc())
        return False

# Select Categories
cats      = doc.Settings.Categories
cats      = [cat for cat in cats if check_cat(cat)]                         # Filter only BuiltInCategories
cat_grids = doc.Settings.Categories.get_Item(BuiltInCategory.OST_Grids)     # Grids are not Model Categories, so I need to manally add it.
cat_view_ports = doc.Settings.Categories.get_Item(BuiltInCategory.OST_Viewports) # Include Viewports as well
cats.append(cat_grids)
cats.append(cat_view_ports)

dict_cats = {cat.Name : cat for cat in cats}
sel_cats  = select_from_dict(dict_cats, title=__title__, label='Select Categories' )

if not sel_cats:
    forms.alert('No Category Selected. Please Try Again', title=__title__, exitscript=True)



# ╔═╗╔═╗╦  ╔═╗╔═╗╔╦╗  ╔═╗╦ ╦╦═╗╦  ╦╔═╗
# ╚═╗║╣ ║  ║╣ ║   ║   ║  ║ ║╠╦╝╚╗╔╝║╣
# ╚═╝╚═╝╩═╝╚═╝╚═╝ ╩   ╚═╝╚═╝╩╚═ ╚╝ ╚═╝ SELECT CURVE
#==================================================
try:
    with forms.WarningBar(title="Pick Curve for Numbering:", handle_esc=True):
        selected_curve = pick_curve(uidoc)
except:
    selected_curve = None

if not selected_curve:
    forms.alert("Curve was not selected. \nPlease Try Again.", title = __title__, exitscript=True)

# ╔═╗╔═╗╔╦╗  ╔═╗╦  ╔═╗╔╦╗╔═╗╔╗╔╔╦╗╔═╗
# ║ ╦║╣  ║   ║╣ ║  ║╣ ║║║║╣ ║║║ ║ ╚═╗
# ╚═╝╚═╝ ╩   ╚═╝╩═╝╚═╝╩ ╩╚═╝╝╚╝ ╩ ╚═╝ GET ELEMENTS
#==================================================
# Create MultiCategory Filter
sel_cats  = [cat.Id for cat in sel_cats]
List_cats        = List[ElementId](sel_cats)
multi_cat_filter = ElementMulticategoryFilter(List_cats)

# Get Elements from ActiveView that matches Selected Categories
all_elements = FilteredElementCollector(doc, doc.ActiveView.Id).WherePasses(multi_cat_filter).WhereElementIsNotElementType().ToElements()
all_elements = list(all_elements)

if not all_elements:
    forms.alert('No Elements found with selected categories in ActiveView. Please Try Again',
                title=__title__,
                exitscript=True)


# ╦╔╗╔╔╦╗╔═╗╦═╗╔═╗╔═╗╔═╗╔╦╗
# ║║║║ ║ ║╣ ╠╦╝╚═╗║╣ ║   ║
# ╩╝╚╝ ╩ ╚═╝╩╚═╚═╝╚═╝╚═╝ ╩  INTERSECT
#==================================================
intersected_elements = []
points = get_points_along_a_curve(selected_curve)

for pt in points:
    for el in all_elements:
        try:
            BB = el.get_BoundingBox(doc.ActiveView)
            if is_point_in_BB_2D(BB, pt):
                intersected_elements.append(el)
                all_elements.remove(el)
                break
        except:
            pass

if not intersected_elements:
    forms.alert('No intersecting elements were found. \nPlease try again.',
                title=__title__,
                exitscript=True)

# ╔═╗╔═╗╔╦╗  ╔═╗╔═╗╦═╗╔═╗╔╦╗╔═╗╔╦╗╔═╗╦═╗╔═╗
# ║ ╦║╣  ║   ╠═╝╠═╣╠╦╝╠═╣║║║║╣  ║ ║╣ ╠╦╝╚═╗
# ╚═╝╚═╝ ╩   ╩  ╩ ╩╩╚═╩ ╩╩ ╩╚═╝ ╩ ╚═╝╩╚═╚═╝ GET PARAMETERS
#==================================================
writable_params = []

for element in intersected_elements:
    params = element.Parameters
    for param in params:
        p_name = param.Definition.Name
        if p_name not in writable_params:
            if not param.IsReadOnly:
                if param.StorageType == StorageType.String:
                    writable_params.append(p_name)

writable_params.sort()

# ╦ ╦╔═╗╔═╗╦═╗  ╦╔╗╔╔═╗╦ ╦╔╦╗
# ║ ║╚═╗║╣ ╠╦╝  ║║║║╠═╝║ ║ ║
# ╚═╝╚═╝╚═╝╩╚═  ╩╝╚╝╩  ╚═╝ ╩  USER INPUT
#==================================================
user_input = UI(writable_params)

p_name = user_input.p_name
count  = int(user_input.count)   if user_input.count else None
prefix = user_input.prefix
suffix = user_input.suffix

if not p_name: forms.alert("'Parameter Name' was not provided! \nPlease Try Again.", title = __title__, exitscript=True)
if not count:  forms.alert("'Count' was not provided!          \nPlease Try Again.", title = __title__, exitscript=True)

# ╦═╗╔═╗╔╗╔╦ ╦╔╦╗╔╗ ╔═╗╦═╗
# ╠╦╝║╣ ║║║║ ║║║║╠╩╗║╣ ╠╦╝
# ╩╚═╚═╝╝╚╝╚═╝╩ ╩╚═╝╚═╝╩╚═ RENUMBER
#==================================================
with ef_Transaction(doc, __title__, debug=True):
    for el in intersected_elements:
        param = el.LookupParameter(p_name)

        if param:
            try:
                value = prefix + str(count) + suffix
                param.Set(value)
                count += 1
            except:
                pass
#==================================================
__Author__ = 'Erik Frits'