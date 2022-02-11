# -*- coding: utf-8 -*-

from Autodesk.Revit.DB import *
app   = __revit__.Application
from Autodesk.Revit.DB import UnitUtils

def convert_cm_to_feet(length):
    """Function to convert cm to feet."""
    rvt_year = int(app.VersionNumber)

    # RVT >= 2022
    if rvt_year < 2022:
        from Autodesk.Revit.DB import DisplayUnitType
        return UnitUtils.Convert(length,
                                DisplayUnitType.DUT_CENTIMETERS,
                                DisplayUnitType.DUT_DECIMAL_FEET)
    # RVT >= 2022
    else:
        from Autodesk.Revit.DB import UnitTypeId
        return UnitUtils.ConvertToInternalUnits(length, UnitTypeId.Centimeters)

def convert_m_to_feet(length):
    """Function to convert cm to feet."""
    rvt_year = int(app.VersionNumber)

    # RVT >= 2022
    if rvt_year < 2022:
        from Autodesk.Revit.DB import DisplayUnitType
        return UnitUtils.Convert(length,
                                 DisplayUnitType.DUT_METERS,
                                 DisplayUnitType.DUT_DECIMAL_FEET)
    # RVT >= 2022
    else:
        from Autodesk.Revit.DB import UnitTypeId
        return UnitUtils.ConvertToInternalUnits(length, UnitTypeId.Meters)
