# -*- coding: utf-8 -*-

__title__ = "Top Constraint"  # Name of the button displayed in Revit
__author__ = "Erik Frits"
# __helpurl__ = r"N:\2019_STANDARDS\04_PyRevit\RLP_Documentation\RLP_Autoupdate_SheetNumber.pdf"                  #Link for a PDF/URL that will be opened with F1 in revit when hovered over the icon.
__doc__ = """
Match Elements Base Constrain and Base Offset 

__Version__ = 0.9

Date: 21.10.2019"""

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

# TOP CONSTRAINT
Main_Top_Constraint = Selected_wall.get_Parameter(DB.BuiltInParameter.WALL_HEIGHT_TYPE)
Main_Top_Constraint_Id = Selected_wall.get_Parameter(DB.BuiltInParameter.WALL_HEIGHT_TYPE).AsElementId()


#Unconnected_____________________________________________________________________________________________________________
if str(Main_Top_Constraint_Id) == "-1":     # True = Unconnected / False = Up to Level

    Main_Base_Offset = Selected_wall.get_Parameter(DB.BuiltInParameter.WALL_BASE_OFFSET).AsDouble()
    Wall_Parameter_Unconnected_Height   = Selected_wall.get_Parameter(DB.BuiltInParameter.WALL_USER_HEIGHT_PARAM)
    Main_Unconnected_Height = Wall_Parameter_Unconnected_Height.AsDouble()
    main_Z_Top = (Selected_wall.Location.Curve.Origin.Z) + Main_Unconnected_Height + Main_Base_Offset

# Select Wall to match
    with forms.WarningBar(title="Pick Wall to match base constrains:", handle_esc=True):
        while True:
            Match_wall = revit.pick_element()
            if not Match_wall:
                break

            Match_Base_Offset = Match_wall.get_Parameter(DB.BuiltInParameter.WALL_BASE_OFFSET).AsDouble()
            Wall_Parameter_Unconnected_Height = Match_wall.get_Parameter(DB.BuiltInParameter.WALL_USER_HEIGHT_PARAM)
            Match_Unconnected_Height = Wall_Parameter_Unconnected_Height.AsDouble()
            match_Z_Top = (Match_wall.Location.Curve.Origin.Z +Match_Base_Offset) + Match_Unconnected_Height
            Difference_Value =  Match_Unconnected_Height + main_Z_Top - match_Z_Top

            t = Transaction(doc, 'Wall: Top constraints')
            t.Start()
            #Set Top Constraint
            p1 = Match_wall.get_Parameter(DB.BuiltInParameter.WALL_HEIGHT_TYPE)
            p1.Set(Main_Top_Constraint_Id)

            #Set Unconnected Height
            p2 = Match_wall.get_Parameter(DB.BuiltInParameter.WALL_USER_HEIGHT_PARAM)
            p2.Set(Difference_Value)
            t.Commit()

#Up to level_____________________________________________________________________________________________________________
else:
    Main_Top_Offset = Selected_wall.get_Parameter(DB.BuiltInParameter.WALL_TOP_OFFSET).AsDouble()

    # Select Wall to match
    with forms.WarningBar(title="Pick Wall to match base constrains:", handle_esc=True):
        while True:
            Match_wall = revit.pick_element()
            if not Match_wall:
                break
            t = Transaction(doc, 'Wall: Top constraints')
            t.Start()
            p1 = Match_wall.get_Parameter(DB.BuiltInParameter.WALL_HEIGHT_TYPE)
            p1.Set(Main_Top_Constraint_Id)
            p2 = Match_wall.get_Parameter(DB.BuiltInParameter.WALL_TOP_OFFSET)
            p2.Set(Main_Top_Offset)
            t.Commit()

