# -*- coding: utf-8 -*-
__title__  = "Rooms to Outline"
__author__ = "Erik Frits"
__doc__ = """Version = 1.0
Date    = 16.11.2021
_____________________________________________________________________
Description:

Create room Outline from selected rooms.
If none selected it will promt user with a Yes/No dialog box
to select all visible rooms in an active view.
_____________________________________________________________________
How-to:
-> Select rooms
-> Run the script
-> If no rooms selected it ask to select all rooms in an active view.
-> Select LineStyle
_____________________________________________________________________
Last update:
- [17.11.2021] - 1.0 RELEASE
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
                               Transaction,
                               CurveArray,
                               CurveElement,
                               Line,
                               XYZ)

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
class RoomToOutline:
    def __init__(self, room, line_style):
        self.line_style = line_style
        self.room = room
        self.area = room.get_Parameter(BuiltInParameter.ROOM_AREA).AsDouble()
        self.room_boundaries = self.room.GetBoundarySegments(SpatialElementBoundaryOptions())
        if not self.area:
            return

        #>>>>>>>>>> CREATE REGION
        dl_curve_array = self.create_outlines()


    @property
    def curve_loop_list(self):
        """Function to create a list of CurveLoop from given room boundaries."""
        curveLoopList = []
        for roomBoundary in self.room_boundaries:
            room_curve_array = CurveArray()
            for boundarySegment in roomBoundary:
                curve = boundarySegment.GetCurve()
                room_curve_array.Append(curve)
            curveLoopList.Add(room_curve_array)
        return curveLoopList

    def create_outlines(self):
        if self.curve_loop_list:
            # filled_region = FilledRegion.Create(doc, self.region_type_id, active_view_id, self.curve_loop_list)
            for i in self.curve_loop_list:
                outline = doc.Create.NewDetailCurveArray(doc.ActiveView, i) # Create Outline


                # #>>>>>>>>>> SET COMMENT AS ROOM NAME
                for line in outline:
                    line.get_Parameter(BuiltInParameter.BUILDING_CURVE_GSTYLE).Set(self.line_style.Id)
                return outline

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
        with ef_Transaction(doc, __title__, debug=True):
            for r in self.selected_rooms:
                new_region = RoomToOutline(room = r, line_style = self.selected_line_style)

    def get_selected_rooms(self):
        """Filter rooms from current selection.
        If nothing is selected - ask if it should select all rooms visible in the view."""

        # >>>>>>>>>> GET SELECTED ROOMS
        selected_rooms = get_selected_rooms(uidoc, exit_if_none=False)
        if not selected_rooms:
            # >>>>>>>>>>Select all rooms visible in the view or exit script.
            selected_rooms = ask_select_all_floors()
        return selected_rooms


    def get_line_styles(self):
        """Function to get available LineStyles for DetaiLines."""
        # CREATE TEMP LINE
        t = Transaction(doc, "temp - Create DetailLine")
        t.Start()
        new_line         = Line.CreateBound(XYZ(0,0,0), XYZ(1,1,0))
        random_line      = doc.Create.NewDetailCurve(active_view, new_line)
        line_styles_ids  = random_line.GetLineStyleIds()
        t.RollBack()

        line_styles = [doc.GetElement(line_style) for line_style in line_styles_ids]
        return line_styles

    def generate_list_items(self):
        """Function to create a ICollection to pass to ListBox in GUI"""

        line_styles = self.get_line_styles()
        self.dict_line_styles = {Element.Name.GetValue(fr): fr for fr in line_styles}

        list_of_items = List[type(ListItem())]()

        first = True
        for type_name, region_type in sorted(self.dict_line_styles.items()):
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

        self.selected_line_style = self.dict_line_styles[selected_type_name]

        # CREATE FLOORS
        self.create_regions()

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝MAIN
#==================================================
if __name__ == '__main__':
    MainGUI()