# -*- coding: utf-8 -*-
__title__ = "Find and Replace: RoomNames"
__author__ = "Erik Frits"
__helpurl__ = ""
__doc__ = """Version = 1.0
Date    = 10.11.2020
_____________________________________________________________________
Description:


Rename multiple views at once with Find/Replace/Suffix/Prefix logic.
_____________________________________________________________________
How-to:

- Select views in ProjectBrowser
- Run the script
- Type Find/Replace/Prefix/Suffix as needed.
_____________________________________________________________________
Last update:

- [10.05.2021] - 1.0 RELESE
- [10.05.2021] - ViewSchedule, ViewDrafting added.
- [10.05.2021] - GUI Updated
_____________________________________________________________________
"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#====================================================================================================
from Autodesk.Revit.DB.Architecture import Room
from Autodesk.Revit.DB import BuiltInParameter

# ef custom
from Renaming.BaseClass_FindReplace import BaseRenaming
from Snippets._context_manager import ef_Transaction, try_except

# ╔═╗╦  ╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝ CLASS
#====================================================================================================

class RenameRooms(BaseRenaming):
    uidoc = __revit__.ActiveUIDocument
    doc   = __revit__.ActiveUIDocument.Document
    element_types = [Room]

    def __init__(self):
        self.start(title=__title__)

    def rename_elements(self):
        """Function to rename selected Groups/GroupTypes."""
        with ef_Transaction(self.doc,__title__):
            for room in self.selected_elements:
                with try_except():
                    current_name = room.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()
                    new_name     = self.prefix + current_name.replace(self.find,self.replace) + self.suffix
                    if new_name and  new_name != current_name:
                        room.Name = new_name

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#====================================================================================================
if __name__ == '__main__':
    x = RenameRooms()

