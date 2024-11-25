# -*- coding: utf-8 -*-
__title__ = "Select on sheets: DWGs"
__author__ = "Erik Frits"
__doc__ = """Version = 1.0
Date    = 07.07.2021
_____________________________________________________________________
Description:

Select DWG on selected sheets.
_____________________________________________________________________
How-to:

- Select sheets in ProjectBrowser menu
- Click the button
_____________________________________________________________________
Last update:
- [07.07.2021] - 1.0 RELEASE
_____________________________________________________________________
To-do:
-
_____________________________________________________________________
"""

#____________________________________________________________________ IMPORTS
import clr
clr.AddReference("System")
from System.Collections.Generic import List
from Autodesk.Revit.DB import (FilteredElementCollector,
                               ElementId,
                               ViewSheet,
                               BuiltInCategory,
                               ImportInstance)

#____________________________________________________________________ VARIABLES
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument


#____________________________________________________________________ MAIN
if __name__ == '__main__':
    # GET TITLEBLOCKS AND SELECTION
    all_ImportInstances = FilteredElementCollector(doc).OfClass(ImportInstance).WhereElementIsNotElementType().ToElements()
    selected_elements = uidoc.Selection.GetElementIds()

    # CONTAINER
    import_instances = []

    # LOOP THROUGH SELECTED ELEMENTS
    for element_id in selected_elements:
        element = doc.GetElement(element_id)

        # FILTER ONLY ViewSheet
        if type(element)!= ViewSheet:
            continue

        # FIND TITLE BLOCK ON SHEET
        for import_instance in all_ImportInstances:
            if import_instance.OwnerViewId == element_id:
                import_instances.append(import_instance.Id)

    # SET SELECTION IF TITLE BLOCKS FOUND
    if import_instances:
        uidoc.Selection.SetElementIds(List[ElementId](import_instances))