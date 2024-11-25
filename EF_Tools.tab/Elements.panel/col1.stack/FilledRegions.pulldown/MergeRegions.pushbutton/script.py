# -*- coding: utf-8 -*-
__title__   = "Merge FilledRegion"
__doc__ = """Version = 1.0
Date    = 17.12.2023
_____________________________________________________________________
Description:
Merge Selected FilledRegions into one Region.
_____________________________________________________________________
How-to:

-> Click on the button
-> Select Filled Regions to merge
-> Click Finish in Top Left Corner
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
app   = __revit__.Application

selection = uidoc.Selection #type: Selection


# ╔═╗╦ ╦╔═╗╔╗╔╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║  ║║║ ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╚═╝╝╚╝ ╩ ╩╚═╝╝╚╝╚═╝
def find_top_faces(solid):
    """Find Top Faces of provided Solid"""
    faces = []
    for face in solid.Faces:
        if isinstance(face, CylindricalFace): # Skip cylindrical faces
            continue

        try:
            if face.FaceNormal.IsAlmostEqualTo(XYZ.BasisZ):
                faces.append(face)
        except:
            pass

    return faces

# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝

class ISelectionFilter_Regions(ISelectionFilter):
    def AllowElement(self, element):
        if type(element) == FilledRegion:
            return True

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
#==================================================
#📦 Define Placeholders
selected_regions = None

#1️⃣ Get FilledRegions
with forms.WarningBar(title='Pick Filled Region:'):
    try:
        ref_picked_objects = selection.PickObjects(ObjectType.Element, ISelectionFilter_Regions())
        selected_regions   = [doc.GetElement(ref) for ref in ref_picked_objects]

        if not selected_regions:
            forms.alert("FileldRegions weren't selected. Please Try Again.",exitscript=True)
    except:
        pass

#✅ Ensure more than 2 Elements
if not selected_regions or len(selected_regions) <2:
    forms.alert('You need to select at least 2 FilledRegions',exitscript=True)


#🎯 Modify Shape
t = Transaction(doc, 'EF_Merge FilledRegions')
t.Start()
try:
    shapes = []
    for region in selected_regions:
        #1️⃣ Create Shape from Boundaries (random height)
        boundaries = region.GetBoundaries()
        shape      = GeometryCreationUtilities.CreateExtrusionGeometry(boundaries, XYZ(0,0,1), 10) #10 - height
        shapes.append(shape)

    #2️⃣ Combine Shapes
    new_shape = shapes.pop()
    for n, shape in enumerate(shapes):
        new_shape = BooleanOperationsUtils.ExecuteBooleanOperation(new_shape, shape, BooleanOperationsType.Union)

    #🐍 Debug Test
    # # Create DirectShape to visualize results
    # cat_id = ElementId(BuiltInCategory.OST_GenericModel)
    # ds1     = DirectShape.CreateElement(doc, cat_id)
    # ds1.SetShape([new_shape])

    #🔝 Get Top Face
    top_faces     = find_top_faces(new_shape)
    final_outline = None

    for n, face in enumerate(top_faces):
        outline = face.GetEdgesAsCurveLoops()
        if n == 0:
            final_outline  = outline
            continue
        final_outline.AddRange(outline)

    #🟦 Create FilledRegion from Face
    fr_id             = selected_regions[0].GetTypeId()
    new_filled_region = FilledRegion.Create(doc, fr_id, doc.ActiveView.Id, final_outline)

    #🔥 Remove Original FilledRegions
    if new_filled_region:
        for region in selected_regions:
            doc.Delete(region.Id)

except:
    import traceback
    print(traceback.format_exc())

t.Commit()
