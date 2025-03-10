# -*- coding: utf-8 -*-
__title__  = "Line To Dimensions"
__author__ = "Erik Frits"

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import ObjectType


def select_line_and_create_dimensions(doc, uidoc):
    # Step 1: Select a line in the document
    sel = uidoc.Selection
    ref = sel.PickObject(ObjectType.Element, "Select a model line.")
    line_element = doc.GetElement(ref)

    # Step 2: Get the curve of the selected line
    curve = line_element.GeometryCurve

    # Step 3: Find all intersecting walls
    wall_refs = []
    walls = FilteredElementCollector(doc).OfClass(Wall).ToElements()

    for wall in walls:
        wall_location_curve = wall.Location.Curve
        if wall_location_curve.Intersect(curve) == SetComparisonResult.Overlap:
            wall_refs.extend(get_wall_outer_faces(wall))

    # Step 4: Create the dimension line
    if wall_refs:
        with Transaction(doc, "Create Dimension Line") as t:
            t.Start()
            dim_line = Line.CreateBound(curve.GetEndPoint(0), curve.GetEndPoint(1))
            doc.Create.NewDimension(doc.ActiveView, dim_line, ReferenceArray(wall_refs))
            t.Commit()


def get_wall_outer_faces(wall):
    # Helper function to get references to the outer faces of a wall
    opt = Options()
    opt.ComputeReferences = True
    opt.IncludeNonVisibleObjects = True
    geometry = wall.get_Geometry(opt)

    references = []
    for geomObj in geometry:
        solid = geomObj as Solid
        if solid:
            for face in solid.Faces:
                normal = face.FaceNormal
                if abs(normal.Y) > 0.5:  # assuming exterior faces are in the Y direction
                    references.append(face.Reference)
                    break
    return references


# Run the tool
select_line_and_create_dimensions(doc, uidoc)
