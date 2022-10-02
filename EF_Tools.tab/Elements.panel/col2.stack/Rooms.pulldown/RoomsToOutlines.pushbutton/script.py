# -*- coding: utf-8 -*-
__title__     = "Rooms to Outline"
__author__    = "Erik Frits"
__version__   = 'Version = 1.2'
__helpurl__   = 'https://www.youtube.com/watch?v=3thf8IvJVpY'
__doc__       = """Version = 1.2
Date    = 29.07.2021
_____________________________________________________________________
Description:

Create Outlines with DetailedLines from selected Rooms.
If no rooms selected it will promt user with a Yes/No dialog box 
to select all visible Rooms in an active view.
_____________________________________________________________________
How-to:

-> Open FloorPlan
-> Select Rooms(it will filter other elements out)
-> Run the script
-> If no Rooms selected it will ask to select all Rooms in an ActiveView.
-> Select LineStyle
_____________________________________________________________________
Last update:
- [09.05.2022] - 1.2 RELEASE
- [08.05.2022] - Updated GUI(Checkboxes + Filtering) + Refactoring
- [17.11.2021] - 1.0 RELEASE
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
                               CurveArray,SpatialElementBoundaryOptions)

#>>>>>>>>>> .NET IMPORTS
import clr
clr.AddReference("System")
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import DialogResult, MessageBox, MessageBoxButtons

#Custom
from Snippets._context_manager  import ef_Transaction, try_except
from Snippets._selection        import get_selected_rooms
from Snippets._lines            import get_line_styles
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

def select_linestyle():
    """Function to display GUI and let user select LineStyle.
    :return:  Selected LineStyle"""
    dict_linestyles = {ls.Name: ls for ls in all_line_styles}
    selected_elements = select_from_dict(dict_linestyles,
                                         title = __title__, label='Select LineStyle',
                                         button_name='Select', version=__version__,
                                         SelectMultiple=False)
    if selected_elements:
        return selected_elements[0]
    forms.alert("No LineStyle was selected. \nPlease, Try Again.", title=__title__, exitscript=True)

def room_to_outline(room, line_style):
    """Function..."""
    #>>>>>>>>>> IGNORE NON-BOUNDING ROOMS
    if not room.get_Parameter(BuiltInParameter.ROOM_AREA).AsDouble():
        return None

    #>>>>>>>>>> ROOM BOUNDARIES -> CurveLoopList
    room_boundaries = room.GetBoundarySegments(SpatialElementBoundaryOptions())
    curveLoopList = []
    for roomBoundary in room_boundaries:
        room_curve_array = CurveArray()
        for boundarySegment in roomBoundary:
            curve = boundarySegment.GetCurve()
            room_curve_array.Append(curve)
        curveLoopList.Add(room_curve_array)

    # >>>>>>>>>> ENSURE NOT EMPTY
    if not curveLoopList:
        return

    #>>>>>>>>>> CREATE OUTLINE
    for curve in curveLoopList:
        outline = doc.Create.NewDetailCurveArray(doc.ActiveView, curve)  # Create Outline

        #>>>>>>>>>> CHANGE LINESTYLE
        for line in outline:
            line.get_Parameter(BuiltInParameter.BUILDING_CURVE_GSTYLE).Set(line_style.Id)


def create_outlines(selected_rooms, selected_line_style):
    """Function to loop through selected rooms and create Outlines from them."""
    # >>>>>>>>>> LOOP THROUGH ROOMS
    with ef_Transaction(doc,__title__,debug=True):
        for r in selected_rooms:
            with try_except(debug=True):
                room_to_outline(room = r, line_style=selected_line_style)

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝MAIN
#==================================================
if __name__ == '__main__':
    selected_rooms      = select_rooms()
    all_line_styles     = get_line_styles(uidoc)
    selected_line_style = select_linestyle()
    create_outlines(selected_rooms, selected_line_style)