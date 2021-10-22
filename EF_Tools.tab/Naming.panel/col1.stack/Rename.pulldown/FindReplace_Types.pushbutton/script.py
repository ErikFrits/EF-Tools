# -*- coding: utf-8 -*-
__title__ = "Find and Replace in FamilyTypes"
__author__ = "Erik Frits"
__doc__ = """Version = 1.0
Date    = 11.10.2021
_____________________________________________________________________
Description:

Rename multiple FamilyTypes at once with 
Find/Replace/Suffix/Prefix logic.

This tool will rename selected types. You can select either the
element instances and it will find its type or you can select type 
directly in ProjecBrowser. 

It has weird beheviour when selecting different categories in 
ProjectBrowser, it can not get selection in this case...

_____________________________________________________________________
How-to:

- Select elements in model or ProjectBrowser
- Run the script
- Type Find/Replace/Prefix/Suffix as needed.
_____________________________________________________________________
To-Do:

_____________________________________________________________________
Last update:

- [11.10.2021] - 1.0 RELESE
_____________________________________________________________________
"""




# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#====================================================================================================


from Autodesk.Revit.DB.Structure    import AnalyticalLinkType
from Autodesk.Revit.DB.Electrical   import ConduitType, CableTrayType
from Autodesk.Revit.DB.Plumbing     import PipingSystemType, PipeType, FlexPipeType
from Autodesk.Revit.DB.Mechanical   import  Space
from Autodesk.Revit.DB.Architecture import Room, TopographySurface

from Autodesk.Revit.DB import *


from Renaming.BaseClass_FindReplace import BaseRenaming
from Snippets._context_manager import ef_Transaction, try_except
from Snippets._variables import ALL_VIEW_TYPES, LINE_TYPES

# ╔═╗╦  ╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝ CLASS
#====================================================================================================

class RenameFamilies(BaseRenaming):
    uidoc = __revit__.ActiveUIDocument
    doc   = __revit__.ActiveUIDocument.Document
    exclude_types  = [Room, Area, Space, ViewSheet, ReferencePlane, Opening, TopographySurface] + ALL_VIEW_TYPES + LINE_TYPES

    def __init__(self):
        self.start(title=__title__)

    def get_selected_elements(self):
        return [self.doc.GetElement(elem_id) for elem_id in self.uidoc.Selection.GetElementIds() if type(self.doc.GetElement(elem_id)) not in self.exclude_types]

    def rename_elements(self):
        """Function to rename selected Groups/GroupTypes."""
        with ef_Transaction(self.doc, __title__):
            for symbol in self.selected_elements:
                with try_except():
                    try:
                        temp = self.doc.GetElement(symbol.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).AsElementId())
                        if temp:
                            symbol = temp
                    except:
                        pass
                    current_name     =  symbol.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()
                    new_name = self.prefix + current_name.replace(self.find,self.replace) + self.suffix

                    if new_name and  new_name != current_name:
                            symbol.Name = new_name

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#====================================================================================================
if __name__ == '__main__':
    x = RenameFamilies()

