# -*- coding: utf-8 -*-
__title__     = "Rooms to Floors"
__author__    = "Erik Frits"
__version__   = 'Version = 1.2'
__doc__       = """Version = 1.2
Date    = 29.07.2021
_____________________________________________________________________
Description:

Create Floors from selected Rooms.
If no rooms selected it will promt user with a Yes/No dialog box 
to select all visible Floors in an active view.
_____________________________________________________________________
How-to:

-> Select rooms
-> Run the script
-> If no rooms selected it will ask to select all rooms in an active view.
-> Select FloorType
_____________________________________________________________________
Last update:
- [08.05.2022] - 1.2 RELEASE
- [08.05.2022] - Updated GUI(Checkboxes + Filtering) + Refactoring
- [16.11.2021] - 1.1 RELEASE
- [16.11.2021] - GUI ADDED
- [29.07.2021] - 1.0 RELEASE
- [29.07.2021] - Refactored
- [29.07.2021] - Bug Solved: Floors with openings 
- [29.07.2021] - Select all rooms if none selected
_____________________________________________________________________
TO-DO:
- UI Control: Offset from level
_____________________________________________________________________
Author: Erik Frits"""
# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
import sys
from pyrevit import forms
from Autodesk.Revit.DB import (FilteredElementCollector, ElementCategoryFilter,
                               BuiltInCategory, BuiltInParameter,
                               Element, FloorType, TransactionGroup, Floor,
                               CurveArray,SpatialElementBoundaryOptions, CurveLoop)

#>>>>>>>>>> .NET IMPORTS
import clr
clr.AddReference("System")
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import DialogResult, MessageBox, MessageBoxButtons
from System.Collections.Generic import List

#Custom
from Snippets._context_manager  import ef_Transaction, try_except
from Snippets._selection        import get_selected_rooms
from GUI.forms                  import select_from_dict

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

# #TODO TEMP
# if rvt_year > 2022:
#     forms.alert('This tool is not supported in Revit 2023 yet. It will be fixed soon.', title=__title__,
#                 exitscript=True)  # FIXME


# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
#==================================================
def ask_select_all_floors():
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
        selected_rooms = ask_select_all_floors()

    if not selected_rooms:
        forms.alert('No rooms were selected. \nPlease Try Again.', title= __title__, exitscript=True)
    return selected_rooms

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
#

def room_to_floor(room, floor_type):
    # Make sure that Room is bounding.
    if not room.get_Parameter(BuiltInParameter.ROOM_AREA).AsDouble():
        return None

    # >>>>>>>>>> CREATE FLOOR
    with ef_Transaction(doc, 'Create Floor', debug=True):
        # >>>>>>>>>> ROOM BOUNDARIES
        room_boundaries = room.GetBoundarySegments(SpatialElementBoundaryOptions())
        floor_shape = room_boundaries[0]
        openings = list(room_boundaries)[1:] if len(room_boundaries) > 1 else []

        if rvt_year < 2023:
            curve_array = CurveArray()
            for seg in floor_shape:
                curve_array.Append(seg.GetCurve())
            new_floor = doc.Create.NewFloor(curve_array, floor_type, active_view_level, False)

            # >>>>>>>>>> CREATE FLOOR OPENINGS SEPERATELY BEFORE RVT 2023
            if openings:
                with ef_Transaction(doc, "Create Openings"):
                    for opening in openings:
                        opening_curve = CurveArray()
                        for seg in opening:
                            opening_curve.Append(seg.GetCurve())
                        floor_opening = doc.Create.NewOpening(new_floor, opening_curve, True)

        if rvt_year >= 2023:
            List_curve_loop = List[CurveLoop]()
            for room_outline in room_boundaries:
                curve_loop = CurveLoop()
                for seg in room_outline:
                    curve_loop.Append(seg.GetCurve())
                List_curve_loop.Add(curve_loop)
            new_floor = Floor.Create(doc, List_curve_loop, floor_type.Id, active_view_level.Id) #FIXME

    return new_floor
#
def create_floors(selected_rooms, selected_floor_type):
    """Function to loop through selected rooms and create floors from them."""
    # >>>>>>>>>> LOOP THROUGH ROOMS
    with TransactionGroup(doc, __title__) as tg:
        tg.Start()
        for r in selected_rooms:
            with try_except(debug=True):
                room_to_floor(room = r, floor_type=selected_floor_type)
        tg.Assimilate()

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝MAIN
#==================================================
if __name__ == '__main__':
    selected_rooms      = select_rooms()
    selected_floor_type = select_floor_type()
    create_floors(selected_rooms, selected_floor_type)

