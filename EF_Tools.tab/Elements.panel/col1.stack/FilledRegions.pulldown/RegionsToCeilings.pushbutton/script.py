# -*- coding: utf-8 -*-
__title__        = "FilledRegion to Ceilings"
__min_revit_ver__= 2022
__version__ = 'Version = 1.0'
__doc__     = """Version = 1.0
Date    = 17.12.2023
_____________________________________________________________________
Description:
Convert selected FilledRegions to Ceilings.
_____________________________________________________________________
How-to:

-> Click on the button
-> Select Filled Regions to convert to Ceilings
-> Select Level
-> Select CeilingType
_____________________________________________________________________
Last update:
- [17.12.2023] - 1.0 RELEASE
_____________________________________________________________________
Author: Erik Frits"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
from Autodesk.Revit.DB           import *
from Autodesk.Revit.UI.Selection import *
from pyrevit import forms

#Custom
from Snippets._context_manager      import ef_Transaction
from GUI.Tools.CreateFromRooms      import CreateFromRooms

#.NET
import clr, traceback
clr.AddReference("System")
from System.Collections.Generic import List

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
uidoc        = __revit__.ActiveUIDocument
doc          = __revit__.ActiveUIDocument.Document
selection    = uidoc.Selection                          # type: Selection
active_level = doc.ActiveView.GenLevel

# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
#==================================================

def create_ceilings(sel_regions, ceil_type, offset):
    """Function to create Ceilings from Rooms."""
    # TRANSACTION + LOOP THROUGH ROOMS
    ceilings = []
    with ef_Transaction(doc, __title__, debug=False):
        for region in sel_regions:
            try:
                region_boundaries = region.GetBoundaries()

                # ROOM BOUNDARIES -> List[CurveLoop]()
                #  CREATE CEILINGS
                if region_boundaries:
                    ceiling = Ceiling.Create(doc, region_boundaries, ceil_type.Id, active_level.Id)
                    ceilings.append(ceiling)
                    # SET OFFSET
                    param = ceiling.get_Parameter(BuiltInParameter.CEILING_HEIGHTABOVELEVEL_PARAM)
                    param.Set(offset)

            except:
                pass
    return ceilings


def get_user_input():
    all_ceil_types  = FilteredElementCollector(doc).OfClass(CeilingType).OfCategory(BuiltInCategory.OST_Ceilings)
    dict_ceil_types = {Element.Name.GetValue(fr): fr for fr in all_ceil_types}

    GUI = CreateFromRooms(dict_ceil_types,
                          title=__title__,
                          label="Select Ceiling Type:",
                          button_name='Create Ceilings',
                          version=__version__)
    return GUI

# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝
#==================================================
class ISelectionFilter_Regions(ISelectionFilter):
    def AllowElement(self, element):
        if type(element) == FilledRegion:
            return True


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#==================================================
#1️⃣ Get FilledRegions
with forms.WarningBar(title='Pick Filled Region:'):
    try:
        ref_picked = selection.PickObjects(ObjectType.Element, ISelectionFilter_Regions())
        sel_regions     = [doc.GetElement(ref) for ref in ref_picked]

        if not sel_regions:
            forms.alert("Multie-Boundary FileldRegion wasn't selected. Please Try Again.",exitscript=True)
    except:
        pass


#2️⃣ Get User Input
GUI                = get_user_input()
selected_ceil_type = GUI.selected_type
offset             = GUI.offset

if not selected_ceil_type:
    forms.alert("No Ceiling Type was selected. Please Try Again.", title=__title__, exitscript=True)

# 3️⃣ Create Ceilings
new_ceilings = create_ceilings(sel_regions, selected_ceil_type, offset)

#4️⃣ Select New Ceilings
uidoc.Selection.SetElementIds(List[ElementId]([c.Id for c in new_ceilings if c.IsValidObject]))
