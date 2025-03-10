# -*- coding: utf-8 -*-
__title__ = "Place All DetailComponents"
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
all_families       = FilteredElementCollector(doc).OfClass(Family).ToElements()
cats               =  [ElementId(BuiltInCategory.OST_DetailComponents)]
all_detail_el_fams = [f for f in all_families if f.FamilyCategory.Id in cats]
all_detail_el_fams = sorted(all_detail_el_fams, key= lambda i:i.Name) #Sort

# Get Start/End Points
distance = 10
start_point = uidoc.Selection.PickPoint()


tg = TransactionGroup(doc,'Create Window Library')
tg.Start()



t2 = Transaction(doc, 'Place Detail Components')
t2.Start()
for n,detail_el_fam in enumerate(all_detail_el_fams):
    try:
        # Create Point
        pt = XYZ(start_point.X,
                 start_point.Y-(n+1)*distance,
                 start_point.Z)


        pt_text = XYZ(pt.X+5, pt.Y, pt.Z)

        typeId = doc.GetDefaultElementTypeId(ElementTypeGroup.TextNoteType)
        TextNote.Create(doc, doc.ActiveView.Id, pt_text, detail_el_fam.Name, typeId)


        # Get Door Type
        symbols       = [doc.GetElement(sym_id) for sym_id in detail_el_fam.GetFamilySymbolIds()]
        random_symbol = symbols[0]

        # Check if Type is Activated
        if not random_symbol.IsActive:
            random_symbol.Activate()

        # Create Door
        detail_el = doc.Create.NewFamilyInstance(pt, random_symbol, doc.ActiveView)
    except:
        import traceback
        print(traceback.format_exc())
        pass
    
t2.Commit()

tg.Assimilate()
