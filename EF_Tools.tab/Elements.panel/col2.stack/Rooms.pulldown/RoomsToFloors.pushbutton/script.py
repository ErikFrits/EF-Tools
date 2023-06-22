# -*- coding: utf-8 -*-
__title__     = "Rooms to Floors"
__author__    = "Erik Frits"
__version__   = 'Version = 1.3'
__doc__       = """Version = 1.3
Date    = 29.07.2021
_____________________________________________________________________
Description:

Create Floors from selected Rooms. 
New Floors will be selected once created.
_____________________________________________________________________
How-to:

-> Pre-Select Rooms (*optional)
-> Run the script
-> Modify/Confirm Room Selection
-> Select FloorType
-> New Floors will be selected
_____________________________________________________________________
Last update:
- [13.01.2023] - 1.3 RELEASE
- [13.01.2023] - Improved Room Selection and UI
- [08.05.2022] - 1.2 RELEASE
- [08.05.2022] - Updated GUI(Checkboxes + Filtering) + Refactoring
- [16.11.2021] - 1.1 RELEASE
- [16.11.2021] - GUI ADDED
- [29.07.2021] - 1.0 RELEASE
- [29.07.2021] - Refactored
- [29.07.2021] - Bug Solved: Floors with openings 
- [29.07.2021] - Select all rooms if none selected
_____________________________________________________________________
Author: Erik Frits"""

import traceback

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
from Autodesk.Revit.DB import *
from pyrevit import forms

# .NET IMPORTS
import clr
clr.AddReference("System")
from System.Collections.Generic import List

#Custom
from Snippets._context_manager  import ef_Transaction, try_except
from Snippets._selection        import get_selected_rooms
from GUI.forms                  import select_from_dict
from GUI.Tools.CreateFromRooms  import CreateFromRooms

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
uidoc    = __revit__.ActiveUIDocument
app      = __revit__.Application
doc      = __revit__.ActiveUIDocument.Document
rvt_year = int(app.VersionNumber)

active_view_id      = doc.ActiveView.Id
active_view         = doc.GetElement(active_view_id)
active_view_level   = active_view.GenLevel

# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝
class FloorsCreationWarningSwallower(IFailuresPreprocessor):
    def PreprocessFailures(self, failuresAccessor):
        failList = failuresAccessor.GetFailureMessages()
        for failure in failList: #type: FailureMessage
            failuresAccessor.DeleteWarning(failure)
            # print(failure)
            # fail_id = failure.GetFailureDefinitionId()
            # if fail_id == BuiltInFailures.OverlapFailures.FloorsOverlap:
            #     failuresAccessor.DeleteWarning(failure)
            # elif fail_id == BuiltInFailures.ExtrusionFailures.CannotDrawExtrusionsError:
            #     failuresAccessor.DeleteWarning(failure)

        return FailureProcessingResult.Continue

# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
#==================================================
def select_floor_type():
    """Function to display GUI and let user select Floor Type.
    :return:  Selected FloorType """
    all_floor_types = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsElementType().ToElements()
    all_floor_types = [f for f in all_floor_types if type(f) == FloorType] # Filter ModelledInPlace Elements.
    dict_floor_types = {Element.Name.GetValue(fr): fr for fr in all_floor_types}
    selected_elements = select_from_dict(dict_floor_types,
                                         title = __title__, label='Select FloorType',
                                         button_name='Select', version=__version__,
                                         SelectMultiple=False)
    if selected_elements:
        return selected_elements[0]
    forms.alert("No FloorType was selected. \nPlease, select a FloorType and Try Again.", title=__title__, exitscript=True)


def room_to_floor(room, floor_type, offset):
    new_floor = None
    try:
        # Make sure that Room is bounding.
        if not room.get_Parameter(BuiltInParameter.ROOM_AREA).AsDouble():
            return None

        #  ROOM BOUNDARIES
        room_boundaries = room.GetBoundarySegments(SpatialElementBoundaryOptions())
        floor_shape = room_boundaries[0]
        openings = list(room_boundaries)[1:] if len(room_boundaries) > 1 else []

        if rvt_year < 2022:

            with Transaction(doc,'Create Floor') as t:
                t.Start()
                failOpt = t.GetFailureHandlingOptions()
                failOpt.SetFailuresPreprocessor(FloorsCreationWarningSwallower())
                t.SetFailureHandlingOptions(failOpt)

                curve_array = CurveArray()
                for seg in floor_shape:
                    curve_array.Append(seg.GetCurve())
                new_floor = doc.Create.NewFloor(curve_array, floor_type, active_view_level, False)
                if new_floor:
                    # SET OFFSET
                    param = new_floor.get_Parameter(BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM)
                    param.Set(offset)
                t.Commit()

            #  CREATE FLOOR OPENINGS SEPERATELY BEFORE RVT 2022
            if openings:
                with Transaction(doc,'Create FloorOpening') as t2:
                    t2.Start()
                    # with ef_Transaction(doc, "Create Openings"):
                    for opening in openings:
                        with try_except():
                            opening_curve = CurveArray()
                            for seg in opening:
                                opening_curve.Append(seg.GetCurve())
                            floor_opening = doc.Create.NewOpening(new_floor, opening_curve, True)
                    t2.Commit()



        if rvt_year >= 2022:
            with Transaction(doc, 'Create FloorOpening') as t:
                t.Start()
                List_curve_loop = List[CurveLoop]()
                for room_outline in room_boundaries:
                    curve_loop = CurveLoop()
                    for seg in room_outline:
                        curve_loop.Append(seg.GetCurve())
                    List_curve_loop.Add(curve_loop)
                new_floor = Floor.Create(doc, List_curve_loop, floor_type.Id, active_view_level.Id) #FIXME
                if new_floor:
                    # SET OFFSET
                    param = new_floor.get_Parameter(BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM)
                    param.Set(offset)

                failOpt = t.GetFailureHandlingOptions()
                failOpt.SetFailuresPreprocessor(FloorsCreationWarningSwallower())
                t.SetFailureHandlingOptions(failOpt)

                t.Commit()


    except:
        # print(traceback.format_exc())
        pass

    if new_floor:
        return new_floor



def create_floors(selected_rooms, selected_floor_type, offset):
    """Function to loop through selected rooms and create floors from them."""
    new_floors = []

    with TransactionGroup(doc, __title__) as tg:
        tg.Start()
        for r in selected_rooms:
            with try_except(debug=True):
                new_floor = room_to_floor(room = r, floor_type=selected_floor_type, offset = offset)
                if new_floor:
                    new_floors.append(new_floor)
        tg.Assimilate()
    return new_floors


def get_user_input():
    all_ceil_types  = FilteredElementCollector(doc).OfClass(FloorType).OfCategory(BuiltInCategory.OST_Floors).ToElements()
    dict_ceil_types = {Element.Name.GetValue(fr): fr for fr in all_ceil_types}

    GUI = CreateFromRooms(dict_ceil_types,
                          title=__title__,
                          label="Select Floor Type:",
                          button_name='Create Floors',
                          version=__version__)
    return GUI
# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝MAIN
#==================================================
if __name__ == '__main__':
    selected_rooms      = get_selected_rooms(uidoc, exitscript=True)
    GUI                 = get_user_input()
    selected_floor_type = GUI.selected_type
    offset              = GUI.offset

    new_floors = create_floors(selected_rooms, selected_floor_type, offset)

    with try_except():
        uidoc.Selection.SetElementIds(List[ElementId]([f.Id for f in new_floors if f.IsValidObject]))
