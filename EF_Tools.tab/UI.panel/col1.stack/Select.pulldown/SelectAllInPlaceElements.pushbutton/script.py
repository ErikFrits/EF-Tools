# -*- coding: utf-8 -*-
__title__   = "Select all In-Place Elements in View"
__author__  = "Erik Frits"
__doc__ = """Version = 1.0
Select all In-Place Elements in the View.
_____________________________________________________________________
How-To:

Click on the button to update selection.
_____________________________________________________________________
Author: Erik Frits"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
from Autodesk.Revit.DB import *

#.NET Imports
import clr
clr.AddReference('System')
from System.Collections.Generic import List

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
#==================================================
def get_in_place_elements():
    """Get In-Place Elements in Active View."""
    collector = FilteredElementCollector(doc, doc.ActiveView.Id).OfClass(FamilyInstance).WhereElementIsNotElementType().ToElements()
    inplace_families = [x for x in collector if x.Symbol.Family.IsInPlace]
    return inplace_families

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#==================================================
if __name__ == '__main__':
    all_in_place     = get_in_place_elements()
    all_in_place_ids = [i.Id for i in all_in_place]

    # Modify Revit UI Selection
    new_selection = List[ElementId](all_in_place_ids)
    uidoc.Selection.SetElementIds(List[ElementId](new_selection))
