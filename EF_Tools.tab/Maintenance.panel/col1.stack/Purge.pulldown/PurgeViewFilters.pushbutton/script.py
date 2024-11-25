# -*- coding: utf-8 -*-
__title__ = "Purge Unused View Filters"
__doc__ = """Version = 1.0
Date    = 24.06.2024
_____________________________________________________________________
Description:
Purge Unused View Filters from your Revit Project.
_____________________________________________________________________
How-To:
- Click the Button
- Select unused View Filters to purge
_____________________________________________________________________
Last update:
- [24.06.2024] - V1.0 RELEASE
_____________________________________________________________________
Author: Erik Frits from LearnRevitAPI.com"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ==================================================
from Autodesk.Revit.DB import *

# pyRevit
from pyrevit import forms

#EF Custom Form
from GUI.forms import select_from_dict

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ==================================================
doc    = __revit__.ActiveUIDocument.Document
uidoc  = __revit__.ActiveUIDocument

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
# ==================================================
# 1️⃣ Get Views and Filters
# all_sel_filters  = FilteredElementCollector(doc).OfClass(SelectionFilterElement).ToElementIds()
all_view_filter_ids = FilteredElementCollector(doc).OfClass(ParameterFilterElement).ToElementIds()
all_views           = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).ToElements() # Views + ViewTemplates!


#2️⃣ Find Used ViewFilters
used_filter_ids = []
for view in all_views:
    view_filters = view.GetFilters()

    for filter_id in view_filters:
        view_filter = doc.GetElement(filter_id)

        # print(view_filter.Name)
        if filter_id not in used_filter_ids:
            used_filter_ids.append(filter_id)


#3️⃣ Get Unused ViewFilters
unused_filter_ids = set(all_view_filter_ids) - set(used_filter_ids)
unused_filters    = [doc.GetElement(f_id) for f_id in unused_filter_ids]


#✅ Check if Unused Filters in Project
if not unused_filters:
    forms.alert('There are no unused View Filters in the project.', title=__title__, exitscript=True)



#👉 Select View Filters to Delete
dict_filters   = {f.Name:f for f in sorted(unused_filters, key = lambda x: x.Name)}
filters_to_del = select_from_dict(dict_filters, title       = __title__,
                                                label       = 'Select Unused ViewFilters to Delete',
                                                button_name = 'Delete View Filters')


#👉 Select View Filters to Delete
# Use this pyRevit form if you want to copy the snippet
# filters_to_del = forms.SelectFromList.show(
#         sorted(unused_filters, key = lambda x: x.Name),
#         name_attr='Name',
#         title='Select filters to Delete',
#         button_name='Delete Selected View Filters',
#         multiselect=True)


#✅ Check Selection
if not filters_to_del:
    forms.alert('No View Filters were selected to be purged. Please Try Again', title=__title__, exitscript=True)


with Transaction(doc, 'Purge ViewFilters') as t:
    t.Start()   #🔓

    for filter_ in filters_to_del:
        try:
            f_name = filter_.Name
            doc.Delete(filter_.Id)
            print("✔️ Deleted ViewFilter: {}".format(f_name))
        except Exception as e:
            print("✖️ Couldn't Delete View Filter: {}".format(f_name))
            print('----- Error Message: {}'.format(e))

    t.Commit()  #🔒

