# -*- coding: utf-8 -*-
__title__ = "Select By Category"
__author__ = "Erik Frits"
__version__ = "Version 1.0"
__doc__ = """Version = 1.0
Date    = 22.05.2023
_____________________________________________________________________
Description:
Choose Allowed Categories for Selection with PickByRectangle
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
selection   = uidoc.Selection # type: Selection

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
    
sel_cat_ids = [cat.Id for cat in sel_cats]

# ╔═╗╔═╗╦  ╔═╗╔═╗╔╦╗
# ╚═╗║╣ ║  ║╣ ║   ║ 
# ╚═╝╚═╝╩═╝╚═╝╚═╝ ╩  SELECT
#==================================================
class ISelectionFilter_Categories(ISelectionFilter):
    def __init__(self, allowed_category_ids):
        """ ISelectionFilter made to filter with categories
        :param allowed_types: list of allowed Categories"""
        self.allowed_category_ids = allowed_category_ids

    def AllowElement(self, element):
        if element.Category.Id in self.allowed_category_ids:
            return True

filter_cat_ids       = ISelectionFilter_Categories(sel_cat_ids)
ref_selected_elements = selection.PickObjects(ObjectType.Element, filter_cat_ids)
selected_elements = [doc.GetElement(ref) for ref in ref_selected_elements]

# SET SELECTION
if selected_elements:
    try:
        selected_element_ids = [e.Id for e in selected_elements]
        uidoc.Selection.SetElementIds(List[ElementId](selected_element_ids))
    except:
        print('{} is not supported with this tool.'.format(type(selected_element)))


#==================================================
__Author__ = 'Erik Frits'