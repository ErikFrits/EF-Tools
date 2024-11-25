# -*- coding: utf-8 -*-

#Imports
from Autodesk.Revit.DB import XYZ
import math

# Functions

def rotate_vector(vector, rotation_rad):
    # pt_start = XYZ(BB.Min.X, (BB.Min.Y + BB.Max.Y) / 2, BB.Min.Z)
    # pt_end   = XYZ(BB.Max.X, (BB.Min.Y + BB.Max.Y) / 2, BB.Min.Z)
    # vector   = pt_end - pt_start
    # rotation = self.element.Location.Rotation


    # Get vector X,Y
    vector_x = vector.X
    vector_y = vector.Y

    # Apply Rotation
    rotated_x = vector_x * math.cos(rotation_rad) - vector_y * math.sin(rotation_rad)
    rotated_y = vector_x * math.sin(rotation_rad) + vector_y * math.cos(rotation_rad)
    rotated_z = vector.Z

    # Creating a new rotated vector
    return XYZ(rotated_x, rotated_y, rotated_z)
