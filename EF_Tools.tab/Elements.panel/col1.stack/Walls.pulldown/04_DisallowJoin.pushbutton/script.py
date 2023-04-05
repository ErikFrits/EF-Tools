# -*- coding: utf-8 -*-
__title__ = "Disallow Join"
__doc__ = """Date    = 22.03.2023
Disallow Join for Selected Walls and Beams.
_____________________________________________________________________
Author: Erik Frits"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
import traceback, clr

from Autodesk.Revit.DB           import *
from Autodesk.Revit.UI.Selection import Selection
from Autodesk.Revit.UI           import UIDocument, UIApplication
from Autodesk.Revit.DB.Structure import *

from pyrevit import forms


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
uidoc        = __revit__.ActiveUIDocument           #type: UIDocument
doc          = __revit__.ActiveUIDocument.Document  #type: Document
app          = __revit__.Application                #type: UIApplication
selection    = uidoc.Selection                      #type: Selection




# ╔═╗╔═╗╔╦╗  ╔═╗╦  ╔═╗╔╦╗╔═╗╔╗╔╔╦╗╔═╗
# ║ ╦║╣  ║   ║╣ ║  ║╣ ║║║║╣ ║║║ ║ ╚═╗
# ╚═╝╚═╝ ╩   ╚═╝╩═╝╚═╝╩ ╩╚═╝╝╚╝ ╩ ╚═╝
# Get Selected Elements
selected_element_ids = selection.GetElementIds()
elements             = [doc.GetElement(e_id) for e_id in selected_element_ids]

if not elements:
    forms.alert('No Elemenets were selected. Please Try Again', title=__title__, exitscript=True)



# ╦ ╦╔╗╔ ╦╔═╗╦╔╗╔
# ║ ║║║║ ║║ ║║║║║
# ╚═╝╝╚╝╚╝╚═╝╩╝╚╝
with Transaction(doc, 'Disallow Join') as t:
    t.Start()
    for el in elements:
        #Unpin Element
        el.Pinned = False

        # Disallow Join (Structural Framing)
        if el.Category.BuiltInCategory == BuiltInCategory.OST_StructuralFraming:
            try:
                StructuralFramingUtils.DisallowJoinAtEnd(el, 0)
                StructuralFramingUtils.DisallowJoinAtEnd(el, 1)
            except:
                print('Could not Disallow Beam[{}]'.format(el.Id))

        # Disallow Join (Walls)
        elif el.Category.BuiltInCategory == BuiltInCategory.OST_Walls:
            try:
                WallUtils.DisallowWallJoinAtEnd(el, 0)
                WallUtils.DisallowWallJoinAtEnd(el, 1)
            except:
                print('Could not Disallow Wall[{}]'.format(el.Id))
    t.Commit()
