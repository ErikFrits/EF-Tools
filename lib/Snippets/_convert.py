# -*- coding: utf-8 -*-
# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ==================================================
from Autodesk.Revit.DB import *

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ==================================================
app      = __revit__.Application
rvt_year = int(app.VersionNumber)


# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
# ==================================================
def convert_internal_units(value, get_internal = True, units='m'):
    #type: (float, bool, str) -> float
    """Function to convert Internal units to meters or vice versa.
    :param value:        Value to convert
    :param get_internal: True to get internal units, False to get Meters
    :param units:        Select desired Units: ['m', 'm2']
    :return:             Length in Internal units or Meters."""

    if rvt_year >= 2021:
        from Autodesk.Revit.DB import UnitTypeId
        if   units == 'm' : units = UnitTypeId.Meters
        elif units == "m2": units = UnitTypeId.SquareMeters
        elif units == 'cm': units = UnitTypeId.Centimeters
    else:
        from Autodesk.Revit.DB import DisplayUnitType
        if   units == 'm' : units = DisplayUnitType.DUT_METERS
        elif units == "m2": units = DisplayUnitType.DUT_SQUARE_METERS
        elif units == "cm": units = DisplayUnitType.DUT_CENTIMETERS

    if get_internal:
        return UnitUtils.ConvertToInternalUnits(value, units)
    return UnitUtils.ConvertFromInternalUnits(value, units)




















# ╔═╗╔╗ ╔═╗╔═╗╦  ╔═╗╔╦╗╔═╗
# ║ ║╠╩╗╚═╗║ ║║  ║╣  ║ ║╣
# ╚═╝╚═╝╚═╝╚═╝╩═╝╚═╝ ╩ ╚═╝ OBSOLETE ( still need to refactor the code)
def convert_cm_to_feet(length):
    """Function to convert cm to feet."""

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



def convert_internal_to_m(length):
    """Function to convert internal to meters."""

    # RVT >= 2022
    if rvt_year < 2022:
        from Autodesk.Revit.DB import DisplayUnitType
        return UnitUtils.Convert(length,
                                 DisplayUnitType.DUT_DECIMAL_FEET,
                                 DisplayUnitType.DUT_METERS)
    # RVT >= 2022
    else:
        from Autodesk.Revit.DB import UnitTypeId
        return UnitUtils.ConvertFromInternalUnits(length, UnitTypeId.Meters)



def convert_internal_to_cm(length):
    """Function to convert internal to centimeters."""

    # RVT >= 2022
    if rvt_year < 2022:
        from Autodesk.Revit.DB import DisplayUnitType
        return UnitUtils.Convert(length,
                                 DisplayUnitType.DUT_DECIMAL_FEET,
                                 DisplayUnitType.DUT_CENTIMETERS)
    # RVT >= 2022
    else:
        from Autodesk.Revit.DB import UnitTypeId
        return UnitUtils.ConvertFromInternalUnits(length, UnitTypeId.Centimeters)




def convert_internal_to_m2(area):
    """Function to convert internal to meters."""

    # RVT >= 2022
    if rvt_year < 2022:
        from Autodesk.Revit.DB import DisplayUnitType
        return UnitUtils.Convert(area,
                                 DisplayUnitType.DUT_SQUARE_FEET,
                                 DisplayUnitType.DUT_SQUARE_METERS)
    # RVT >= 2022
    else:
        from Autodesk.Revit.DB import UnitTypeId
        return UnitUtils.ConvertFromInternalUnits(area, UnitTypeId.SquareMeters)