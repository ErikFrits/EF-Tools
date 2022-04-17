# -*- coding: utf-8 -*-

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
#==================================================
from Autodesk.Revit.DB import BoundingBoxXYZ, XYZ




# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
#==================================================
def is_point_in_BB_2D(BB, p):
    # type:(BoundingBoxXYZ, XYZ) -> bool
    """ Function to determine if a point is located inside of a given BoundingBox in 2D space(XY).
    :param BB: BoundingBoxXYZ   - Bounding Box of a Revit element
    :param p:  XYZ              - Point
    :return:  bool              - True/False"""
    if BB.Min.X < p.X and BB.Min.Y < p.Y and BB.Max.X > p.X and BB.Max.Y > p.Y:
        return True
    return False