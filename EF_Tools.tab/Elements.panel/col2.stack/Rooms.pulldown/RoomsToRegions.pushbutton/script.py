# -*- coding: utf-8 -*-
__title__     = "Rooms to Regions"
__author__    = "Erik Frits"
__version__   = 'Version = 1.2'
__helpurl__   = 'https://www.youtube.com/watch?v=3thf8IvJVpY'
__doc__ = """Version = 1.2
Date    = 08.02.2021
_____________________________________________________________________
Description:

Create FilledRegions with selected Rooms.
If none selected it will promt user with a Yes/No dialog box
to select all visible rooms in an active view.

- As a bonus it will write Room's name into FilledRegion Comment
_____________________________________________________________________
How-to:

-> Open FloorPlan
-> Select Rooms(it will filter other elements out)
-> Run the script
-> If no rooms selected it ask to select all rooms in an ActiveView.
-> Select RegionType
_____________________________________________________________________
Last update:
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
import sys
from pyrevit import  forms
from Autodesk.Revit.DB import *

#>>>>>>>>>> .NET IMPORTS
import clr
clr.AddReference("System")
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import DialogResult, MessageBox, MessageBoxButtons

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

active_view_id      = doc.ActiveView.Id
active_view         = doc.GetElement(active_view_id)
active_view_level   = active_view.GenLevel

# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
#==================================================
def ask_select_all_rooms():
    """Function to show Yes/No dialog box to ask user 'Incl primary and dependant views and sheets?'
    :return: List of all room visible in the currect view. if None - Exit Script"""
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PROMT USER YES/NO
    dialogResult = MessageBox.Show('There were no rooms selected. Would you like to select all rooms visible in the active view?',
                                    __title__, MessageBoxButtons.YesNo)
    if (dialogResult == DialogResult.Yes):
        return FilteredElementCollector(doc, active_view_id).WherePasses(ElementCategoryFilter(BuiltInCategory.OST_Rooms)).ToElements()
    sys.exit()

def select_rooms():
    """Function to get rooms in project."""
    selected_rooms = get_selected_rooms(uidoc, exit_if_none=False)
    if not selected_rooms:
        # >>>>>>>>>>Select all rooms visible in the view or exit script.
        selected_rooms = ask_select_all_rooms()

    if not selected_rooms:
        forms.alert('No rooms were selected. \nPlease Try Again.', title= __title__, exitscript=True)
    return selected_rooms

def select_region_type():
    """Function to display GUI and let user select RegionType.
    :return:  Selected RegionType"""
    all_filled_regions = FilteredElementCollector(doc).OfClass(FilledRegionType)
    dict_filled_regions = {Element.Name.GetValue(fr): fr for fr in all_filled_regions}

    selected_elements = select_from_dict(dict_filled_regions,
                                         title = __title__, label='Select RegionType',
                                         button_name='Select', version=__version__,
                                         SelectMultiple=False)
    if selected_elements:
        return selected_elements[0]
    forms.alert("No RegionType was selected. \nPlease, Try Again.", title=__title__, exitscript=True)

def create_regions(rooms, region_type):
    """Function to loop through selected rooms and create Regions from them."""
    # >>>>>>>>>> TRANSACTION + LOOP THROUGH ROOMS
    with ef_Transaction(doc, __title__, debug=True):
        for room in rooms:

            # >>>>>>>>>> IGNORE NON-BOUNDING ROOMS
            if not room.get_Parameter(BuiltInParameter.ROOM_AREA).AsDouble():
                return None

            # >>>>>>>>>> ROOM BOUNDARIES -> CurveLoopList
            room_boundaries = room.GetBoundarySegments(SpatialElementBoundaryOptions())
            curveLoopList = []

            for roomBoundary in room_boundaries:
                room_curve_loop = CurveLoop()
                for boundarySegment in roomBoundary:
                    curve = boundarySegment.GetCurve()
                    room_curve_loop.Append(curve)
                curveLoopList.Add(room_curve_loop)

            # >>>>>>>>>> CREATE REGION
            if curveLoopList:
                filled_region = FilledRegion.Create(doc, region_type.Id, active_view_id, curveLoopList)

                #>>>>>>>>>> SET COMMENT AS ROOM NAME
                room_name = room.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()
                filled_region.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set(room_name)

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝MAIN
#==================================================
if __name__ == '__main__':
    selected_rooms       = select_rooms()
    selected_region_type = select_region_type()
    create_regions(selected_rooms, selected_region_type)
