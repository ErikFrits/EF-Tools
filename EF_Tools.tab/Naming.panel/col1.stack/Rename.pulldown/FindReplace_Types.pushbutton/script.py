# -*- coding: utf-8 -*-
__title__ = "Find and Replace in FamilyTypes"
__author__ = "Erik Frits"
__version__ = 'Version: 1.1'
__doc__ = """Version = 1.1
Date    = 11.10.2021
_____________________________________________________________________
Description:

Rename multiple FamilyTypes with Find/Replace logic.
You will be able to select Types from the menu.
_____________________________________________________________________
How-to:
- Run the script
- Select FamilyTypes from the Menu.
- Type Find/Replace/Prefix/Suffix as needed.
_____________________________________________________________________
Last update:
- [15.12.2022] - 1.1 UPDATE
- [11.10.2021] - 1.0 RELESE
_____________________________________________________________________
Author: Erik Frits"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#====================================================================================================
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Architecture import RailingType, HandRailType, StairsType
from Autodesk.Revit.DB.Mechanical   import FlexDuctType, DuctSystemType, DuctType, DuctInsulationType, MechanicalSystemType
from Autodesk.Revit.DB.Plumbing     import FlexPipeType, PipingSystemType, PipeInsulationType, PipeType
from Autodesk.Revit.DB.Electrical   import *

# Custom
from Renaming.BaseClass_FindReplace import BaseRenaming
from Snippets._context_manager import ef_Transaction, try_except
from GUI.forms import select_from_dict


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#====================================================================================================
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document


# ╔═╗╦  ╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝ CLASS
#====================================================================================================
class RenameFamilyTypes(BaseRenaming):
    def __init__(self):
        self.start(title=__title__, version=__version__)

    def get_selected_elements(self):
        # GET AND FILTER TYPES
        all_types = FilteredElementCollector(doc).WhereElementIsElementType().ToElements()
        incl_types = [FamilySymbol, WallType, FloorType, CeilingType, RoofType,
                      FilledRegionType, TextNoteType, AnnotationSymbolType, AnnotationSymbol,
                      DimensionType, SpotDimensionType, GridType, CurtainSystemType, MullionType, GroupType,
                      FlexPipeType, FlexDuctType, RailingType,HandRailType, CableTrayType, ConduitType,
                      DuctSystemType, DuctType,MechanicalSystemType, DuctInsulationType,
                      PipingSystemType, PipeInsulationType, PipeType,
                      StairsType, BeamSystemType]
        filtered_all_types = [typ for typ in all_types if type(typ) in incl_types]

        # CREATE DICTIONARY {FamilyName/TypeName : Type}
        dict_all_types = {}

        for typ in filtered_all_types:

            # FAMILY/TYPE NAME
            type_name = typ.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()
            family_name = ""
            with try_except():
                try:    family_name = typ.Family.Name
                except: family_name = typ.FamilyName

            # Add to Dict
            dict_all_types["{} : {}".format(family_name, type_name)] = typ

        # Select From Dict
        selected_types = select_from_dict(dict_all_types, title=__title__,
                                          version=__version__,
                                          label='Select Types to Rename. (FamilyName : TypeName)')
        return selected_types


    def rename_elements(self):
        """Function to rename selected Groups/GroupTypes."""
        with ef_Transaction(doc, __title__):
            for symbol in self.selected_elements:
                with try_except():
                    try:
                        temp = doc.GetElement(symbol.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).AsElementId())
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
    x = RenameFamilyTypes()

