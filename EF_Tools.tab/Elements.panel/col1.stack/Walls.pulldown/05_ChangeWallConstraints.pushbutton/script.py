# -*- coding: utf-8 -*-
__title__         = "Modify Wall Constraints"
__min_revit_ver__ = 2021
__version__       = 1.0
__doc__ = """Date    = 01.10.2023
_____________________________________________________________________
Sponsored by: Prologue-Systems
Thanks to Scott Reed!

_____________________________________________________________________
Description:
Modify Wall Base/Top Constraints while keeping same geometry.
- Excludes Walls in Groups
- Excludes In-Place Walls
_____________________________________________________________________
How-To:
- *Pre-Select Walls (optional)
- Run the Tool
- Select/Confirm Wall Selection
- Select New Top/Base Level Constraints

# Required Parameters:
-'Modify Base Constraint'
-'Modify Top Constraint'
_____________________________________________________________________
Release 1.0 [01.10.2023]:
_____________________________________________________________________
Author: Erik Frits"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
from Autodesk.Revit.DB           import *
from pyrevit import forms

# Custom
from Snippets._selection import get_selected_walls

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
uidoc        = __revit__.ActiveUIDocument
doc          = uidoc.Document
app          = doc.Application
selection    = uidoc.Selection
rvt_year     = int(app.VersionNumber)

# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝
#==================================================

def select_desired_levels():
    """Function to get user input.
    :return: dict of selected values.
    dict_keys = 'modify_wall_base' | 'level_base' | 'modify_wall_top' | 'level_top' """
    try:
        all_levels = FilteredElementCollector(doc).OfClass(Level).ToElements()
        dict_levels = {lvl.Name: lvl for lvl in all_levels}
        from rpw.ui.forms import (FlexForm, ComboBox, Separator, Button, CheckBox)
        components = [CheckBox('modify_wall_base', 'Modify Base Constraint'),
                      ComboBox('level_base', dict_levels),
                      CheckBox('modify_wall_top', 'Modify Top Constraint'),
                      ComboBox('level_top', dict_levels),
                      Separator(),
                      Button('Modify Wall Constraints') ]
        form = FlexForm(__title__, components)
        form.show()
        return form.values
    except:
        forms.alert('Could not get User Input. Please Try Again.',title=__title__, exitscript=True)

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝

#1️⃣ Select Walls
selected_walls = get_selected_walls(uidoc, exitscript=True)


#2️⃣ Get User Input (Top/Base Constrains)
try:
    user_inputs      = select_desired_levels()
    modify_wall_base = user_inputs['modify_wall_base']
    modify_wall_top  = user_inputs['modify_wall_top']
    new_level_base   = user_inputs['level_base']
    new_level_top    = user_inputs['level_top']
except:
    forms.alert('Could not get User Input. Please Try Again.', title=__title__, exitscript=True)

#3️⃣ Modify Walls
t = Transaction(doc, 'Modify Wall Levels')
t.Start()
for wall in selected_walls:
    try:
        # 👀 Check if Element is Taken (WorkSharing)
        checkoutStatus = WorksharingUtils.GetCheckoutStatus(doc, wall.Id)
        if checkoutStatus == CheckoutStatus.OwnedByOtherUser:
            print('[{}]Wall is Taken by Another User.'.format(wall.Id))
            continue


        # Get Parameters
        p_base_level  = wall.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT)
        p_base_offset = wall.get_Parameter(BuiltInParameter.WALL_BASE_OFFSET)
        p_top_level   = wall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE)
        p_top_offset  = wall.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET)

        # Get param values
        wall_height       = wall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).AsDouble()
        base_offset       = p_base_offset.AsDouble()
        base_level        = doc.GetElement(p_base_level.AsElementId())
        base_level_elev   = base_level.Elevation

        # Calculate Wall Elevations
        wall_base_elevation = base_level_elev + base_offset
        wall_top_elevation  = wall_base_elevation + wall_height

        # MODIFY BASE BASE
        if modify_wall_base:
            p_base_level.Set(new_level_base.Id)

            # Calculate new offset
            new_offset = wall_base_elevation - new_level_base.Elevation
            p_base_offset.Set(new_offset)

        # MODIFY TOP LEVEL
        if modify_wall_top:
            p_top_level.Set(new_level_top.Id)

            # Calculate new offset
            new_offset = wall_top_elevation - new_level_top.Elevation
            p_top_offset.Set(new_offset)
    except:
        pass
t.Commit()