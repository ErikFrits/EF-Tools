# -*- coding: utf-8 -*-
__title__ = "Match Graphic Overrides"
__doc__ = """Version = 1.0
Date    = 15.05.2022
_____________________________________________________________________
Description:

Match Graphic Overrides.
_____________________________________________________________________
How-to:
-> Run the Tool
-> Select element with the main GraphicOverrides
-> Select elements to match same GraphicOverrides 
-> Click [Esc] to finish.
_____________________________________________________________________
Last update:
- [18.05.2022] - 1.1 Bug Fixed.
- [15.05.2022] - 1.0 RELEASE
_____________________________________________________________________
Author: Erik Frits"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ==================================================
# pyRevit
from pyrevit import revit, forms

# Custom Imports
from Snippets._context_manager import ef_Transaction

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ==================================================
doc     = __revit__.ActiveUIDocument.Document
uidoc   = __revit__.ActiveUIDocument
app     = __revit__.Application

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
# ==================================================
if __name__ == '__main__':
    # Select Element with main Override
    with forms.WarningBar(title="Pick Main Element to Get Override Settings.", handle_esc=True):
        selected_element = revit.pick_element()

    # Make sure main is selected.
    if not selected_element:
        forms.alert('Main Element was not selected. Please Try Again.', title=__title__, exitscript=True)

    # Get Override Style
    graphics = doc.ActiveView.GetElementOverrides(selected_element.Id)

    # Pick elements to match Overrides.
    with forms.WarningBar(title="Pick Element to Match Override Settings", handle_esc=True):
        while True:
            elem = None
            try:          elem = revit.pick_element()
            except:       break
            if not elem:  break
            with ef_Transaction(doc,__title__):
                doc.ActiveView.SetElementOverrides(elem.Id, graphics)
