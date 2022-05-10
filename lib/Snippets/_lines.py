# -*- coding: utf-8 -*-

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
#==================================================
from Autodesk.Revit.DB import *


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
uidoc   = __revit__.ActiveUIDocument
app     = __revit__.Application
doc     = __revit__.ActiveUIDocument.Document

active_view_id      = doc.ActiveView.Id
active_view         = doc.GetElement(active_view_id)
active_view_level   = active_view.GenLevel

# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
#==================================================

def get_points_along_a_curve(curve, step=0.3):
    """ Function to get points along given Curve
    :param curve: Curve that will be tessellated.
    :param step:  approx. Step distance between points
    :return: list of Points along the curve."""

    # CONTAINER
    points = []

    # GET POINTS ALONG CURVE
    tessellation = curve.Tessellate()
    dist = 0

    pt = curve.GetEndPoint(0)
    for q in tessellation:

        if not points:
            points.append(pt)
            dist = 0.0

        else:
            dist += pt.DistanceTo(q)
            if dist >= step:
                points.append(q)
                dist = 0
        pt = q

    return points



def get_line_styles(uidoc):
    """Function to get available LineStyles for DetaiLines.
    It will create a temporary DetailLine to get LineStyles to prevent having issues
    in a project without lines.

    !IMPORTANT This function has to be run outside of any transactions!

    :return: list of Available LineStyles"""

    # CREATE TEMP LINE
    with Transaction(doc, "temp - Create DetailLine") as t:
        t.Start()
        new_line         = Line.CreateBound(XYZ(0,0,0), XYZ(1,1,0))
        random_line      = uidoc.Document.Create.NewDetailCurve(active_view, new_line)
        line_styles_ids  = random_line.GetLineStyleIds()
        t.RollBack()
    line_styles = [doc.GetElement(line_style) for line_style in line_styles_ids]
    return line_styles