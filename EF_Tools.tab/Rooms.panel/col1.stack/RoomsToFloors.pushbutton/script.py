# -*- coding: utf-8 -*-
__title__  = "Rooms to Floors"
__author__ = "Erik Frits"
__doc__ = """Version = 1.0
Date    = 29.07.2021
_____________________________________________________________________
Description:

Create Floors with selected rooms outline.
If none selected it will promt user with a Yes/No dialog box 
to select all visible Floors in an active view.
_____________________________________________________________________
How-to:

-> Select rooms
-> Run the script
-> If no rooms selected it ask to select all rooms in an active view.
-> Select FloorType
_____________________________________________________________________
Last update:

- [29.07.2021] - 1.0 RELEASE
- [29.07.2021] - Refactored
- [29.07.2021] - Solved Floors with openings 
- [29.07.2021] - Select all rooms if none selected
_____________________________________________________________________
Author: Erik Frits
"""

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> IMPORTS
import sys
from pyrevit import revit, forms
from Snippets._selection import get_selected_rooms, select_floor_type
from Autodesk.Revit.DB import (BuiltInParameter,
                               SpatialElementBoundaryOptions,
                               FilteredElementCollector,
                               ElementCategoryFilter,
                               BuiltInCategory,
                               CurveArray,
                               Transaction,
                               TransactionGroup)

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
class RoomToFloor:
    def __init__(self, room, floor_type, active_view_level):
        self.floor_type = floor_type
        self.active_view_level = active_view_level

        self.room = room
        self.area = float(room.get_Parameter(BuiltInParameter.ROOM_AREA).AsValueString()[:-3].replace(",","."))
        self.name = room.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()
        self.room_boundaries = self.room.GetBoundarySegments(SpatialElementBoundaryOptions())

        #>>>>>>>>>> CREATE Floor
        new_floor = self.create_Floors()

    def create_Floors(self):
        """Function to create a list of CurveLoop from given room boundaries."""
        if not self.area: return

        __comment__ = """
        I can't explain why, but I need to have these 2 transactions below or 
        otherwise revit will crash without giving any error tracebacks or whatsoever. 
        It just shuts it down without saying anything...
        Just keep them unless you want some headache :) 
        - Erik Frits
        """

        #>>>>>>>>>> ROOM BOUNDARIES
        floor_shape = self.room_boundaries[0]
        openings = list(self.room_boundaries)[1:] if len(self.room_boundaries) > 1 else []

        #>>>>>>>>>> CREATE FLOOR
        with Transaction(doc,'Create Floor') as t1:
            t1.Start()
            curveLoopList = CurveArray()
            for seg in floor_shape:
                curveLoopList.Append(seg.GetCurve())
            new_floor = doc.Create.NewFloor(curveLoopList, self.floor_type, self.active_view_level, False)
            t1.Commit()

        # >>>>>>>>>> CREATE FLOOR OPENINGS
        if openings:
            with Transaction(doc, 'Create Openings') as t2:
                t2.Start()
                try:
                    for opening in openings:
                        opening_curve = CurveArray()
                        for seg in opening:
                            opening_curve.Append(seg.GetCurve())

                        floor_opening = doc.Create.NewOpening(new_floor,
                                                              opening_curve,
                                                              True)
                except:
                    print("Failed to create openings. Please let know how you broke it.")
                t2.Commit()
        return new_floor


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> FUNCTIONS
def ask_select_all_floors():
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

    #>>>>>>>>>> ACTIVE VIEW LEVEL
    active_view_id = doc.ActiveView.Id
    active_view = doc.GetElement(active_view_id)
    active_view_level = active_view.GenLevel

    #>>>>>>>>>> GET SELECTED ROOMS
    selected_rooms = get_selected_rooms(uidoc, exit_if_none=False)

    if not selected_rooms:
        #>>>>>>>>>>Select all rooms visible in the view.
        if ask_select_all_floors():  selected_rooms = FilteredElementCollector(doc, active_view_id).WherePasses(ElementCategoryFilter(BuiltInCategory.OST_Rooms)).ToElements()
        else:                       sys.exit()

    #>>>>>>>>>> ASK USER TO SELECT FLOOR TYPE
    floor_type = select_floor_type(uidoc)

    #>>>>>>>>>> LOOP THROUGH ROOMS
    with TransactionGroup(doc,__title__) as tg:
        tg.Start()
        for r in selected_rooms:
            room = RoomToFloor(room = r,
                               floor_type=floor_type,
                               active_view_level=active_view_level)
        tg.Assimilate()