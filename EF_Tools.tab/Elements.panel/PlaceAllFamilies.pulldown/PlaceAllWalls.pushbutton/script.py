# -*- coding: utf-8 -*-
__title__  = "Place WallTypes"
__author__ = "Erik Frits"


# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
#==================================================
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Structure import StructuralType
# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
#==================================================
doc         = __revit__.ActiveUIDocument.Document
uidoc       = __revit__.ActiveUIDocument

# Global Variables
active_view  = doc.ActiveView
active_level = active_view.GenLevel

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
#==================================================

#1️⃣ Get All WalLTypes
wall_types = FilteredElementCollector(doc).OfClass(WallType).ToElements()


#2️⃣ Define Start/End Points
pt_start = uidoc.Selection.PickPoint()
pt_end   = XYZ(pt_start.X + 10, pt_start.Y, pt_start.Z)
gap      = 1 #in feet
Y        = pt_start.Y


#🔓 Create Transaction to make changes
with Transaction(doc,'Create Wall Library') as t:
    t.Start()   #🔓

    for n, wall_type in enumerate(wall_types):
        #3️⃣ Adjust Y coordinate for equal spacing between walls
        Y -= wall_type.Width/2 + gap  # Apply the gap first

        #4️⃣ Create Line For Each Wall
        #          |   X      |   Y   |       Z   |
        start = XYZ(pt_start.X,   Y   , pt_start.Z )
        end   = XYZ(pt_end.X  ,   Y   , pt_end.Z   )
        line = Line.CreateBound(start, end)

        #5️⃣ Create Wall
        wall          = Wall.Create(doc, line, active_level.Id, False)
        wall.WallType = wall_type

        #6️⃣ Adjust Y coordinate by wall thickness
        Y -= wall_type.Width/2  # Subtract the wall thickness after placing it


        #7️⃣ Create TextNote with WallType Name
        wall_type_name = Element.Name.GetValue(wall_type)
        text_type_id   = doc.GetDefaultElementTypeId(ElementTypeGroup.TextNoteType)
        pt             = XYZ(end.X + gap, Y+wall_type.Width, end.Z)
        new_text       = TextNote.Create(doc, active_view.Id, pt, wall_type_name, text_type_id)



    t.Commit()  #🔒





#🔓 Create Transaction to make changes
with Transaction(doc,'Create a Wall') as t:
    t.Start()   #🔓

    active_level = active_view.GenLevel

    #1️⃣ Define Coordinates for the line
    start = XYZ(0 ,0,0)
    end   = XYZ(10,0,0)
    line = Line.CreateBound(start, end)

    #5️⃣ Create Wall
    wall          = Wall.Create(doc, line, active_level.Id, False)

    t.Commit()  #🔒












