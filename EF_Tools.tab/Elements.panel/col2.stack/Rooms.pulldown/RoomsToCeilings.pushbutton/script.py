# -*- coding: utf-8 -*-
__title__ = "Rooms To Ceiling"
__version__   = 'Version = 1.0'
__min_revit_ver__= 2022
__doc__ = """Version = 1.0
Date    = 07.01.2023
_____________________________________________________________________
Description:
Create Ceilings from selected Rooms.

_____________________________________________________________________
How-to:

-> Pre-Select Rooms (*optional)
-> Run the script
-> Modify/Confirm Room Selection
-> Select CeilingType
-> Create Ceilings
_____________________________________________________________________
Last update:
- [07.01.2023] - 1.0 RELEASE
_____________________________________________________________________
Author: Erik Frits"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
from Autodesk.Revit.DB              import *
from Autodesk.Revit.DB.Architecture import Room
from Autodesk.Revit.UI.Selection    import ISelectionFilter, ObjectType, Selection
from pyrevit import forms

#Custom
from Snippets._selection            import get_selected_elements, ISelectionFilter_Classes
from Snippets._context_manager      import ef_Transaction
from GUI.forms                      import select_from_dict
from GUI.Tools.CreateFromRooms      import CreateFromRooms
from Snippets._convert              import convert_internal_units


#.NET
import clr, traceback, sys
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
def get_selected_rooms(exitscript = True):
    """Function to Pick Rooms.
    Previously selected rooms will be pre-selected."""
    selected_elements = [doc.GetElement(e_id) for e_id in selection.GetElementIds()]
    selected_rooms    = [e for e in selected_elements if type(e) == Room]
    ref_rooms         = [Reference(r) for r in selected_rooms]
    ref_preselection  = List[Reference](ref_rooms)

    error_msg = 'No Rooms were selected.\nPlease Try Again'
    # Pick Walls (exterior walls are preselected)
    ISF_Rooms          = ISelectionFilter_Classes([Room,])

    try:
        with forms.WarningBar(title='Select Rooms and click "Finish"'):
            ref_selected_rooms = selection.PickObjects(ObjectType.Element,
                                                       ISF_Rooms,
                                                       'Select Rooms',
                                                       ref_preselection)

        selected_rooms  = [doc.GetElement(ref) for ref in ref_selected_rooms]
        if not selected_rooms:
            forms.alert(error_msg, title=__title__, exitscript=exitscript)
    except:
        sys.exit()
        # forms.alert(error_msg, title=__title__, exitscript=True)

    return selected_rooms

def create_ceilings(rooms, ceil_type, offset):
    """Function to create Ceilings from Rooms."""
    # >>>>>>>>>> TRANSACTION + LOOP THROUGH ROOMS
    ceilings = []
    with ef_Transaction(doc, __title__, debug=True):
        for room in rooms:

            # >>>>>>>>>> IGNORE NON-BOUNDING ROOMS
            if not room.get_Parameter(BuiltInParameter.ROOM_AREA).AsDouble():
                return None

            # >>>>>>>>>> ROOM BOUNDARIES -> List[CurveLoop]()
            room_boundaries = room.GetBoundarySegments(SpatialElementBoundaryOptions())
            curveLoopList   = List[CurveLoop]()

            for roomBoundary in room_boundaries:
                room_curve_loop = CurveLoop()
                for boundarySegment in roomBoundary:
                    curve = boundarySegment.GetCurve()
                    room_curve_loop.Append(curve)
                curveLoopList.Add(room_curve_loop)

            # >>>>>>>>>> CREATE CEILINGS
            if curveLoopList:
                try:
                    ceiling = Ceiling.Create(doc, curveLoopList, ceil_type.Id, active_level.Id)
                    ceilings.append(ceiling)
                    # SET OFFSET
                    param = ceiling.get_Parameter(BuiltInParameter.CEILING_HEIGHTABOVELEVEL_PARAM)
                    param.Set(offset)
                except:
                    print(traceback.format_exc())
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

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#==================================================
if __name__ == '__main__':
    selected_rooms  = get_selected_rooms()

    GUI                = get_user_input()
    selected_ceil_type = GUI.selected_type
    offset             = GUI.offset

    if not selected_ceil_type:
        forms.alert("No Ceiling Type was selected. Please Try Again.", title=__title__, exitscript=True)

    new_ceilings = create_ceilings(selected_rooms, selected_ceil_type, offset)

    # Select New Ceilings
    uidoc.Selection.SetElementIds(List[ElementId]([c.Id for c in new_ceilings]))
