# -*- coding: utf-8 -*-
__title__ = "Regions: Change Linestyle"   # Name of the button displayed in Revit
__author__ = "Erik Frits"
__version__ = 'Version = 1.4'
__doc__ = """Version = 1.4
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
from pyrevit import forms
from Autodesk.Revit.DB import  *

#>>>>>>>>>> CUSTOM IMPORTS
from Snippets._selection import get_selected_elements
from Snippets._context_manager import ef_Transaction, try_except


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
uidoc   = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document

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

# ╔╦╗╔═╗╦╔╗╔    ╔═╗╦ ╦╦
# ║║║╠═╣║║║║    ║ ╦║ ║║
# ╩ ╩╩ ╩╩╝╚╝    ╚═╝╚═╝╩ MAIN + GUI
# ==================================================
from GUI.forms import select_from_dict

# HET SELECTED FILLED REGIONS
selected_filled_regions = [element for element in get_selected_elements(uidoc) if type(element) == FilledRegion]
if not selected_filled_regions:
    forms.alert("There were no FilledRegion selected. \nPlease Try again.", __title__, exitscript=True)

# GET LINE STYLES
region = selected_filled_regions[0]
valid_line_styles_ids = region.GetValidLineStyleIdsForFilledRegion(doc)
valid_line_styles = [doc.GetElement(i) for i in valid_line_styles_ids]
dict_valid_line_styles = {i.Name: i for i in valid_line_styles}

# ASK FOR USER INPUT (select LineStyle)
selected_line_style = select_from_dict(dict_valid_line_styles, title=__title__, label='Select LineStyle', SelectMultiple=False, version=__version__)
if selected_line_style and type(selected_line_style) == list:
    selected_line_style = selected_line_style[0]
else:
    forms.alert('No LineStyle was selected. Please try Again', title=__title__ ,exitscript=True)

# CHANGE LINESTYLE
with ef_Transaction(doc, __title__):
    for region in selected_filled_regions:
        with try_except():
            region.SetLineStyleId(selected_line_style.Id)
