# -*- coding: utf-8 -*-

__title__  = "Overview: View Filters"
__author__  = "Erik Frits"
__doc__ = """Version = 1.01
Date    = 01.07.2020
_____________________________________________________________________
Description:
Create overview of all used and unused ViewFilters in the project
with linkify buttons to the corresponding views and view templates. 
_____________________________________________________________________
How-to:
- Run the script
- You will get an output menu with the results
_____________________________________________________________________
Last update:
- [24.06.2024] - V1.0 - Added

_____________________________________________________________________
Author: Erik Frits"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ==================================================
from Autodesk.Revit.DB import *
from collections import defaultdict

# pyRevit
from pyrevit import forms, script

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ==================================================
doc    = __revit__.ActiveUIDocument.Document
uidoc  = __revit__.ActiveUIDocument
app    = __revit__.Application
output = script.get_output()


# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝
# ==================================================

def sort_view_filters(list_filters):
    """Sort View Filters by Used and Unused Filters
    :param list_filters: list of ParameterFilterElement or SelectionFilterElement
    :return:             2 Lists of sorted View Filters: [LIST OF USED FILTERS], [LIST OF UNUSED FILTERS]"""

    # Get Views + ViewTemplates
    all_views = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views)\
                                        .WhereElementIsNotElementType().ToElements()

    # Get Used View Filters
    used_ids   = []
    for view in all_views:
        view_filter_ids = view.GetFilters()

        for filter_id in view_filter_ids:
            if filter_id in list_filters:
                if filter_id not in used_ids:
                    used_ids.append(filter_id)

    # Get Unused
    unused_ids = set(list_filters) - set(used_ids)

    # Convert to Elements
    used   = [doc.GetElement(e_id) for e_id in used_ids]
    unused = [doc.GetElement(e_id) for e_id in unused_ids]

    return used, unused



# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
# ==================================================
# Get All Filters

all_param_filters = FilteredElementCollector(doc).OfClass(ParameterFilterElement).ToElementIds()
all_sel_filters   = FilteredElementCollector(doc).OfClass(SelectionFilterElement).ToElementIds()



# Sort Used/Unused for Selection/Parameter Filters
used_p_filters, unused_p_filters = sort_view_filters(all_param_filters)
used_s_filters, unused_s_filters = sort_view_filters(all_sel_filters)


# print('Parameter Used/Unused')
# print(len(used_p_filters))
# print(len(unused_p_filters))
#
# print('Selection Used/Unused')
# print(len(used_s_filters))
# print(len(unused_s_filters))


output.print_md('# Parameter View Filters')
output.print_md('Total Used Parameter View Filters: {}/{}'.format(len(used_p_filters), len(all_param_filters)))
output.print_md('## Used Parameter View Filters')
for f in used_p_filters:
    output.print_md('**{}**'.format(f.Name))



output.print_md('## Unused Parameter View Filters')
for f in unused_p_filters:
    output.print_md('**{}**'.format(f.Name))



output.print_md('# Selection View Filters')
output.print_md('Total Used Selection View Filters: {}/{}'.format(len(used_s_filters), len(all_sel_filters)))
