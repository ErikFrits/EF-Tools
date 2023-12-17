# -*- coding: utf-8 -*-
__title__ = "Change Linestyle"   # Name of the button displayed in Revit
__author__ = "Erik Frits"
__version__ = 'Version = 1.5'
__doc__ = """Version = 1.5
Date    = 18.07.2021
_____________________________________________________________________
Description:

Apply selected LineStyle to borders of the selected FilledRegions.
_____________________________________________________________________
How-to:

-> Select FilledRegions
-> Run the script
-> Select LineStyle to apply
_____________________________________________________________________
Last update:
- [17.12.2023] - 1.5 RELEASE
    - Improved Selection + Refactored
- [07.02.2023] - 1.4 RELEASE
    - Bug: Error when working with multiple Projects
    - Bug: Error when no LineStyle was selected  
- [15.12.2022] - 1.3 RELEASE
- [24.10.2020] - 1.2 RELEASE
- [17.11.2021] - 1.1 RELEASE
- [17.11.2021] - Custom GUI added.
- [18.07.2021] - 1.0 RELEASE
_____________________________________________________________________
Author: Erik Frits"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
from Autodesk.Revit.DB import  *
from Autodesk.Revit.UI.Selection import *
from pyrevit import forms

#>>>>>>>>>> CUSTOM IMPORTS
from Snippets._selection       import get_selected_elements
from Snippets._context_manager import ef_Transaction, try_except


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
uidoc   = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document
selection = uidoc.Selection #type: Selection

# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝ CLASSES
#==================================================

class ListItem:
    """Helper Class for displaying selected sheets in my custom GUI."""
    def __init__(self,  Name='Unnamed', IsChecked = False, element = None):
        self.Name       = Name
        self.IsChecked  = IsChecked
        self.element    = element


class ISelectionFilter_Regions(ISelectionFilter):
    def AllowElement(self, element):
        if type(element) == FilledRegion:
            return True



# ╔╦╗╔═╗╦╔╗╔    ╔═╗╦ ╦╦
# ║║║╠═╣║║║║    ║ ╦║ ║║
# ╩ ╩╩ ╩╩╝╚╝    ╚═╝╚═╝╩ MAIN + GUI
# ==================================================
#📦 Define Placeholders
selected_regions = None

#1️⃣ Get Selected FilledRegions
selected_regions = [element for element in get_selected_elements(uidoc,exitscript=False) if type(element) == FilledRegion]

#2️⃣ Prompt PickObject if None were Selected
if not selected_regions:
    with forms.WarningBar(title='Pick Filled Regions:'):
        try:
            ref_picked_objects = selection.PickObjects(ObjectType.Element, ISelectionFilter_Regions())
            selected_regions   = [doc.GetElement(ref) for ref in ref_picked_objects]
        except:
            pass

#✅ Ensure Selected
if not selected_regions:
    forms.alert("FileldRegions weren't selected. Please Try Again.", exitscript=True)


# 3. Get ALl Line Styles
region                 = selected_regions[0]
valid_line_styles_ids  = region.GetValidLineStyleIdsForFilledRegion(doc)
valid_line_styles      = [doc.GetElement(i) for i in valid_line_styles_ids]
dict_valid_line_styles = {i.Name: i for i in valid_line_styles}


# 4. User Input - Select LineStyle
from GUI.forms import select_from_dict
selected_line_style = select_from_dict(dict_valid_line_styles,
                                       title=__title__,
                                       label='Select LineStyle',
                                       SelectMultiple=False,
                                       version=__version__)

if not selected_line_style:
    forms.alert('No LineStyle was selected. Please try Again', title=__title__ ,exitscript=True)

if type(selected_line_style) == list:
    selected_line_style = selected_line_style[0] # select_from_dict always returns a list...



#🎯 Change LineStyles
with ef_Transaction(doc, __title__):
    for region in selected_regions:
        with try_except():
            region.SetLineStyleId(selected_line_style.Id)
