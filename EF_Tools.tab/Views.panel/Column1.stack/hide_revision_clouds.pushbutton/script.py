# -*- coding: utf-8 -*-

__title__       = "Hide Revision Clouds"   # Name of the button displayed in Revit
__author__      = "Erik Frits"
__highlight__   = ''
__doc__         = """
Version = 1.0
Date    = 18.01.2021
_____________________________________________________________________
Description:

This tool will find all clouds in the selected views.
It will group ungrouped clouds and switch off 'Issued' parameter if 
it is set to True and prevents any modifications.

Then it will hide clouds on primary and all of its dependant views.
_____________________________________________________________________
How-to:
Here is a guide on how to use the tool.
1.1) Select views in project browser before clicking on the button.
1.2) Select views from the menu if nothing was selected before.
It will do the rest.
_____________________________________________________________________
Prerequisite:

All requirements and things to be changed in the script should be 
described here.
_____________________________________________________________________
Last update:

- It creates groups for ungrouped clouds
- Switches off 'Issued' parameter
- Hides on primary and dependant views 
_____________________________________________________________________
To-do:
- Add a menu in a begining with a warning of how much time it might
take per view and that everyone is better to sync before running it
to avoid worksharing clashes.

- Code refactoring
- reduce imports
- Add select from List option if nothing selected.

- Improve speed. Trz not get clouds from each View. 
Instead Get all and create dictionary with its related view.
_____________________________________________________________________
"""

from pyrevit import forms
import clr
from Autodesk.Revit import DB
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *
from pyrevit import revit
import sys
from System.Collections.Generic import List
from datetime import date
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application




all_detail_groups = FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_IOSDetailGroups).WhereElementIsNotElementType().ToElements()
selected_views = uidoc.Selection.GetElementIds()

sys.path.append(r"N:\2019_STANDARDS\04_PyRevit\Extra")
from rlp_functions import script_for_admins_only
# script_for_admins_only()



def hide_clouds(view):
    print("[Hiding clouds] - " , view.Name)

    if type(view)!= ViewPlan and type(view)!= ViewSection and type(view)!= View3D:
        print('[Warning] - View with the name - {} [{}] has not been taken in the account because it is not in the list of supported plan types. Supported plans = [ViewPlan, ViewSection, View3D'.format(view.Name, view.Id))
        print(type(view))
        return False

    #Get all clouds on views
    all_clouds_on_view = FilteredElementCollector(doc,view_id).OfCategory(BuiltInCategory.OST_RevisionClouds).WhereElementIsNotElementType().ToElements() # Only visible clouds are found!

    clouds_to_group         = [i for i in all_clouds_on_view if  i.GroupId.Equals(ElementId.InvalidElementId)]           #NOT IN THE GROUP
    clouds_already_in_group = [i for i in all_clouds_on_view if not i.GroupId.Equals(ElementId.InvalidElementId)]       #IN THE GROUP


    clouds_issued = [i for i in all_clouds_on_view if i.IsRevisionIssued()]

    for i in clouds_issued:

        # set revision.Issued = False so it is possible to hide it.
        revision_id = i.RevisionId
        revision    = doc.GetElement(revision_id)
        revision.Issued = False
        print("{} - has been unissued to be able to hide it.".format(revision.Name))



    #CREATE GROUP

    #ICollection<ElementId> for clouds
    #group = document.Create.NewGroup(selectedIds)
    if clouds_to_group:
        clouds_to_group_ids = [i.Id for i in clouds_to_group]
        List_clouds_to_group = List[ElementId](clouds_to_group_ids)




        today = date.today().strftime("%Y_%m_%d")

        new_group_name = "W_" + view.Name + " - " + str(today)

        group = doc.Create.NewGroup(List_clouds_to_group)
        group_type_param = group.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM)
        group_type = doc.GetElement(group_type_param.AsElementId())
        group_type.Name = new_group_name

        print('Group created - {}'.format(group.Name))
    #HIDE CLOUDS

    all = [i.Id for i in clouds_to_group + clouds_already_in_group]
    if all:
        clouds_to_hide = List[ElementId](all)
        view.HideElements(clouds_to_hide)





t = Transaction(doc,"Py: Hide Clouds")
t.Start()

for view_id in selected_views:
    view = doc.GetElement(view_id)
    hide_clouds(view)
    #HIDE ON DEPENTANT VIEWS TOO
    dependant_views= view.GetDependentViewIds()
    if dependant_views:
        for view_id in dependant_views:
            view = doc.GetElement(view_id)
            hide_clouds(view)

t.Commit()
print("Script is done.")