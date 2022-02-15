# -*- coding: utf-8 -*-
__title__ = "Regions: Change Linestyle"   # Name of the button displayed in Revit
__author__ = "Erik Frits"
__doc__ = """Version = 1.1
Date    = 18.07.2021
_____________________________________________________________________
Description:

Apply LineStyle from the list to borders 
of the selected FilledRegions.
_____________________________________________________________________
How-to:

-> Select FilledRegions
-> Run the script
-> Select LineStyle to apply
_____________________________________________________________________
Last update:
- [17.11.2021] - 1.1 RELEASE
- [17.11.2021] - Custom GUI added.
- [18.07.2021] - 1.0 RELEASE
_____________________________________________________________________
Author: Erik Frits
"""
# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
from pyrevit import forms, revit
from Autodesk.Revit.DB import  *

# >>>>>>>>>> .NET IMPORTS
import clr
clr.AddReference("System")
from System.Diagnostics.Process import Start
from System.Collections.Generic import List
from System.Windows.Window import DragMove
from System.Windows.Input import MouseButtonState

#>>>>>>>>>> CUSTOM IMPORTS
from Snippets._selection import get_selected_elements
from Snippets._context_manager import ef_Transaction, try_except


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
uidoc   = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document

# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝ CLASSES
#==================================================

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
        self.selected_filled_regions = [element for element in get_selected_elements(uidoc) if type(element) == FilledRegion]
        if not self.selected_filled_regions:
            forms.alert("There were no FilledRegion selected. \nPlease Try again.", __title__, exitscript=True)

        self.form = forms.WPFWindow.__init__(self, "Script.xaml")
        self.ListBox_FloorTypes.ItemsSource = self.generate_list_items()
        self.main_title.Text = __title__
        self.ShowDialog()

    def change_region_linestyles(self):
        """Function to change LineStyles of selected regions."""
        # >>>>>>>>>> APPLY SELECTED LINESTYLE
        with ef_Transaction(doc, __title__):
            for region in self.selected_filled_regions:
                with try_except():
                    region.SetLineStyleId(self.selected_line_style.Id)

    def generate_list_items(self):
        """Function to create a List<Class> to pass to ListBox in GUI"""
        # >>>>>>>>>> GET VALID LINESTYLES
        region                      = self.selected_filled_regions[0]
        valid_line_styles_ids       = region.GetValidLineStyleIdsForFilledRegion(doc)
        valid_line_styles           = [doc.GetElement(i) for i in valid_line_styles_ids]
        self.dict_valid_line_styles = {i.Name: i for i in valid_line_styles}

        list_of_items = List[type(ListItem())]()

        first = True
        for line_style_name, line_style in sorted(self.dict_valid_line_styles.items()):
            checked = True if first else False
            first = False
            list_of_items.Add(ListItem(line_style_name, checked, line_style))

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
        selected_line_style = None
        items = self.ListBox_FloorTypes.Items
        for item in items:
            if item.IsChecked:
                selected_line_style = item.Name
                break

        self.selected_line_style = self.dict_valid_line_styles[selected_line_style]

        # CREATE FLOORS
        self.change_region_linestyles()


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝MAIN
#==================================================
if __name__ == '__main__':
    MainGUI()