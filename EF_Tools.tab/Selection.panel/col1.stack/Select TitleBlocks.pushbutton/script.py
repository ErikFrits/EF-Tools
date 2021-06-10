# -*- coding: utf-8 -*-
__title__ = "Select TitleBlocks"
__author__ = "Erik Frits"
__helpurl__ = ""
__highlight__ = 'updated'
__doc__ = """Version = 1.0
Date    = 08.12.2020
_____________________________________________________________________
Description:
Select title blocks on selected sheets.
_____________________________________________________________________
How-to:
- Select sheets in ProjectBrowser menu
- Click the button
_____________________________________________________________________
Prerequisite:
- Select sheets
_____________________________________________________________________
Last update:
- (20.04.2021) Refactored
_____________________________________________________________________
To-do:
- [ISSUE] - Selection valid only for a single change
_____________________________________________________________________
"""

# IMPORTS
from Autodesk.Revit.DB import FilteredElementCollector
import clr
clr.AddReference("System")
from System.Collections.Generic import List

# VARIABLES
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# MAIN
if __name__ == '__main__':
    # GET TITLEBLOCKS AND SELECTION
    all_TitleBlocks = FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_TitleBlocks).WhereElementIsNotElementType().ToElements()
    selected_elements = uidoc.Selection.GetElementIds()

    # GET TITLE BLOCKS
    title_blocks = []

    for element_id in selected_elements:
        element = doc.GetElement(element_id)

        # FILTER ONLY ViewSheet
        if type(element)!= ViewSheet:
            continue

        # FIND TITLE BLOCK ON SHEET
        for title_block in all_TitleBlocks:
            if title_block.OwnerViewId == sheet_id:
                title_blocks.append(title_block.Id)

    # SET SELECTION IF TITLE BLOCKS FOUND
    if title_blocks:
        uidoc.Selection.SetElementIds(List[ElementId](title_blocks))






