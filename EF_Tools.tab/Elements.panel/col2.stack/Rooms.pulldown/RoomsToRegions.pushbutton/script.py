# -*- coding: utf-8 -*-
__title__  = "Rooms to Regions"
__author__ = "Erik Frits"
__doc__ = """Version = 1.1
# Date    = 08.02.2021
_____________________________________________________________________
# Description:
#
# Create FilledRegions with selected rooms outline.
# If none selected it will promt user with a Yes/No dialog box
# to select all visible rooms in an active view.
#
# - As a bonus it will write Room's name into FilledRegion Comment
# _____________________________________________________________________
# How-to:
#
# -> Select rooms
# -> Run the script
# -> If no rooms selected it ask to select all rooms in an active view.
# -> Select RegionType
_____________________________________________________________________
Last update:
# - [26.07.2021] - 1.0 RELEASE
# - [26.07.2021] - Refactored
# - [26.07.2021] - Select all rooms if None selected
# - [26.07.2021] - Solved issue with multiple boundaries
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
                               Element,
                               CurveLoop,
                               FilledRegion, FilledRegionType)

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
class RoomToRegion:
    def __init__(self, room, region_type):
        self.region_type = region_type
        self.region_type_id = region_type.Id
        self.room = room
        self.area = room.get_Parameter(BuiltInParameter.ROOM_AREA).AsDouble()
        self.name = room.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()
        self.room_boundaries = self.room.GetBoundarySegments(SpatialElementBoundaryOptions())

        if not self.area:
            return

        #>>>>>>>>>> CREATE REGION
        region = self.create_Regions()

        #>>>>>>>>>> SET COMMENT AS ROOM NAME
        region.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set(self.name)

    @property
    def curve_loop_list(self):
        """Function to create a list of CurveLoop from given room boundaries."""
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
            filled_region = FilledRegion.Create(doc, self.region_type_id, active_view_id, self.curve_loop_list)
            return filled_region
            #doc.Create.NewDetailCurveArray(doc.ActiveView, roomCurves) # Create Outline

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

    def create_regions(self):
        """Function to loop through selected rooms and create floors from them."""
        # >>>>>>>>>> LOOP THROUGH ROOMS
        with ef_Transaction(doc, __title__):
            for r in self.selected_rooms:
                new_region = RoomToRegion(room = r, region_type = self.selected_region_type)

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

        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET RegionType
        all_filled_regions = FilteredElementCollector(doc).OfClass(FilledRegionType)
        self.dict_filled_regions = {Element.Name.GetValue(fr): fr for fr in all_filled_regions}

        list_of_items = List[type(ListItem())]()

        first = True
        for type_name, region_type in sorted(self.dict_filled_regions.items()):
            checked = True if first else False
            first = False
            list_of_items.Add(ListItem(type_name, checked, region_type))
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

        self.selected_region_type = self.dict_filled_regions[selected_type_name]

        # CREATE FLOORS
        self.create_regions()

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝MAIN
#==================================================
if __name__ == '__main__':
    MainGUI()