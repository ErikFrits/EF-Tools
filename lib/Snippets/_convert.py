# -*- coding: utf-8 -*-

from Autodesk.Revit.DB import *

def convert_cm_to_feet(length):
    """Function to convert cm to feet."""
    return UnitUtils.Convert(length,
                           DisplayUnitType.DUT_CENTIMETERS,
                           DisplayUnitType.DUT_DECIMAL_FEET)


