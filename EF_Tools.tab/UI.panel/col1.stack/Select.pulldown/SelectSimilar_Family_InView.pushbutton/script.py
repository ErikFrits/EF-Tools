# -*- coding: utf-8 -*-
__title__ = "SelectSimilar: Family (in View)"
__author__ = "Erik Frits"
__doc__ = """Version = 1.0
Date    = 22.08.2022
_____________________________________________________________________
Description:
Select all instances in the View of the same Family.

_____________________________________________________________________
How-to:

- Select a single element
- Get All instances of the same family in View
_____________________________________________________________________
Last update:
- [02.09.2022] - 1.0 RELEASE
_____________________________________________________________________"""

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
# ==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application
rvt_year = int(app.VersionNumber)

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
# ==================================================
if __name__ == '__main__':
    from Selection.select_similar_family import select_similar_by_family
    select_similar_by_family(uidoc, mode='view')
    # Same script is used for 2 buttons.
    # - Select Similar: Family (in View)
    # - Select Similar: Family (in Model)