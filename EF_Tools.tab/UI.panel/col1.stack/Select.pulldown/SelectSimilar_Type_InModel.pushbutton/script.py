# -*- coding: utf-8 -*-
__title__ = "SelectSimilar: Type (in Model) -SA"
__author__ = "Erik Frits"
__helpurl__ = "https://erikfrits.com/blog/super-select-multiple-elements-in-viewmodel/"
__doc__ = """Version = 1.2
Date    = 08.02.2021
_____________________________________________________________________
Description:

This is an improved version of Built-In tools named: 
'Select All Instances: In Model'        [SA]

You can now select multiple similar instances in the 
model/view with multiple selected elements. This tool also
supports selection of many unusual elements unlike built-in tool.
_____________________________________________________________________
How-to:

Select a few instances in the model and run the script.
_____________________________________________________________________
Last update:
- [10.06.2021] - 1.2 RELEASE
- [10.06.2021] - Script was refactorred and placed in lib/Selection/ 
- [10.06.2021] - Selection rule added - [Rooms/Area]
- [10.06.2021] - Selection rule added - [PlanRegion]
- [10.06.2021] - Selection rule added - [ScopeBox]
- [13.04.2021] - 1.1 RELEASE 
- [13.04.2021] - added rules for DetailArc, DetailElipse, 
                 DetailCurve, DetailNurbSpline
- [13.04.2021] - Fixed issue if nothing selected 
- [08.02.2021] - 1.0 RELEASE
- [08.02.2021] - Selection rule added - [Refference Planes]
- [08.02.2021] - Selection rule added - [RevisionClouds]
- [08.02.2021] - Selection rule added - [PropertyLine]
- [08.02.2021] - Selection rule added - [Lines]
- [08.02.2021] - Selection rule added - [RoomSeparation/AreaBoundary]
- [08.02.2021] - Imports reduced
_____________________________________________________________________
To-do:
- 
_____________________________________________________________________
If you select an element and it changes your selection to many other
unwanted types, please let me know the Category of the elmenet, 
it might need an individual filtering rule.
_____________________________________________________________________
"""
#____________________________________________________________________ MAIN
# Same script is used for 2 buttons.
# - Super Select : all in the model (SA)
# - Super Select : all in the view  (SS)

# lib/Selection/super_select.py
from Selection import super_select
super_select.select(mode='model')