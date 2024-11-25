# -*- coding: utf-8 -*-
__title__   = "Split Regions with Region"
__doc__ = """Version = 1.0
Date    = 17.12.2023
_____________________________________________________________________
Description:
Split Selected FilledRegion with another Region.

💡 First Region will be cut!
_____________________________________________________________________
How-to:

-> Click on the button
-> Select Filled Region to cut
-> Select another Filled Region 
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


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
uidoc = __revit__.ActiveUIDocument
doc   = __revit__.ActiveUIDocument.Document #type: Document

from Autodesk.Revit.UI.Selection import Selection, ObjectType
selection = uidoc.Selection #type: Selection


# ╔═╗╦ ╦╔═╗╔╗╔╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║  ║║║ ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╚═╝╝╚╝ ╩ ╩╚═╝╝╚╝╚═╝
#==================================================
def find_top_face(solid):
    # Iterate through the faces of the solid
    for face in solid.Faces:
        if face.FaceNormal.IsAlmostEqualTo(XYZ.BasisZ):
            return face

# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝
#==================================================
class ISelectionFilter_Regions(ISelectionFilter):
    def AllowElement(self, element):
        if type(element) == FilledRegion:
            return True


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
#==================================================
#📦 Define Placeholders
cutting_region, selected_region = None, None

#1️⃣ Get Main Region
with forms.WarningBar(title='Pick Main Filled Region:'):
    try:
        ref_picked_object = selection.PickObject(ObjectType.Element, ISelectionFilter_Regions())
        selected_region   = doc.GetElement(ref_picked_object)

        if not selected_region:
            forms.alert("Main FileldRegion wasn't selected. Please Try Again.",exitscript=True)
    except:
        pass

#2️⃣ Get Cutting Region
with forms.WarningBar(title='Pick Cutting Filled Region:'):
    try:
        ref_picked_object = selection.PickObject(ObjectType.Element, ISelectionFilter_Regions())
        cutting_region    = doc.GetElement(ref_picked_object)

        if not cutting_region:
            forms.alert("Cutting FileldRegion wasn't selected. Please Try Again.",exitscript=True)
    except:
        import traceback
        print(traceback.format_exc())
        pass


#🎯 Modify Shape
t = Transaction(doc, 'EF_Split Region with Region')
t.Start()
try:
    #1️⃣ Create Shapes from Boundaries (random height)
    boundaries = selected_region.GetBoundaries()
    shape      = GeometryCreationUtilities.CreateExtrusionGeometry(boundaries, XYZ(0,0,1), 10) #10 - height

    boundaries_cut = cutting_region.GetBoundaries()
    shape_cut      = GeometryCreationUtilities.CreateExtrusionGeometry(boundaries_cut, XYZ(0,0,1), 10) #10 - height

    #2️⃣ Boolean Difference (Cut)
    new_shape = BooleanOperationsUtils.ExecuteBooleanOperation(shape, shape_cut, BooleanOperationsType.Difference)

    #🐍 Dev Part
    # # # Create DirectShape to visualize results
    # cat_id = ElementId(BuiltInCategory.OST_GenericModel)
    # ds1     = DirectShape.CreateElement(doc, cat_id)
    # ds1.SetShape([new_shape])

    #3️⃣ Get Top Face Outline
    top_face_1 = find_top_face(new_shape)
    outline_1  = top_face_1.GetEdgesAsCurveLoops()


    #4️⃣ Create FilledRegion from Face
    default_fr_id  = doc.GetDefaultElementTypeId(ElementTypeGroup.FilledRegionType)
    fr_id          = selected_region.GetTypeId()
    filled_region1 = FilledRegion.Create(doc, fr_id, doc.ActiveView.Id, outline_1)

    #5️⃣ Remove Initial FilledRegion
    if filled_region1:
        doc.Delete(selected_region.Id)

except:
    pass

t.Commit()