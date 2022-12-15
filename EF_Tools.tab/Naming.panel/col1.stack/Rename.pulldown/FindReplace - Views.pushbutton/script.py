# -*- coding: utf-8 -*-
__title__ = "Find and Replace in Views"
__author__ = "Erik Frits"
__version__ = 'Version: 1.2'
__doc__ = """Version: 1.2
Date    = 10.11.2020
_____________________________________________________________________
Description:

Rename multiple views at once with Find/Replace/Suffix/Prefix logic.
You can select views in Project Browser or if nothing selected
you will get a menu to select your views.

_____________________________________________________________________
How-to:

- Select views in ProjectBrowser (optional)
- Run the script
- Type Find/Replace/Prefix/Suffix as needed.
_____________________________________________________________________
Last update:
- [15.12.2022] - 1.2 RELEASE
- [10.05.2021] - 1.0 RELESE
- [10.05.2021] - ViewSchedule, ViewDrafting added.
- [10.05.2021] - GUI Updated
_____________________________________________________________________
Author: Erik Frits"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#====================================================================
from Autodesk.Revit.DB import *

# Custom
from Renaming.BaseClass_FindReplace import BaseRenaming
from Snippets._context_manager import ef_Transaction, try_except
from Snippets._selection import get_selected_views

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#====================================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument


# ╔═╗╦  ╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝ CLASS
#====================================================================

class RenameViews(BaseRenaming):
    uidoc = __revit__.ActiveUIDocument
    doc   = __revit__.ActiveUIDocument.Document

    def __init__(self):
        self.start(title=__title__, version=__version__)

    def get_selected_elements(self):
        """Get Selected Views or let user select Views from a list."""
        return get_selected_views(uidoc, title=__title__, version=__version__)

    def rename_elements(self):
        """Function to rename selected Views."""
        with ef_Transaction(self.doc, __title__, debug=True):
            for view in self.selected_elements:

                with try_except(debug=True):
                    current_name  = view.Name
                    new_name      = self.prefix + current_name.replace(self.find,self.replace) + self.suffix

                    if new_name and  new_name != current_name:
                        view.Name = new_name

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#====================================================================
if __name__ == '__main__':
    x = RenameViews()

