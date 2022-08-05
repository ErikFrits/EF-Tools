# -*- coding: utf-8 -*-
__title__ = "Find and Replace in ViewFilters"
__author__ = "Erik Frits"
__helpurl__ = ""
__doc__ = """Version = 1.0
Date    = 10.11.2020
_____________________________________________________________________
Description:

Rename multiple views at once with Find/Replace/Suffix/Prefix logic.
_____________________________________________________________________
How-to:

- Run the script
- Type Find/Replace/Prefix/Suffix as needed.
_____________________________________________________________________
Last update:

- [21.06.2022] - 1.0 RELESE
_____________________________________________________________________"""


#____________________________________________________________________ IMPORTS

from pyrevit import forms
from Autodesk.Revit.DB import *
from Autodesk.Revit.Exceptions import ArgumentException

# .NET IMPORTS
from clr import AddReference
AddReference("System")
from System.Diagnostics.Process import Start
from System.Windows.Window import DragMove
from System.Windows.Input import MouseButtonState

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document

#____________________________________________________________________ FUNCTIONS
def view_rename(selected_views, FIND, REPLACE, PREFIX, SUFFIX ):
    #type:(list,str,str,str,str) -> None
    """ Function to rename given views based on given criterias."""
    t = Transaction(doc, __title__)
    t.Start()
    for view in selected_views:

        # GENERATE NEW NAME
        view_new_name = PREFIX + view.Name.replace(FIND, REPLACE) + SUFFIX

        # [FAILSAVE] ENSURE THAT VIEW NAME IS UNIQUE BY ADDING <*> IF NEEDED.
        fail_count =0
        while fail_count < 10:
            fail_count += 1
            try:
                if view.Name != view_new_name:
                    view.Name = view_new_name
                    break
            except ArgumentException:
                view_new_name +=  "*"
            except:
                view_new_name += "_"
    t.Commit()

#____________________________________________________________________ GUI



#____________________________________________________________________ MAIN
filters_all = FilteredElementCollector(doc).OfClass(FilterElement).ToElements()
dict_filters = {i.Name : i for i in filters_all}

from GUI.forms import select_from_dict, FindReplace
selected_filters = select_from_dict(dict_filters, label='Select ViewFilters to rename.', SelectMultiple=True)

FR = FindReplace(__title__)

with Transaction(doc,__title__) as t:
    t.Start()

    for f in selected_filters:
        try:
            f.Name = FR.prefix + f.Name.replace(FR.find, FR.replace) + FR.suffix

        except:
            print('Failed to rename {}'.format(f.Name))
    t.Commit()
