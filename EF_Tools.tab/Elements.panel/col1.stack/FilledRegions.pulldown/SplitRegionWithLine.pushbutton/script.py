# -*- coding: utf-8 -*-
__title__   = "Split Regions with Line"
__doc__ = """Version = 1.1
Date    = 17.12.2023
_____________________________________________________________________
Description:
Split Selected FilledRegions with a Detail Line.

💡 Detail Line will be used to create an infinite plane!
_____________________________________________________________________
How-to:

-> Click on the button
-> Select Filled Regions
-> Select DetailLine
_____________________________________________________________________
Last update:
- [12.01.2024] - 1.1 Minor Selection Bug Fixed
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
#==================================================
def mirror_plane(plane):
    # Get the origin and normal of the original plane
    origin = plane.Origin
    normal = plane.Normal

    # Mirror the normal by reversing its direction
    mirrored_normal = XYZ(-normal.X, -normal.Y, -normal.Z)

    # Create a new mirrored plane with the same origin and mirrored normal
    mirrored_plane = Plane.CreateByNormalAndOrigin(mirrored_normal, origin)
    return mirrored_plane


def find_top_face(solid):
    # Iterate through the faces of the solid
    for face in solid.Faces:
        if face.FaceNormal.IsAlmostEqualTo(XYZ.BasisZ):
            return face


def create_plane_from_line(line):
    '''Create Infinite Plane from Line'''
    crv = line.Location.Curve
    pt_start = crv.GetEndPoint(0)
    pt_end   = crv.GetEndPoint(1)
    pt_mid   = (pt_start + pt_end) / 2
    pt_mid   = XYZ(pt_mid.X, pt_mid.Y, pt_mid.Z + 10)
    plane    = Plane.CreateByThreePoints(pt_start, pt_end, pt_mid)
    return plane

# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝
#==================================================
class ISelectionFilter_Regions(ISelectionFilter):
    def AllowElement(self, element):
        if type(element) == FilledRegion:
            return True


class ISelectionFilter_DetailLine(ISelectionFilter):
    def AllowElement(self, element):
        if type(element) == DetailLine:
            return True


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
#==================================================
#📦 Define Placeholders
selected_line    = None
selected_regions = None

#1️⃣ Get FilledRegions
with forms.WarningBar(title='Pick Filled Region:'):
    try:
        ref_picked_objects = selection.PickObjects(ObjectType.Element, ISelectionFilter_Regions())
        selected_regions   = [doc.GetElement(ref) for ref in ref_picked_objects]
    except:
        pass


#2️⃣ Get DetailLine
with forms.WarningBar(title='Pick Detail Line:'):
    try:
        ref_picked_object   = selection.PickObject(ObjectType.Element, ISelectionFilter_DetailLine())
        selected_line       = doc.GetElement(ref_picked_object)
    except:
        pass

# Check if elements were selected
if not selected_regions:
    forms.alert("FileldRegions weren't selected. Please Try Again.",exitscript=True)

if not selected_line:
    forms.alert("Detail Line wasn't selected. Please Try Again.", exitscript=True)


#3️⃣ Create Plane from Line (By 3 Points)
plane = create_plane_from_line(selected_line)


#✅ Ensure Elements
if not selected_line or not selected_regions:
    forms.alert('Select Region and Line.', exitscript=True)


#🎯 Modify Shape
t = Transaction(doc, 'EF_Split Regions with Line')
t.Start()

for region in selected_regions:
    try:
        #📦 Create Shape from Boundaries (random height)
        boundaries = region.GetBoundaries()
        shape      = GeometryCreationUtilities.CreateExtrusionGeometry(boundaries, XYZ(0,0,1), 10) #10 - height

        #✂ Split Solid with Plane (In both directions)
        new_shape_1 = BooleanOperationsUtils.CutWithHalfSpace(shape, plane)
        new_shape_2 = BooleanOperationsUtils.CutWithHalfSpace(shape, mirror_plane(plane))

        #🔝 Get Top Faces of new Geometries
        top_face_1 = find_top_face(new_shape_1)
        top_face_2 = find_top_face(new_shape_2)

        #🔲 Get Top Face Outlines
        outline_1 = top_face_1.GetEdgesAsCurveLoops()
        outline_2 = top_face_2.GetEdgesAsCurveLoops()

        #🔵 Get Filled Region Type
        fr_id = region.GetTypeId()

        #✅ Create new FilledRegions
        filled_region1 = FilledRegion.Create(doc, fr_id, doc.ActiveView.Id, outline_1)
        filled_region2 = FilledRegion.Create(doc, fr_id, doc.ActiveView.Id, outline_2)

        #🔥 Delete Old Filled Region
        if filled_region1 and filled_region2:
            doc.Delete(region.Id)

        # # Create DirectShape to visualize results
        # cat_id = ElementId(BuiltInCategory.OST_GenericModel)
        # ds1     = DirectShape.CreateElement(doc, cat_id)
        # ds1.SetShape([new_shape_1])
        #
        # ds2     = DirectShape.CreateElement(doc, cat_id)
        # ds2.SetShape([new_shape_2])
    except:
        pass
t.Commit()
