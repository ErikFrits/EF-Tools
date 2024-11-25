# -*- coding: utf-8 -*-
__title__     = "Rooms to Outline"
__author__    = "Erik Frits"
__version__   = 'Version = 1.3'
__doc__       = """Version = 1.3
Date    = 29.07.2021
_____________________________________________________________________
Description:

Create DetailLines from selected Rooms's outlines. 
New DetailLines will be selected once created.
_____________________________________________________________________
How-to:

-> Pre-Select Rooms(optional)
-> Run the script
-> Modify/Confirm Room Selection
-> Select LineStyle
-> New DetailLines will be selected
_____________________________________________________________________
Last update:
- [13.01.2023] - 1.3 RELEASE
- [13.01.2023] - Improved Room Selection and UI
- [09.05.2022] - 1.2 RELEASE
- [08.05.2022] - Updated GUI(Checkboxes + Filtering) + Refactoring
- [17.11.2021] - 1.0 RELEASE
_____________________________________________________________________
Author: Erik Frits"""
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
    # IGNORE NON-BOUNDING ROOMS
    if not room.get_Parameter(BuiltInParameter.ROOM_AREA).AsDouble():
        return None

    # ROOM BOUNDARIES -> CurveLoopList
    room_boundaries = room.GetBoundarySegments(SpatialElementBoundaryOptions())
    curveLoopList = []
    for roomBoundary in room_boundaries:
        room_curve_array = CurveArray()
        for boundarySegment in roomBoundary:
            curve = boundarySegment.GetCurve()
            room_curve_array.Append(curve)
        curveLoopList.Add(room_curve_array)

    #  ENSURE NOT EMPTY
    if not curveLoopList:
        return

    # CREATE OUTLINE
    outlines = []
    for curve in curveLoopList:
        outline = doc.Create.NewDetailCurveArray(doc.ActiveView, curve)  # Create Outline

        # CHANGE LINESTYLE
        for line in outline:
            outlines.append(line)
            line.get_Parameter(BuiltInParameter.BUILDING_CURVE_GSTYLE).Set(line_style.Id)
    return outlines


def create_outlines(selected_rooms, selected_line_style):
    """Function to loop through selected rooms and create Outlines from them."""
    #  LOOP THROUGH ROOMS
    all_outlines = []
    with ef_Transaction(doc,__title__,debug=True):
        for r in selected_rooms:
            with try_except(debug=True):
                all_outlines += room_to_outline(room = r, line_style=selected_line_style)
    return all_outlines

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝MAIN
#==================================================
if __name__ == '__main__':
    selected_rooms      = get_selected_rooms(uidoc=uidoc, exitscript=True)
    all_line_styles     = get_line_styles(uidoc)
    selected_line_style = select_linestyle()
    new_outlines        = create_outlines(selected_rooms, selected_line_style)

    # Select New Outlines
    uidoc.Selection.SetElementIds(List[ElementId]([c.Id for c in new_outlines if c.IsValidObject]))

