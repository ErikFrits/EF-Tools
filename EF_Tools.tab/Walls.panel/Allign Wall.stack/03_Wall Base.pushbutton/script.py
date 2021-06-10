# -*- coding: utf-8 -*-

__title__ = "Base Constraint"  # Name of the button displayed in Revit
__author__ = "Erik Frits"
# __helpurl__ = r"N:\2019_STANDARDS\04_PyRevit\RLP_Documentation\RLP_Autoupdate_SheetNumber.pdf"                  #Link for a PDF/URL that will be opened with F1 in revit when hovered over the icon.
__doc__ = """
Match Elements Base Constrain and Base Offset 

__Version__ = 0.9

Date: 21.10.2019
"""

from pyrevit import forms
import clr
from Autodesk.Revit import DB
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *
from pyrevit import revit
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application


class CustomISelectionFilter(ISelectionFilter):
    def __init__(self, nom_categorie):
        self.nom_categorie = nom_categorie

    def AllowElement(self, e):
        if str(e.Category.Id) == str(self.nom_categorie):
        #if e.Category.Name == "Walls"
            return True
        else:
            return False
    def AllowReference(self, ref, point):
        return true

# Select Wall
try:
    temp = uidoc.Selection.PickObject(ObjectType.Element, CustomISelectionFilter("-2000011"), "Select a Wall")    # -2000011 <- Id of OST_Walls
    Selected_wall = doc.GetElement(temp.ElementId)
except:
    forms.alert("Script is canceled.",exitscript=True,title="Script Canceled.")

# Get Properties
Wall_Parameter_Base_Constraint = Selected_wall.get_Parameter(DB.BuiltInParameter.WALL_BASE_CONSTRAINT)
Wall_Parameter_Base_Offset = Selected_wall.get_Parameter(DB.BuiltInParameter.WALL_BASE_OFFSET)

# Get Main Wall Parameters
Main_Base_Containt = Wall_Parameter_Base_Constraint.AsElementId()
Main_Base_Offset = Wall_Parameter_Base_Offset.AsDouble()

# Select Wall to match
with forms.WarningBar(title="Pick Wall to match base constrains:", handle_esc=True):
    while True:
        Match_wall = revit.pick_element()
        if not Match_wall:
            break
        t = Transaction(doc, 'Wall: Base constraints')
        t.Start()
        p1 = Match_wall.get_Parameter(DB.BuiltInParameter.WALL_BASE_OFFSET)
        p1.Set(Main_Base_Offset)

        p2 = Match_wall.get_Parameter(DB.BuiltInParameter.WALL_BASE_CONSTRAINT)
        p2.Set(Main_Base_Containt)
        t.Commit()
