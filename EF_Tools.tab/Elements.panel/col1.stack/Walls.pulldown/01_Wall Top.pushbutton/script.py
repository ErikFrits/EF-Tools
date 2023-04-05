# -*- coding: utf-8 -*-

__title__ = "Wall Match: Top"
__author__ = "Erik Frits"
__doc__ = """Version = 1.0
Date    = 21.10.2019
_____________________________________________________________________
Description:

Match Wall: Top constraints
_____________________________________________________________________
How-to:

-> Run the script
-> Select the main wall
-> Select all the wall you would like to match to the main one 
_____________________________________________________________________
Last update:
- [18.07.2021] - V1.0 RELEASE
- [18.07.2021] - Refactored 
- [18.07.2021] - Optimized perfomance 
_____________________________________________________________________
To-do:
- 
_____________________________________________________________________
"""

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> IMPORTS
from pyrevit import forms, revit
from Autodesk.Revit.DB import (BuiltInParameter)
from Snippets._selection import pick_wall

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VARIABLES
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> MAIN
if __name__ == '__main__':

    #>>>>>>>>>> SELECT MAIN WALL
    try:    Selected_wall = pick_wall(uidoc)
    except: forms.alert("Script is canceled.",exitscript=True,title="Script Canceled.")

    #>>>>>>>>>> TOP
    Main_Top_Constraint     = Selected_wall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE)
    Main_Top_Constraint_Id  = Selected_wall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).AsElementId()
    Main_is_unconnected     = str(Main_Top_Constraint_Id) == "-1"  # True = Unconnected / False = Up to Level

    #>>>>>>>>>> BASE
    Main_Base_Containt  = Selected_wall.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT).AsElementId()
    Main_Base_Offset    = Selected_wall.get_Parameter(BuiltInParameter.WALL_BASE_OFFSET).AsDouble()

    #>>>>>>>>>> LOOP: SELECT MATCH WALL
    with forms.WarningBar(title="Pick Wall to match base constrains:", handle_esc=True):
        while True:

            #>>>>>>>>>> PICK WALL
            try:    Match_wall = pick_wall(uidoc)
            except: break
            if not Match_wall: break

            #>>>>>>>>>> SET PARAMETERS
            with revit.Transaction(__title__):

                Match_wall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).Set(Main_Top_Constraint_Id)

                #>>>>>>>>>> IF TOP CONSTRAINT: UNCONNECTED
                if Main_is_unconnected:

                    #>>>>>>>>>> MAIN WALL PARAMETERS
                    main_unconnected_height = Selected_wall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).AsDouble()
                    main_Z_Top = (Selected_wall.Location.Curve.Origin.Z) + main_unconnected_height + Main_Base_Offset

                    #>>>>>>>>>> MATCH WALL PARAMETERS
                    match_base_offset        = Match_wall.get_Parameter(BuiltInParameter.WALL_BASE_OFFSET).AsDouble()
                    match_unconnected_height = Match_wall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).AsDouble()
                    match_Z_Top              = (Match_wall.Location.Curve.Origin.Z + match_base_offset) + match_unconnected_height

                    #>>>>>>>>>> NEW UNCONNECTED HEIGHT
                    new_unconnected_height = match_unconnected_height + main_Z_Top - match_Z_Top
                    Match_wall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).Set(new_unconnected_height)

                #>>>>>>>>>> IF TOP CONSTRAINT: LEVEL
                else:
                    Main_Top_Offset = Selected_wall.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET).AsDouble()
                    Match_wall.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET).Set(Main_Top_Offset)