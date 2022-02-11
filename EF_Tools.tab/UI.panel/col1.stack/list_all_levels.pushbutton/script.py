# -*- coding: utf-8 -*-

__title__  = "List All Levels"
__author__  = "Erik Frits"
__doc__ = """Version = 1.01
Date    = 01.07.2020
_____________________________________________________________________
Description:

Get an overview of all the levels in the project sorted by elevation.
_____________________________________________________________________
How-to:
- Just run the script.
_____________________________________________________________________
Last update:
- [11.02.2022] - 1.01 added Revit 2022 Support.

_____________________________________________________________________
Author: Erik Frits
"""
#____________________________________________________________________ IMPORTS
import operator
from Autodesk.Revit.DB import (FilteredElementCollector,
                               BuiltInCategory,
                               UnitUtils)
from Snippets._convert import convert_m_to_feet
doc = __revit__.ActiveUIDocument.Document

#____________________________________________________________________ MAIN
# GET ALL ELVELS
levels = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()

# CONVERT UNITS TO METERS
dict_lvl = {}
for i in levels:
    dict_lvl[i.Name] = convert_m_to_feet(i.Elevation)

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