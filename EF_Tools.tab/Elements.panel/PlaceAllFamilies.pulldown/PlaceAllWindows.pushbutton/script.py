# -*- coding: utf-8 -*-
__title__ = "Place All Windows"
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
import os, traceback
from Autodesk.Revit.DB import *
from pyrevit import forms

#>>>>>>>>>> .NET IMPORTS
import clr
clr.AddReference("System")
from System.Collections.Generic import List
from Autodesk.Revit.DB.Structure import StructuralType

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
#==================================================
doc         = __revit__.ActiveUIDocument.Document
uidoc       = __revit__.ActiveUIDocument
app         = __revit__.Application
rvt_year    = int(app.VersionNumber)
PATH_SCRIPT = os.path.dirname(__file__)
selection   = uidoc.Selection # type: Selection
active_level = doc.ActiveView.GenLevel



# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
# Get All Door Families + Random Type
all_families = FilteredElementCollector(doc).OfClass(Family).ToElements()
cats =  [ElementId(BuiltInCategory.OST_Windows)]
all_window_fams = [f for f in all_families if f.FamilyCategory.Id in cats]


# Get Start/End Points
distance = 10
start_point = uidoc.Selection.PickPoint()
end_point = XYZ(start_point.X + distance*(1+len(all_window_fams)),
                start_point.Y,
                start_point.Z)

tg = TransactionGroup(doc,'Create Window Library')
tg.Start()

# Create Wall
t = Transaction(doc, 'Create Wall')
t.Start()
geomLine = Line.CreateBound(start_point, end_point)
wall     = Wall.Create(doc, geomLine, active_level.Id, False)
t.Commit()


t2 = Transaction(doc, 'Place Windows')
t2.Start()
for n,window_fam in enumerate(all_window_fams):
    try:
        # Create Point
        pt = XYZ(start_point.X+(n+1)*distance,
                 start_point.Y,
                 start_point.Z)

        # Get Door Type
        symbols       = [doc.GetElement(sym_id) for sym_id in window_fam.GetFamilySymbolIds()]
        random_symbol = symbols[0]

        # Check if Type is Activated
        if not random_symbol.IsActive:
            random_symbol.Activate()

        # Create Door
        window = doc.Create.NewFamilyInstance(pt, random_symbol, wall, active_level, StructuralType.NonStructural)
    except:
        pass
t2.Commit()

tg.Assimilate()
