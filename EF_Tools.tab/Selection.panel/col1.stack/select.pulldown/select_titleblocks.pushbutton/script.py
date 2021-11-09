# -*- coding: utf-8 -*-
__title__ = "Select on sheets: TitleBlocks"
__author__ = "Erik Frits"
__doc__ = """Version = 1.2
Date    = 08.12.2020
_____________________________________________________________________
Description:

Select title blocks on selected sheets.
_____________________________________________________________________
How-to:

- Select sheets in ProjectBrowser menu
- Click the button
_____________________________________________________________________
Last update:
- [10.06.2021] - 1.2 RELEASE
- [10.06.2021] - Refactired
_____________________________________________________________________
To-do:
- [BUG] - Selection valid only for a single change in titleblocks.
- [TO-DO] - add __helpurl__ for blog post
_____________________________________________________________________
"""

#____________________________________________________________________ IMPORTS
import clr
clr.AddReference("System")
from System.Collections.Generic import List
from Autodesk.Revit.DB import (FilteredElementCollector,
                               ElementId,
                               ViewSheet,
                               BuiltInCategory)

#____________________________________________________________________ VARIABLES
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

#____________________________________________________________________ MAIN
if __name__ == '__main__':
    # GET TITLEBLOCKS AND SELECTION
    all_TitleBlocks = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_TitleBlocks).WhereElementIsNotElementType().ToElements()
    selected_elements = uidoc.Selection.GetElementIds()

    # CONTAINER
    title_blocks = []

    # LOOP THROUGH SELECTED ELEMENTS
    for element_id in selected_elements:
        element = doc.GetElement(element_id)

        # FILTER ONLY ViewSheet
        if type(element)!= ViewSheet:
            continue

        # FIND TITLE BLOCK ON SHEET
        for title_block in all_TitleBlocks:
            if title_block.OwnerViewId == element_id:
                title_blocks.append(title_block.Id)

    # SET SELECTION IF TITLE BLOCKS FOUND
    if title_blocks:
        uidoc.Selection.SetElementIds(List[ElementId](title_blocks))


