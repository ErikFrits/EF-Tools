# -*- coding: utf-8 -*-
__title__ = "Place All Doors"
__author__ = "Erik Frits"
__doc__ = """Version = 1.0
_____________________________________________________________________
Description:

_____________________________________________________________________
Author:  Erik Frits"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
#==================================================
from Autodesk.Revit.DB.Structure import StructuralType
from Autodesk.Revit.DB import *

#>>>>>>>>>> .NET IMPORTS
import clr
clr.AddReference("System")
from System.Collections.Generic import List

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
#==================================================
doc         = __revit__.ActiveUIDocument.Document
uidoc       = __revit__.ActiveUIDocument
active_level = doc.ActiveView.GenLevel


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
# Get All Door Families + Random Type
all_families  = FilteredElementCollector(doc).OfClass(Family).ToElements()
cats          =  [ElementId(BuiltInCategory.OST_Doors)]
all_door_fams = [f for f in all_families if f.FamilyCategory.Id in cats]  # Filter out Excl_Categories


# Get Start/End Points
distance = 10
start_point = uidoc.Selection.PickPoint()
end_point = XYZ(start_point.X + distance*(1+len(all_door_fams)),
                start_point.Y,
                start_point.Z)

tg = TransactionGroup(doc,'Create Door Library')
tg.Start()

# Create Wall
t = Transaction(doc, 'Create Wall')
t.Start()
geomLine = Line.CreateBound(start_point, end_point)
wall     = Wall.Create(doc, geomLine, active_level.Id, False)
t.Commit()


t2 = Transaction(doc, 'Place Doors')
t2.Start()
for n,door_fam in enumerate(all_door_fams):
    try:
        # Create Point
        pt = XYZ(start_point.X+(n+1)*distance,
                 start_point.Y,
                 start_point.Z)

        # Get Door Type
        symbols = [doc.GetElement(sym_id) for sym_id in door_fam.GetFamilySymbolIds()]
        random_symbol = symbols[0]

        # Check if Type is Activated
        if not random_symbol.IsActive:
            random_symbol.Activate()

        # Create Door
        door = doc.Create.NewFamilyInstance(pt, random_symbol, wall, active_level, StructuralType.NonStructural)
    except:
        pass
t2.Commit()

tg.Assimilate()
