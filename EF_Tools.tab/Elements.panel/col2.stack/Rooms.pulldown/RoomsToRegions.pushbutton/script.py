# -*- coding: utf-8 -*-
__title__     = "Rooms to Regions"
__author__    = "Erik Frits"
__version__   = 'Version = 1.3'
__helpurl__   = 'https://www.youtube.com/watch?v=3thf8IvJVpY'
__doc__ = """Version = 1.3
Date    = 08.02.2021
_____________________________________________________________________
Description:

Create FilledRegions from selected Rooms. 
New FilledRegions will be selected once created.
It will also write Room's name into Comments.

_____________________________________________________________________
How-to:

-> Pre-Select Rooms(optional)
-> Run the script
-> Modify/Confirm Room Selection
-> Select RegionType
-> New Regions will be selected
_____________________________________________________________________
Last update:
- [13.01.2023] - 1.3 RELEASE
- [13.01.2023] - Improved Room Selection and UI
- [09.05.2022] - 1.2 RELEASE
- [08.05.2022] - Updated GUI(Checkboxes + Filtering) + Refactoring
- [26.07.2021] - 1.0 RELEASE
- [26.07.2021] - Refactored
- [26.07.2021] - Select all rooms if None selected
- [26.07.2021] - Solved issue with multiple boundaries
_____________________________________________________________________
Author: Erik Frits"""
# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
from Autodesk.Revit.DB import *
from pyrevit import  forms

# .NET IMPORTS
import clr
clr.AddReference("System")
from System.Collections.Generic import List

#Custom
from Snippets._context_manager  import ef_Transaction
from Snippets._selection        import get_selected_rooms
from GUI.forms                  import select_from_dict

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
uidoc   = __revit__.ActiveUIDocument
app     = __revit__.Application
doc     = __revit__.ActiveUIDocument.Document

active_view         = doc.ActiveView
active_view_id      = active_view.Id
active_view_level   = active_view.GenLevel

# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
#==================================================
def select_region_type():
    """Function to display GUI and let user select RegionType.
    :return:  Selected RegionType"""
    all_filled_regions  = FilteredElementCollector(doc).OfClass(FilledRegionType)
    dict_filled_regions = {Element.Name.GetValue(fr): fr for fr in all_filled_regions}

    selected_elements   = select_from_dict(dict_filled_regions,
                                         title = __title__, label='Select RegionType',
                                         button_name='Select', version=__version__,
                                         SelectMultiple=False)
    if selected_elements:
        return selected_elements[0]
    forms.alert("No RegionType was selected. \nPlease, Try Again.", title=__title__, exitscript=True)

def create_regions(rooms, region_type):
    """Function to loop through selected rooms and create Regions from them."""
    # TRANSACTION + LOOP THROUGH ROOMS
    all_regions = []
    with ef_Transaction(doc, __title__, debug=True):
        for room in rooms:
            try:
                # IGNORE NON-BOUNDING ROOMS
                if not room.get_Parameter(BuiltInParameter.ROOM_AREA).AsDouble():
                    return None

                # ROOM BOUNDARIES -> CurveLoopList
                room_boundaries = room.GetBoundarySegments(SpatialElementBoundaryOptions())
                curveLoopList   = List[CurveLoop]()

                for roomBoundary in room_boundaries:
                    room_curve_loop = CurveLoop()
                    for boundarySegment in roomBoundary:
                        curve = boundarySegment.GetCurve()
                        room_curve_loop.Append(curve)
                    curveLoopList.Add(room_curve_loop)

                # CREATE REGION
                if curveLoopList:
                    filled_region = FilledRegion.Create(doc, region_type.Id, active_view_id, curveLoopList)
                    all_regions.append(filled_region)

                    # SET COMMENT AS ROOM NAME
                    room_name = room.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()
                    filled_region.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set(room_name)
            except:
                pass
    return all_regions

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝MAIN
#==================================================
if __name__ == '__main__':
    selected_rooms       = get_selected_rooms(uidoc, exitscript=True)
    selected_region_type = select_region_type()
    new_regions          = create_regions(selected_rooms, selected_region_type)
    uidoc.Selection.SetElementIds(List[ElementId]([c.Id for c in new_regions if c.IsValidObject]))
