# -*- coding: utf-8 -*-
__title__ = "Unhide All Elements in Active View"
__version__ = 'Version = 1.0'
__doc__ = """Version = 1.0
Date    = 15.09.2022
_____________________________________________________________________
Description:
Unhide all Elements in the active view
_____________________________________________________________________
Last update:
_____________________________________________________________________
To-Do:
_____________________________________________________________________
Author: Erik Frits"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ==================================================
from Autodesk.Revit.DB import *

# .NET Imports
import os, clr
clr.AddReference("System")
from System.Collections.Generic import List

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ==================================================
doc   = __revit__.ActiveUIDocument.Document

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
# ==================================================
if __name__ == '__main__':
    all_elements = FilteredElementCollector(doc).WhereElementIsNotElementType().ToElementIds()
    unhide_elements = List[ElementId](all_elements)

    with Transaction(doc,__title__) as t:
        t.Start()
        doc.ActiveView.UnhideElements(unhide_elements)
        t.Commit()