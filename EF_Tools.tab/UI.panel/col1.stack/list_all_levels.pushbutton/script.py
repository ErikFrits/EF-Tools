# -*- coding: utf-8 -*-

__title__  = "List All Levels"
__author__  = "Erik Frits"
__doc__ = """Version = 1.0
Date    = 01.07.2020
_____________________________________________________________________
Description:

Get an overview of all the levels in the project sorted by elevation.
_____________________________________________________________________
How-to:
- Just run the script.
_____________________________________________________________________
"""
#____________________________________________________________________ IMPORTS
import operator
from Autodesk.Revit.DB import (FilteredElementCollector,
                               BuiltInCategory,
                               UnitUtils,
                               DisplayUnitType)
doc = __revit__.ActiveUIDocument.Document

#____________________________________________________________________ MAIN
# GET ALL ELVELS
levels = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()

# CONVERT UNITS TO METERS
dict_lvl = {}
for i in levels:
    dict_lvl[i.Name] = UnitUtils.Convert(i.Elevation, DisplayUnitType.DUT_DECIMAL_FEET, DisplayUnitType.DUT_METERS)

# SORT BY ELEVATION
sorted_x = sorted(dict_lvl.items(), key=operator.itemgetter(1))

# PRINT LEVELS WITH ITS ELEVATIONS
for i in sorted_x[::-1]: #reversed order
    if i[1] > 0:
        print("+{}		{}".format(format(i[1], '.2f'), i[0]))
    elif i[1] < 0:
        print("{}		{}".format(format(i[1], '.2f'), i[0]))
    else:
        print("{}		{}".format("0.00", i[0]))