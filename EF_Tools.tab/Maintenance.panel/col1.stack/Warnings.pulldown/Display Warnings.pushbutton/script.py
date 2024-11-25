# -*- coding: utf-8 -*-
__title__ = "Display Warnings by User"
__version__ = 'Version = 1.0'
__doc__ = """Version = 1.0
Date    = 15.09.2022
_____________________________________________________________________
Description:
...
_____________________________________________________________________
Last update:
- [08.04.2024] - V1.0 RELEASE
_____________________________________________________________________
To-Do:
- ...
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
output = script.get_output()
app    = __revit__.Application

# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
# ==================================================

def get_sorted_warnings():
    """Function to get All Warnings in the project and sort them by their description
    :return: dict of warnings {warn_description : list_of_warnings}"""

    dict_all_warnings = defaultdict(list)
    for w in doc.GetWarnings():
        description = w.GetDescriptionText()
        dict_all_warnings[description].append(w)
    return dict_all_warnings



# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
# ==================================================

# Get + Sort Warnings
dict_all_warnings = get_sorted_warnings()


from GUI.forms import select_from_dict


selected_warnings = select_from_dict(dict_all_warnings, title = __title__, SelectMultiple=True)
print(selected_warnings)

for descr, list_warnings in dict_all_warnings.items():
    table_data = []

    for warn in list_warnings:
        element_ids      = list(warn.GetFailingElements()) + list(warn.GetAdditionalElements())
        last_modified_by = {WorksharingUtils.GetWorksharingTooltipInfo(doc, el_id).LastChangedBy for el_id in element_ids}
        last_modified_by = ', '.join(last_modified_by)

        # Linkify
        title = 'Select'
        warn_linkify = output.linkify(element_ids, title)

        # Create a Row of Data
        row = [descr, last_modified_by, str(len(element_ids)), warn_linkify]
        table_data.append(row)
    output.print_table(table_data=table_data,
                       title  =descr,
                       columns=['Warning Description', 'Last Modified By:', 'Elements', 'Linkify'],
                       formats=['**{}**', '*{}*', '', ''])

