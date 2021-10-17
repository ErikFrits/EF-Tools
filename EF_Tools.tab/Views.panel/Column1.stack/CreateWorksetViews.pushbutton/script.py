# -*- coding: utf-8 -*-
__title__ = "Create 3D Views: Worksets"   # Name of the button displayed in Revit
__author__ = "Erik Frits"
__doc__ = """Version = 1.0
Date    = 12.08.2021
_____________________________________________________________________
Description:

Create 3D View for each workset and isolate its elements.
If view already exists then it skips it. 
If you want to update views that it has produced earlier, 
please delete them and re-run the script.
_____________________________________________________________________
How-to:

-> Run the script
-> It will create 3D views for each Workset
ViewNaming:  'Py_(Workset.Name)'

_____________________________________________________________________
Last update:

- [12.08.2021] - 1.0 RELEASE
_____________________________________________________________________
"""

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> IMPORTS
from Autodesk.Revit.DB import  (View3D ,FilteredWorksetCollector, WorksetKind, WorksetVisibility,ViewFamilyType, FilteredElementCollector,
                                Transaction, SubTransaction, BuiltInParameter)
import sys

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VARIABLES
doc   = __revit__.ActiveUIDocument.Document

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> MAIN
if __name__ == '__main__':

    t = Transaction(doc, __title__)
    t.Start()

    #>>>>>>>>>>>>>>>>>>>> GET WORKSETS
    all_worksets = FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset).ToWorksets() #ToWorksets #ToWorksets()
    if not all_worksets:
        print("No Worksets found in the current project.")
        sys.exit()

    #>>>>>>>>>>>>>>>>>>>> LOOP THROUGH WORKSETS
    print("CREATING WORKSETS: ")
    for Workset in all_worksets:
        workset_name = Workset.Name

        #>>>>>>>>>> GET 3D VIEW TYPE
        all_view_types = FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements()
        view_type_3D = None
        for view_type in all_view_types:
            if '3D' in view_type.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString():
                view_type_3D = view_type
                break

        #>>>>>>>>>> CREATE 3D VIEW
        st = SubTransaction(doc)
        st.Start()

        view = View3D.CreateIsometric(doc, view_type_3D.Id)
        view_new_name = "Py_{}".format(Workset.Name)

        try:
            view.Name = view_new_name
            print("--- Workset 3DView created: {}".format(view_new_name))

        except:
            st.RollBack()
            print("--- Workset 3DView already exists: {}".format(view_new_name))
            continue
        st.Commit()

        #>>>>>>>>>> SET WORKSET VISIBILITIES
        for workset in all_worksets:
            if workset.Name == Workset.Name:
                view.SetWorksetVisibility(workset.Id, WorksetVisibility.Visible)
            else:
                view.SetWorksetVisibility(workset.Id, WorksetVisibility.Hidden)
    t.Commit()

