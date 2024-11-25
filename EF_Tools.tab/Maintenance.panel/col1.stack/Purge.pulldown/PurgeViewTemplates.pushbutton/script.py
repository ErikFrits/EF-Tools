# -*- coding: utf-8 -*-
__title__ = "Purge Unused View Templates"
__doc__ = """Version = 1.0
Date    = 24.06.2024
_____________________________________________________________________
Description:
Purge Unused View Templates from your Revit Project.
_____________________________________________________________________
How-To:
- Click the Button
- Select unused View Templates to purge
_____________________________________________________________________
Last update:
- [28.06.2024] - V1.0 RELEASE
_____________________________________________________________________
Author: Erik Frits from LearnRevitAPI.com"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ==================================================
from Autodesk.Revit.DB import *
from collections import defaultdict

# pyRevit
from pyrevit import forms, script

#EF Custom Form
from GUI.forms import select_from_dict

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ==================================================
doc    = __revit__.ActiveUIDocument.Document
uidoc  = __revit__.ActiveUIDocument
output = script.get_output()
# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
# ==================================================
#👉 Get Views and ViewTemplates
all_views_and_vt = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views)\
                .WhereElementIsNotElementType().ToElements()
all_views  = [v    for v in all_views_and_vt if not v.IsTemplate]
all_vt_ids = [v.Id for v in all_views_and_vt if     v.IsTemplate]


#🔬 Get Used ViewTemplates
used_vt_ids = []
for view in all_views:
    vt_id = view.ViewTemplateId
    if vt_id != ElementId(-1):
        if vt_id not in used_vt_ids:
            used_vt_ids.append(vt_id)


# Get All Unused ViewTemplates
unused_vt_ids = set(all_vt_ids) - set(used_vt_ids)
unused_vt     = [doc.GetElement(v_id) for v_id in unused_vt_ids]

# ✅ Ensure Unused ViewTemplates
if not unused_vt:
    forms.alert('No Unused ViewTemplates in the project. Please Try Again', title=__title__, exitscript=True)

#🔎 Select ViewTemplates to Purge
# vt_to_del = forms.SelectFromList.show(unused_vt,
#                                 multiselect=False,
#                                 name_attr='Name',
#                                 button_name='Select View Templates to Purge')

dict_unused_vt = {vt.Name: vt for vt in unused_vt}
vt_to_del = select_from_dict(dict_unused_vt, title=__title__,label='Select ViewTemplates to Purge', button_name='Purge')

# ✅ Ensure ViewTemplates were selected
if not vt_to_del:
    forms.alert('No ViewTemplates were selected. Please Try Again', title=__title__, exitscript=True)

#👀 Print ViewTemplates Report
output.print_md('### There were {}/{} Unused ViewTemplates in the project.'.format(len(unused_vt_ids), len(all_vt_ids)))
# output.print_md('Total ViewTemplates:  **{}**'.format(len(all_vt_ids)))
# output.print_md('Used ViewTemplates:   {}'.format(len(used_vt_ids)))
# output.print_md('Unused ViewTemplates: {}'.format(len(unused_vt_ids)))
output.print_md('---')

#🔥 Purge View Templates
t = Transaction(doc,'Purge ViewTemplates')
t.Start()   #🔓

deleted = 0
for vt in vt_to_del:
    try:
        vt_name = vt.Name
        doc.Delete(vt.Id)
        output.print_md('🔥Purged ViewTemplate: **{}**'.format(vt_name))
        deleted += 1
    except Exception as e:
        print("✖️ Couldn't delete ViewTempalte: {} due to {}".format(vt_name, e))

t.Commit()  #🔒

#👀 Create Final print statement
output.print_md('---')
output.print_md('*Script Execution has finished. {} ViewTemplates were purged.*'.format(deleted))

#⌨️ Happy Coding!
