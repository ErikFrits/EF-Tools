# -*- coding: utf-8 -*-
__title__  = "Rooms to Floors"
__author__ = "Erik Frits"
__doc__ = """Version = 1.1
Date    = 29.07.2021
_____________________________________________________________________
Description:

Create Floors from selected Rooms.
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
- [16.11.2021] - 1.1 RELEASE
- [16.11.2021] - GUI ADDED
- [29.07.2021] - 1.0 RELEASE
- [29.07.2021] - Refactored
- [29.07.2021] - Solved Floors with openings 
- [29.07.2021] - Select all rooms if none selected
_____________________________________________________________________
Author: Erik Frits
"""
# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
import sys
from pyrevit import revit, forms
from Snippets._selection import get_selected_rooms
from Snippets._context_manager import ef_Transaction
from Autodesk.Revit.DB import (BuiltInParameter,
                               SpatialElementBoundaryOptions,
                               FilteredElementCollector,
                               ElementCategoryFilter,
                               BuiltInCategory,
                               CurveArray,
                               TransactionGroup,
                               Element)

#>>>>>>>>>> .NET IMPORTS
import clr
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import (DialogResult,
                                  MessageBox,
                                  MessageBoxButtons)
clr.AddReference("System")
from System.Diagnostics.Process import Start
from System.Collections.Generic import List
from System.Windows.Window      import DragMove
from System.Windows.Input       import MouseButtonState

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
def ask_select_all_floors():
    """Function to show Yes/No dialog box to ask user 'Incl primary and dependant views and sheets?'
    :return: List of all room visible in the currect view. if None - Exit Script"""
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PROMT USER YES/NO
    dialogResult = MessageBox.Show('There were no rooms selected. Would you like to select all rooms visible in the active view?',
                                    __title__,
                                    MessageBoxButtons.YesNo)

    if (dialogResult == DialogResult.Yes):
        return FilteredElementCollector(doc, active_view_id).WherePasses(ElementCategoryFilter(BuiltInCategory.OST_Rooms)).ToElements()
    sys.exit()

# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝ CLASSES
#==================================================
class RoomToFloor:
    def __init__(self, room, floor_type, active_view_level):
        """Class for creating a floor from given room.
        :param room:                Revit Room object.
        :param floor_type:          selected FloorType.
        :param active_view_level:   Level of a currently open view."""

        self.floor_type = floor_type
        self.active_view_level = active_view_level

        self.room = room
        self.area = room.get_Parameter(BuiltInParameter.ROOM_AREA).AsDouble()

        if self.area:
            self.name = room.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()
            self.room_boundaries = self.room.GetBoundarySegments(SpatialElementBoundaryOptions())

            #>>>>>>>>>> CREATE Floor
            new_floor = self.create_Floors()

    def create_Floors(self):
        """Function to create a list of CurveLoop from given room boundaries."""
        __comment__ = """Keep 2 transactions below or otherwise revit will crash without giving 
                         any error tracebacks or whatsoever. It just shuts it down without saying anything...
                         Just keep them unless you want some headache :) - Erik Frits"""

        #>>>>>>>>>> ROOM BOUNDARIES
        floor_shape = self.room_boundaries[0]
        openings = list(self.room_boundaries)[1:] if len(self.room_boundaries) > 1 else []

        #>>>>>>>>>> CREATE FLOOR
        with ef_Transaction(doc,'Create Floor'):
            curveLoopList = CurveArray()
            for seg in floor_shape:
                curveLoopList.Append(seg.GetCurve())

            new_floor = doc.Create.NewFloor(curveLoopList, self.floor_type, self.active_view_level, False)

        # >>>>>>>>>> CREATE FLOOR OPENINGS
        if openings:
            with ef_Transaction(doc,"Create Openings"):
                for opening in openings:
                    opening_curve = CurveArray()
                    for seg in opening:
                        opening_curve.Append(seg.GetCurve())

                    floor_opening = doc.Create.NewOpening(new_floor,
                                                          opening_curve,
                                                          True)
        return new_floor


class ListItem:
    """Helper Class for displaying selected sheets in my custom GUI."""
    def __init__(self,  Name='Unnamed', IsChecked = False, element = None):
        self.Name       = Name
        self.IsChecked  = IsChecked
        self.element    = element

