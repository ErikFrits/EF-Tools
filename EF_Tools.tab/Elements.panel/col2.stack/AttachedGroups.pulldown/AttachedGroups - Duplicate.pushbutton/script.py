# -*- coding: utf-8 -*-
__title__ = "Attached Groups: Duplicate"
__author__ = "Erik Frits"
__version__ = 'Version 1.1'
__min_revit_ver__= 2020
__doc__ = """Version = 1.1
Date    = 30.11.2021
_____________________________________________________________________
Description:

This tool will duplicate selected attached groups for 
selected groups.
_____________________________________________________________________
How-to:

-> Click on this tool
-> Select Groups
-> Select Attached Groups you would like to duplciate
-> Create new name using FindReplace logic.
_____________________________________________________________________
Last update:
- [04.12.2021] - RELEASE 1.1
- [04.12.2021] - CUSTOM GUI
- [04.12.2021] - REFACTORED
_____________________________________________________________________
"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗
# ║║║║╠═╝║ ║╠╦╝ ║
# ╩╩ ╩╩  ╚═╝╩╚═ ╩  IMPORT
#==================================================
from Autodesk.Revit.DB import BuiltInParameter

# CUSTOM
from Snippets._groups           import select_group_types, select_attached_groups
from Snippets._context_manager  import ef_Transaction
from GUI.forms                  import FindReplace


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#==================================================

if __name__ == '__main__':

    #SELECTED VIEWS
    selected_group_types            = select_group_types(uidoc=uidoc, title=__title__, version=__version__, exit_if_none=True)
    selected_group_type_ids         = [g.Id for g in selected_group_types]
    selected_group_names            = [g.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString() for g in selected_group_types]
    selected_attached_groups        = select_attached_groups(selected_group_types, title=__title__, label='Select AttachedGroups to Duplicate:', uidoc=uidoc, version=__version__, exit_if_none=True)
    selected_attached_group_names   = [g.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString() for g in selected_attached_groups]
    GUI                             = FindReplace(title=__title__, label='New Name for Attached Groups:', button_name="Duplicate")

    # DUPLICATE
    with ef_Transaction(doc,  __title__, debug=True):
        group_types     = [doc.GetElement(group_type_id) for group_type_id in selected_group_type_ids if group_type_id]
        for group_type in group_types:
            # GET ATTACHED GROUPS
            for a_group_id in group_type.GetAvailableAttachedDetailGroupTypeIds():
                a_group = uidoc.Document.GetElement(a_group_id)

                # CHECK IF IT IS IN SELECTED ATTACHED GROUPS
                orig_a_group_name = a_group.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()
                if orig_a_group_name not in selected_attached_group_names:
                    continue

                # CREATE NEW NAME
                new_group_name = GUI.find_replace(orig_a_group_name)

                # DUPLICATE
                for i in range(5):
                    try:
                        a_group.Duplicate(new_group_name)
                        break
                    except:
                        new_group_name += "*"