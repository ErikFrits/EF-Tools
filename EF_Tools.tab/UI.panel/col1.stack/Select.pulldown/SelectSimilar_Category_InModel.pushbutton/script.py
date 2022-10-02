# -*- coding: utf-8 -*-
__title__ = "SelectSimilar: Category (in Model)"
__author__ = "Erik Frits"
__doc__ = """Version = 1.0
Date    = 12.07.2021
_____________________________________________________________________
Description:

This tool will select all elements in model that
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
# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
# ==================================================
uidoc = __revit__.ActiveUIDocument

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
# ==================================================
from Selection import select_similar_category
select_similar_category.select(uidoc=uidoc, mode='model')
# Same script is used for 2 buttons.
# - Select Similar: Category (in View)
# - Select Similar: Category (in Model)