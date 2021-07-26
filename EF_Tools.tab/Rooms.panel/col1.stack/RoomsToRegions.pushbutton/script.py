# -*- coding: utf-8 -*-
__title__  = "Rooms to Regions"
__author__ = "Erik Frits"
__doc__ = """Version = 1.2
Date    = 08.02.2021
_____________________________________________________________________
Description:

Create FilledRegions with selected rooms outline.
If none selected it will promt user with a Yes/No dialog box 
to select all visible rooms in an active view.

- As a bonus it will write Room's name into FilledRegion Comment
_____________________________________________________________________
How-to:

-> Select rooms
-> Run the script
-> If no rooms selected it ask to select all rooms in an active view.
_____________________________________________________________________
Last update:

- [26.07.2021] - 1.0 RELEASE
_____________________________________________________________________
To-do:

- 
_____________________________________________________________________
"""



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> IMPORTS
import sys
from pyrevit import revit, forms
from Snippets.selection import get_selected_rooms, select_region_type
from Autodesk.Revit.DB import (BuiltInParameter,
                               SpatialElementBoundaryOptions,
                               CurveLoop,
                               FilledRegion,
                               FilledRegionType,
                               FilteredElementCollector,
                               ElementCategoryFilter,
                               BuiltInCategory)

#>>>>>>>>>> .NET IMPORTS
import clr
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import (DialogResult, MessageBox,MessageBoxButtons)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VARIABLES
uidoc   = __revit__.ActiveUIDocument
app     = __revit__.Application
doc     = __revit__.ActiveUIDocument.Document

active_view_id = doc.ActiveView.Id

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> CLASSES
class RoomToRegion:
    def __init__(self, room, region_type):
        self.region_type = region_type

        self.room = room
        self.area = float(room.get_Parameter(BuiltInParameter.ROOM_AREA).AsValueString()[:-3].replace(",","."))
        self.name = room.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()
        self.room_boundaries = self.room.GetBoundarySegments(SpatialElementBoundaryOptions())

        #>>>>>>>>>> CREATE REGION
        region = self.create_Regions()

        #>>>>>>>>>> SET COMMENT AS ROOM NAME
        region.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set(self.name)

    @property
    def curve_loop_list(self):
        """Function to create a list of CurveLoop from given room boundaries."""
        if not self.area: return

        curveLoopList = []
        for roomBoundary in self.room_boundaries:
            room_curve_loop = CurveLoop()

            for boundarySegment in roomBoundary:
                curve = boundarySegment.GetCurve()
                room_curve_loop.Append(curve)

            curveLoopList.Add(room_curve_loop)
        return curveLoopList


    def create_Regions(self):
        if self.curve_loop_list:
            filled_region = FilledRegion.Create(doc, self.region_type, active_view_id, self.curve_loop_list)
            return filled_region
            #doc.Create.NewDetailCurveArray(doc.ActiveView, roomCurves)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> FUNCTIONS
def ask_select_all_rooms():
    """Function to show Yes/No dialog box to a user asking
    'Incl primary and dependant views and sheets?' """
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PROMT USER YES/NO
    dialogResult = MessageBox.Show('There were no rooms selected. Would you like to select all rooms visible in the active view?',
                                    __title__,
                                    MessageBoxButtons.YesNo)
    if (dialogResult == DialogResult.Yes):
        return True
    return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> MAIN
if __name__ == '__main__':
    #>>>>>>>>>> GET SELECTED ROOMS
    selected_rooms = get_selected_rooms(exit_if_none=False)

    if not selected_rooms:
        #Select all rooms visible in the view.
        if ask_select_all_rooms():  selected_rooms = FilteredElementCollector(doc, active_view_id).WherePasses(ElementCategoryFilter(BuiltInCategory.OST_Rooms)).ToElements()
        else:                       sys.exit()
    #>>>>>>>>>> ASK USER TO SELECT FilledRegion TYPE
    region_type = select_region_type()
    region_type_id = region_type.Id

    #>>>>>>>>>> LOOP THROUGH ROOMS
    with revit.Transaction(__title__):
        for r in selected_rooms:
            room = RoomToRegion(r, region_type_id)