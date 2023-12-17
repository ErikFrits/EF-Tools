# -*- coding: utf-8 -*-
__title__   = "Split FilledRegion Boundaries"
__doc__ = """Version = 1.0
Date    = 17.12.2023
_____________________________________________________________________
Description:
Split Selected FilledRegion's Boundaries into separate Regions.
_____________________________________________________________________
How-to:

-> Click on the button
-> Select Filled Region to split
_____________________________________________________________________
Last update:
- [17.12.2023] - 1.0 RELEASE
_____________________________________________________________________
To-Do?:
- Keep Parameters?
_____________________________________________________________________
Author: Erik Frits"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *
from pyrevit import forms

# .NET Imports
import clr
clr.AddReference("System")
from System.Collections.Generic import List

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document #type: Document
app   = __revit__.Application

selection = uidoc.Selection #type: Selection


# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝
#==================================================
class ISelectionFilter_Regions(ISelectionFilter):
    def AllowElement(self, element):
        if type(element) == FilledRegion:
            boundaries = element.GetBoundaries()
            if len(boundaries) > 1:
                return True


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#==================================================
#📦 Define Placeholders
region = None

#1️⃣ Get Region
with forms.WarningBar(title='Pick Filled Region:'):
    try:
        ref_picked = selection.PickObject(ObjectType.Element, ISelectionFilter_Regions())
        region     = doc.GetElement(ref_picked)

        if not region:
            forms.alert("Multie-Boundary FileldRegion wasn't selected. Please Try Again.",exitscript=True)
    except:
        pass

region_type_id    = region.GetTypeId()

#🎯 Modify Shape
t = Transaction(doc, 'EF_Split FilledRegion Boundaries')
t.Start()

#2️⃣ Create Shape from Boundaries (random height)
boundaries = region.GetBoundaries()
for boundary in boundaries:
    try:
        outline = List[CurveLoop]([boundary])
        filled_region = FilledRegion.Create(doc, region_type_id, doc.ActiveView.Id, outline)
    except:
        pass

t.Commit()
