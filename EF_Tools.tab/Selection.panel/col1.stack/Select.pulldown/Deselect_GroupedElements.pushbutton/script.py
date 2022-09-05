# -*- coding: utf-8 -*-
__title__ = "Deselect Grouped Elements"
__author__ = "Erik Frits"
__doc__ = """Version = 1.0
Date    = 220325
_____________________________________________________________________
Description:

Remove elements that are part of the group from current selection.

_____________________________________________________________________
How-to:

- Select elements
- Click the button
- It will deselect elements that are in groups
_____________________________________________________________________
Last update:
- [25.03.2022] - 1.0 RELEASE
_____________________________________________________________________
To-do:
- 
_____________________________________________________________________
"""

#____________________________________________________________________ IMPORTS
import clr
clr.AddReference("System")
from System.Collections.Generic import List
from Autodesk.Revit.DB import ElementId



#____________________________________________________________________ VARIABLES
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

#____________________________________________________________________ MAIN
if __name__ == '__main__':
    # FILTERED CONTAINER
    new_selection = []

    # GET CURRENT SELECTION
    selected_elements_ids = uidoc.Selection.GetElementIds()
    selected_elements = [doc.GetElement(id) for id in selected_elements_ids]

    # REMOVE ELEMENTS THAT ARE IN GROUPS
    for elem in selected_elements:
        if elem.GroupId == ElementId(-1):
            new_selection.append(elem.Id)

    # CHANGE SELECTION
    uidoc.Selection.SetElementIds(List[ElementId](new_selection))

