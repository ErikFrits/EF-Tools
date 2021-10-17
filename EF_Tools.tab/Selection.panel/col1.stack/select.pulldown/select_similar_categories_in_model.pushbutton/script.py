# -*- coding: utf-8 -*-
__title__ = "Select similar categories (in model)"
__author__ = "Erik Frits"
__doc__ = """Version = 1.0
Date    = 12.07.2021
_____________________________________________________________________
Description:

This tool will select will select all elements in model that
have the same category as currently selected elements.
_____________________________________________________________________
How-to:

-> Slect a few instances, which categories you would like to select.
-> Run the script
_____________________________________________________________________
Last update:

- [12.07.2021] - 1.0 RELEASE
_____________________________________________________________________
To-do:

- Test the tool with different elements.
_____________________________________________________________________
"""
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> MAIN
# Same script is used for 2 buttons.
# - Select similar categories (in view)
# - Select similar categories (in model)

# lib/Selection/super_select.py
uidoc = __revit__.ActiveUIDocument

from Selection import select_similar_category
select_similar_category.select(uidoc=uidoc, mode='model')