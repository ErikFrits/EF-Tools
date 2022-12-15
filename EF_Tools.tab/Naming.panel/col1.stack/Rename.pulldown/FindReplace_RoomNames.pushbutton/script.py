# -*- coding: utf-8 -*-
__title__ = "Find and Replace: RoomNames"
__author__ = "Erik Frits"
__version__ = 'Version: 1.1'
__doc__ = """Version = 1.0
Date    = 10.11.2020
_____________________________________________________________________
Description:

Rename multiple Room Names at once with Find/Replae logic.
_____________________________________________________________________
How-to:

- Select Rooms 
- Run the script
- Type Find/Replace/Prefix/Suffix as needed.
- Rename Selected Rooms 
_____________________________________________________________________
Last update:
- [15.12.2022] - 1.1 UPDATE
- [10.05.2021] - 1.0 RELEASE
- [10.05.2021] - ViewSchedule, ViewDrafting added.
- [10.05.2021] - GUI Updated
_____________________________________________________________________
Author: Erik Frits"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#====================================================================
from Autodesk.Revit.DB.Architecture import Room
from Autodesk.Revit.DB import BuiltInParameter

#pyRevit
from pyrevit import forms

# Custom
from Renaming.BaseClass_FindReplace import BaseRenaming
from Snippets._context_manager      import ef_Transaction, try_except
from Snippets._selection            import get_selected_elements

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#====================================================================
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document

# ╔═╗╦  ╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝ CLASS
#====================================================================
class RenameRooms(BaseRenaming):
    def __init__(self):
        self.start(title=__title__, version=__version__)

    def get_selected_elements(self):
        """Get Selected Views or let user select Views from a list."""
        selected_elements = get_selected_elements(uidoc)
        selected_rooms = [el for el in selected_elements if type(el) == Room]
        if not selected_rooms:
            forms.alert('No Rooms were selected, \nPlease Try Again', exitscript=True, title=__title__)

        return selected_rooms


    def rename_elements(self):
        """Function to rename selected Views."""
        with ef_Transaction(doc,__title__):
            for room in self.selected_elements:
                with try_except():
                    current_name = room.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()
                    new_name     = self.prefix + current_name.replace(self.find,self.replace) + self.suffix
                    if new_name and  new_name != current_name:
                        room.Name = new_name

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#====================================================================
if __name__ == '__main__':
    x = RenameRooms()

