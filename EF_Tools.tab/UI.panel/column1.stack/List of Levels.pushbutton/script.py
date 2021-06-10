# -*- coding: utf-8 -*-

__title__  = "List Of Levels"
__author__  = "Erik Frits"
__doc__ = """
return an ordered list of levels by its elevation.

__version__ = 0.1

WIP:
- Create UI menu with refresh button."""


import clr
import System
import Autodesk
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit import DB
from Autodesk.Revit.DB import *
import time
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application
doc = __revit__.ActiveUIDocument.Document

levels = FilteredElementCollector(doc).OfCategory(
    BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
dict_lvl = {}

for i in levels:
    dict_lvl[i.Name] = i.Elevation * 30.48 / 100

import operator
sorted_x = sorted(dict_lvl.items(), key=operator.itemgetter(1))

for i in sorted_x[::-1]: #reversed order
    if i[1] > 0:
        print("+{}		{}".format(format(i[1], '.2f'), i[0]))
    elif i[1] < 0:
        print("{}		{}".format(format(i[1], '.2f'), i[0]))
    else:
        print("{}		{}".format("+-0.00", i[0]))


print(app.Username)

















