# -*- coding: utf-8 -*-
__title__       = "Hide Revision Clouds"
__author__      = "Erik Frits"
__doc__         = """
Version = 1.0
Date    = 18.01.2021
_____________________________________________________________________
Description:

This tool will find all clouds in the selected views.
It will group ungrouped clouds and switch off 'Issued' parameter if 
it is set to True because it prevents any modifications incl hiding

Then it will hide clouds on selected and all of its dependant views.
_____________________________________________________________________
How-to:


-> Select views in project browser before clicking on the button.
-> Run the script
_____________________________________________________________________
Last update:

- [29.07.2021] - 1.0 RELEASE
- [29.07.2021] - Group clouds if possible
- [29.07.2021] - set revision.Issued = False to be able to hide
- [29.07.2021] - Hide on dependant views too
_____________________________________________________________________
To-do:

- [Feature]    - Add select from List option if nothing selected.
- [Perfomance] - Improve speed. Try not get clouds from each View. 
                 Instead, get all clouds and create a dictionary 
                 with its related view. {view: clouds}
_____________________________________________________________________
Author: Erik Frits
"""

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> IMPORTS
from datetime import date
from Autodesk.Revit.DB import (FilteredElementCollector,
                               BuiltInCategory,
                               ElementId,
                               ViewPlan,
                               ViewSection,
                               View3D,
                               View,
                               ViewDrafting,
                               BuiltInParameter,
                               Transaction)
#>>>>>>>>>> .NET IMPORTS
from System.Collections.Generic import List

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VARIABLES
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> FUNCTIONS

def hide_clouds(view):

    #>>>>>>>>>>>>>>>>>>>> VERIFY VIEW TYPE
    if type(view)not in [ViewPlan, ViewSection, View3D, View, ViewDrafting]:
        return

    print("*** Hiding clouds - {} ***".format(view.Name))

    #>>>>>>>>>>>>>>>>>>>> Get all clouds on views
    all_clouds_on_view      = FilteredElementCollector(doc,view.Id).OfCategory(BuiltInCategory.OST_RevisionClouds).WhereElementIsNotElementType().ToElements() # Only visible clouds are found!
    clouds_to_group         = [i for i in all_clouds_on_view if     i.GroupId.Equals(ElementId.InvalidElementId)]           #NOT IN THE GROUP
    clouds_already_in_group = [i for i in all_clouds_on_view if not i.GroupId.Equals(ElementId.InvalidElementId)]           #IN THE GROUP
    clouds_issued           = [i for i in all_clouds_on_view if i.IsRevisionIssued()]

    #>>>>>>>>>>>>>>>>>>>> ISSUED = FALSE (OTHERWISE CANT HIDE IT)
    for i in clouds_issued:
        revision_id = i.RevisionId
        revision    = doc.GetElement(revision_id)
        revision.Issued = False
        print("{} - has been unissued to be able to hide it.".format(revision.Name))

    #>>>>>>>>>>>>>>>>>>>> CREATE A GROUP
    if clouds_to_group:
        #>>>>>>>>>> NEW GROUP NAME
        prefix          = 'Revision'
        today           = date.today().strftime("%Y_%m_%d")
        separator       = '_'
        new_group_name  = separator.join([prefix, view.Name, str(today)])

        #>>>>>>>>>> LIST OF CLOUDS
        clouds_to_group_ids  = [i.Id for i in clouds_to_group]
        List_clouds_to_group = List[ElementId](clouds_to_group_ids)

        #>>>>>>>>>> GROUP
        group               = doc.Create.NewGroup(List_clouds_to_group)
        group_type_param    = group.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM)
        group_type          = doc.GetElement(group_type_param.AsElementId())
        group_type.Name     = new_group_name
        print('------ New cloud group has been created - {}'.format(group.Name))

    #>>>>>>>>>>>>>>>>>>>> HIDE CLOUDS
    all_clouds = [i.Id for i in clouds_to_group + clouds_already_in_group]
    if all_clouds:
        view.HideElements(List[ElementId](all_clouds))

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> MAIN
if __name__ == '__main__':
    all_detail_groups = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_IOSDetailGroups).WhereElementIsNotElementType().ToElements()
    from Snippets._selection import get_selected_views
    selected_views = get_selected_views(uidoc, exit_if_none=True, title=__title__)
    if selected_views:
        t = Transaction(doc,__title__)
        t.Start()
        for view in selected_views:
            #>>>>>>>>>> SELECTED VIEW
            hide_clouds(view)

            #>>>>>>>>>>DEPENTANT VIEWS
            dependant_views= view.GetDependentViewIds()
            if dependant_views:
                for view_id in dependant_views:
                    view = doc.GetElement(view_id)
                    hide_clouds(view)
        t.Commit()
        print("Script is done.")