# ╔╦╗╔═╗╦╔╗╔    ╔═╗╦ ╦╦
# ║║║╠═╣║║║║    ║ ╦║ ║║
# ╩ ╩╩ ╩╩╝╚╝    ╚═╝╚═╝╩ MAIN + GUI
# ==================================================
class MainGUI(forms.WPFWindow):
    def __init__(self):
        """Main class for GUI to creating floors from selected Rooms."""
        self.selected_rooms = self.get_selected_rooms()
        if self.selected_rooms:
            self.form = forms.WPFWindow.__init__(self, "Script.xaml")
            self.ListBox_FloorTypes.ItemsSource = self.generate_list_items()
            self.main_title.Text = __title__
            self.ShowDialog()

    def create_floors(self):
        """Function to loop through selected rooms and create floors from them."""
        # >>>>>>>>>> LOOP THROUGH ROOMS
        with TransactionGroup(doc, __title__) as tg:
            tg.Start()
            for r in self.selected_rooms:
                room = RoomToFloor(room = r,
                                   floor_type = self.selected_floor_type,
                                   active_view_level = active_view_level)
            tg.Assimilate()


    def get_selected_rooms(self):
        """Filter rooms from current selection.
        If nothing is selected - ask if it should select all rooms visible in the view."""

        # >>>>>>>>>> GET SELECTED ROOMS
        selected_rooms = get_selected_rooms(uidoc, exit_if_none=False)
        if not selected_rooms:
            # >>>>>>>>>>Select all rooms visible in the view or exit script.
            selected_rooms = ask_select_all_floors()
        return selected_rooms

    def generate_list_items(self):
        """Function to create a ICollection to pass to ListBox in GUI"""
        all_floor_types = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsElementType().ToElements()
        self.dict_floor_types = {Element.Name.GetValue(fr): fr for fr in all_floor_types}
        list_of_items = List[type(ListItem())]()

        first = True
        for type_name, floor_type in sorted(self.dict_floor_types.items()):
            checked = True if first else False
            first = False
            list_of_items.Add(ListItem(type_name, checked, floor_type))
        return list_of_items

    # ╔═╗╦═╗╔═╗╔═╗╔═╗╦═╗╔╦╗╦╔═╗╔═╗
    # ╠═╝╠╦╝║ ║╠═╝║╣ ╠╦╝ ║ ║║╣ ╚═╗
    # ╩  ╩╚═╚═╝╩  ╚═╝╩╚═ ╩ ╩╚═╝╚═╝ PROPERTIES
    # ==================================================
    @property
    def ListBox(self):
        return self.ListBox_FloorTypes

    # ╔═╗╦  ╦╔═╗╔╗╔╔╦╗  ╦ ╦╔═╗╔╗╔╔╦╗╦  ╔═╗╦═╗╔═╗
    # ║╣ ╚╗╔╝║╣ ║║║ ║   ╠═╣╠═╣║║║ ║║║  ║╣ ╠╦╝╚═╗
    # ╚═╝ ╚╝ ╚═╝╝╚╝ ╩   ╩ ╩╩ ╩╝╚╝═╩╝╩═╝╚═╝╩╚═╚═╝ GUI EVENT HANDLERS:
    # ==================================================

    def button_close(self,sender,e):
        """Stop application by clicking on a <Close> button in the top right corner."""
        self.Close()

    def Hyperlink_RequestNavigate(self, sender, e):
        """Forwarding for a Hyperlink"""
        Start(e.Uri.AbsoluteUri)

    def header_drag(self,sender,e):
        """Drag window by holding LeftButton on the header."""
        if e.LeftButton == MouseButtonState.Pressed:
            DragMove(self)

    def button_run(self,sender,e):
        """Main run button.
        Closes the dialog box and starts duplicating selected sheets."""
        self.Close()


        # GET SELECTED MAIN SHEET
        selected_type_name = None
        items = self.ListBox_FloorTypes.Items
        for item in items:
            if item.IsChecked:
                selected_type_name = item.Name
                break

        self.selected_floor_type = self.dict_floor_types[selected_type_name]

        # CREATE FLOORS
        self.create_floors()


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝MAIN
#==================================================
if __name__ == '__main__':
    MainGUI()
