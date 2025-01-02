# -*- coding: utf-8 -*-
__title__   = "Unique Door/Window Sections"
__doc__ = """Date    = 30.01.2024
_____________________________________________________________________
Description:
Tutorial on how to Create Sections for all Window Types. 
- Elevation Section
- Cross Section
- Plan Section (Yes, we can create PlansViews with sections)

_____________________________________________________________________
Author: Erik Frits"""
# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
from Autodesk.Revit.DB import *
from pyrevit import forms

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
uidoc     = __revit__.ActiveUIDocument
doc       = __revit__.ActiveUIDocument.Document #type: Document
app       = __revit__.Application

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#==================================================
#👉 Get and Sort Window Instances of Each Type
windows = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).WhereElementIsNotElementType().ToElements()

dict_windows = {}
for win in windows:
    family_name = win.Symbol.Family.Name
    type_name   = Element.Name.GetValue(win.Symbol)
    key_name    = '{}_{}'.format(family_name, type_name)

    host = win.Host
    if type(host) == Wall:
        dict_windows[key_name] = win
    else:
        print('Unsupported Host for Window: {} [{}]'.format(key_name, win.Id))

# #👀 Preview Dict Windows
# for k,v in dict_windows.items():
#     print(k,v)

#🔏 Create Transaction to Modify Project
t = Transaction(doc, 'Generate Window Sections')
t.Start() #🔓





#🎯 Create Section
for window_name, window in dict_windows.items():
    try:
        #1️⃣ Get Window Origin Point
        win_origin = window.Location.Point          #type: XYZ

        #2️⃣ Calculate Vector based on the Wall
        host_wall = window.Host
        curve     = host_wall.Location.Curve        #type: Curve
        pt_start  = curve.GetEndPoint(0)            #type: XYZ
        pt_end    = curve.GetEndPoint(1)            #type: XYZ
        vector    = pt_end - pt_start               #type: XYZ

        #3️⃣ Get Window Size
        win_width  = window.Symbol.get_Parameter(BuiltInParameter.GENERIC_WIDTH).AsDouble()
        cm_40      = UnitUtils.ConvertToInternalUnits(40, UnitTypeId.Centimeters) #40cm (Revit API takes unit in FEET!)
        win_depth  = cm_40
        offset     = cm_40
        win_height = window.Symbol.get_Parameter(BuiltInParameter.CASEWORK_HEIGHT).AsDouble() # ADJUST TO YOUR PARAMETERS!
        if not win_height:
            win_height = window.Symbol.LookupParameter('Höhe ab FBOK').AsDouble() # ADJUST TO YOUR PARAMETERS!

        # ╔╦╗╦═╗╔═╗╔╗╔╔═╗╔═╗╔═╗╦═╗╔╦╗
        #  ║ ╠╦╝╠═╣║║║╚═╗╠╣ ║ ║╠╦╝║║║
        #  ╩ ╩╚═╩ ╩╝╚╝╚═╝╚  ╚═╝╩╚═╩ ╩
        # ==================================================

        # 🪟 TRANSFORMATION - ELEVATION SECTION
        # 4️⃣🅰️ Create Transform (Origin point + X,Y,Z Vectors)

        # TRANSFORMATION - ELEVATION
        trans        = Transform.Identity           # Create Instance of Transform
        trans.Origin = win_origin                   # Set Origin Point (Window Insertion Point)

        vector = vector.Normalize() # * -1/1 Multiply Vector to flip Section if necessary!

        trans.BasisX = vector
        trans.BasisY = XYZ.BasisZ
        trans.BasisZ = vector.CrossProduct(XYZ.BasisZ)  #The cross product is defined as the vector which is perpendicular to both vectors
        # ==================================================

        # #🪟 TRANSFORMATION - CROSS SECTION
        # #4️⃣🅱️ Create Transform (Origin point + X,Y,Z Vectors)
        # trans        = Transform.Identity           # Create Instance of Transform
        # trans.Origin = win_origin                   # Set Origin Point (Window Insertion Point)
        #
        # vector = vector.Normalize() # * -1/1 Multiply Vector to flip Section if necessary!
        #
        # vector_cross = vector.CrossProduct(XYZ.BasisZ)
        #
        # trans.BasisX = vector_cross
        # trans.BasisY = XYZ.BasisZ
        # trans.BasisZ = vector_cross.CrossProduct(XYZ.BasisZ)
        # # ==================================================

        # #🪟 TRANSFORMATION - SECTION PLAN
        # #4️⃣©️ Create Transform (Origin point + X,Y,Z Vectors)
        # trans = Transform.Identity  # Create Instance of Transform
        # trans.Origin = win_origin  # Set Origin Point (Window Insertion Point)
        #
        # # Create Transform for PlanSection (XYZ Vectors) 🤦‍♂️ Yes, Section can be used to look down like Plans...
        # vector = vector.Normalize()
        # trans.BasisX = vector
        # trans.BasisY = -XYZ.BasisZ.CrossProduct(vector).Normalize()
        # trans.BasisZ = -XYZ.BasisZ

        # ==================================================

        #5️⃣ Create SectionBox
        section_box = BoundingBoxXYZ() # origin 0,0,0

        half            = win_width/2
        section_box.Min = XYZ(-half - offset ,  0          - offset , -win_depth)
        section_box.Max = XYZ(half + offset  ,  win_height + offset , win_depth)
        #💡               XYZ(X - Left/Right , Y - Up/Down          , Z - Forward/Backwards)

        section_box.Transform = trans # Apply Transform (Origin + XYZ Vectors)

        #6️⃣ Create Section View
        section_type_id  = doc.GetDefaultElementTypeId(ElementTypeGroup.ViewTypeSection)
        window_elevation = ViewSection.CreateSection(doc, section_type_id, section_box)

        # 7️⃣ New Name
        new_name = 'py_{} (Plan)'.format(window_name)

        for i in range(10):
            try:
                window_elevation.Name = new_name
                print('✅ Created Section: {}'.format(new_name))
                break
            except:
                new_name += '*'

    except:
        import traceback
        print('---\n❌ERROR:')
        print(traceback.format_exc())

t.Commit() # 🔒