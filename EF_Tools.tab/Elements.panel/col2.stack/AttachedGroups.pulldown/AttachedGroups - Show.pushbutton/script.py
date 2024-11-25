# -*- coding: utf-8 -*-

__title__ = "Attached Groups: Show"   # Name of the button displayed in Revit
__author__ = "Erik Frits"
__min_revit_ver__= 2020
__version__ = "Version 1.1"
__doc__ = """Version = 1.1
Date    = 30.11.2021
_____________________________________________________________________
Description:

This tool will Show AttachedGroups that you want on selected views.

_____________________________________________________________________
How-to:

-> Click on this tool
-> Select Groups
-> Select Attached Groups you would like to Show
_____________________________________________________________________
Last update:
- [04.12.2021] - RELEASE 1.1
- [04.12.2021] - CUSTOM GUI
- [04.12.2021] - REFACTORED
_____________________________________________________________________
Erik Frits"""


# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗
# ║║║║╠═╝║ ║╠╦╝ ║
# ╩╩ ╩╩  ╚═╝╩╚═ ╩  IMPORT
#==================================================

from Autodesk.Revit.DB import BuiltInParameter,BuiltInCategory, FilteredElementCollector

# CUSTOM
from Snippets._groups           import select_group_types, select_attached_groups, show_attached_group
from Snippets._selection        import get_selected_views
from Snippets._context_manager  import ef_Transaction

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
    selected_views                  = get_selected_views(uidoc, exit_if_none=True, title=__title__)
    selected_group_types            = select_group_types(uidoc=uidoc, title=__title__, version=__version__, exit_if_none=True)
    selected_group_type_ids         = [g.Id for g in selected_group_types]
    selected_group_names            = [g.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString() for g in selected_group_types]
    selected_attached_groups        = select_attached_groups(selected_group_types, title=__title__, label='Select AttachedGroups to Show', uidoc=uidoc, version=__version__, exit_if_none=True)
    selected_attached_group_names   = [g.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString() for g in selected_attached_groups]

    # SHOW ATTACHED GROUPS
    with ef_Transaction(doc,  __title__, debug=True):
        for view in selected_views:
            groups_in_view = FilteredElementCollector(doc, view.Id).OfCategory(BuiltInCategory.OST_IOSModelGroups).ToElements()
            filtered_groups = [g for g in groups_in_view if  g.GroupType.Id in selected_group_type_ids]

            for group in filtered_groups:
                show_attached_group(view, group, selected_attached_group_names, uidoc=uidoc)
            print("-"*60)


# EF-COMMENT:
# EXTRA CUSTOM RULE FOR FILTERING GROUPS BY MATCHING ROOM PARAMETER TO PART OF VIEW NAME.
# ModelGroups that has rooms with parameter 'TOP' = 105 will only be shown on a view that has Top 105 in its name.
#     view_top = int(view.Name.split("TOP ")[-1])
#     for group in groups_on_view:
#         try:
#             group_rooms = [doc.GetElement(id) for id in group.GetMemberIds() if
#                            "Room" in str(type(doc.GetElement(id)))]
#             random_room = group_rooms[0]
#             room_top = int(random_room.LookupParameter('Top').AsString())
#
#             if room_top == view_top:
#                 # print(group.Name ,selected_group_names)
#                     # print('Showing attached group on the view - {}'.format(view))
#                     show_attached_group(view, group, user_keyword_attached_groups)
#                 # else:
#                 #     print(group.Name, False)