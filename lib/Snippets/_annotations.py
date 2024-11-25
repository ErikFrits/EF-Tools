# -*- coding: utf-8 -*-

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#====================================================================================================
from Autodesk.Revit.DB import *
from pyrevit import forms

# CUSTOM IMPORTS
from Snippets._convert import convert_cm_to_feet
from Snippets._filtered_element_collector import all_legends

#>>>>>>>>>> .NET IMPORTS
import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System")
from System.Collections.Generic import List




# ╔═╗╔╗╔╔╗╔╔═╗╔╦╗╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠═╣║║║║║║║ ║ ║ ╠═╣ ║ ║║ ║║║║╚═╗
# ╩ ╩╝╚╝╝╚╝╚═╝ ╩ ╩ ╩ ╩ ╩╚═╝╝╚╝╚═╝ ANNOTATIONS
#==================================================
def create_text_note(doc, view, x ,y ,text, text_note_type, bold=False):
    #type:(Document, View, float, float, str, ElementId) -> TextNote
    """Function to create a TextNote.
    :param doc:             Revit Document
    :param view:            View
    :param x:               Position Coordinate X
    :param y:               Position Coordinate Y
    :param text:            TextNote Content
    :param text_note_type:  text_note_type
    :return:                TextNote"""
    text = '-' if not text else text
    # TEXTNOTE
    text_note = TextNote.Create(doc, view.Id, XYZ(x, y, 0),text, text_note_type.Id)

    if bold:
        formatted_text = FormattedText(text)
        formatted_text.SetBoldStatus(True)
        text_note.SetFormattedText(formatted_text)
    return text_note





def create_region(doc, view, X, Y, region_width=120.0, region_height=60.0):
    #type:(Document, View, float, float, float, float) -> FilledRegion
    """Function to create a FilledRegion.
    :param doc:                 Revit Document
    :param view:                View
    :param X:                   Bottom Left Corner - X
    :param Y:                   Bottom Left Corner - Y
    :param region_width:        FilledRegion width in FEET
    :param region_height:       FilledRegion height in FEET
    :return:                    FilledRegion"""
    # VARIABLES
    region_type_id = doc.GetDefaultElementTypeId(ElementTypeGroup.FilledRegionType)

    # CONTAINER
    elements_line_text = []

    # REGION POINTS
    points_0 = XYZ(X, Y, 0.0)
    points_1 = XYZ(X+region_width, Y, 0.0)
    points_2 = XYZ(X+region_width, Y-region_height, 0.0)
    points_3 = XYZ(X, Y-region_height, 0.0)
    points = [points_0, points_1, points_2, points_3, points_0]

    # CREATE BOUNDARY
    list_boundary = List[CurveLoop]()
    boundary = CurveLoop()

    for n, point in enumerate(points):
        if n == 4: break
        # LINE POINTS
        p1, p2 = points[n], points[n + 1]
        # LINE
        boundary.Append(Line.CreateBound(p1, p2))
    list_boundary.Add(boundary)

    filled_region = FilledRegion.Create(doc, region_type_id, view.Id, list_boundary)
    return filled_region

def create_horizontal_line(doc, view, X, Y, line_width_feet, scale = 100):
    #type:(Document, View, float, float, float, float)  -> DetailCurve
    """:param doc:                 Revit Document
    :param view:                View where to draw
    :param X:                   X - Coordinate
    :param Y:                   Y - Coordinate
    :param line_width_feet:     Line Width in feet
    :param scale:               View Scale?
    :return:                    DetailCurve"""

    # VARIABLES
    line_width      = line_width_feet / 100

    # CREATE LINE DEFAULT ELEMENTS
    line_constructor = Line.CreateBound(XYZ(X, Y, 0), XYZ(X+line_width_feet, Y, 0))
    line = doc.Create.NewDetailCurve(view, line_constructor)


    return line
