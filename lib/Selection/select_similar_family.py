# -*- coding: utf-8 -*-
__title__ = "Select Similar Family Instances in Model"
__author__ = "Erik Frits"
__doc__ = """Version = 1.0
Date    = 22.08.2022
_____________________________________________________________________
Description:
Select all instances in the project of the same Family.
_____________________________________________________________________
How-to:
- Select a single element
- Get All instances of the same family in Model
_____________________________________________________________________
Last update:
- [22.08.2022] - 1.0 RELEASE
_____________________________________________________________________
"""
# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ==================================================
import clr
clr.AddReference("System")
from System.Collections.Generic import List
from Autodesk.Revit.DB import *

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
# ==================================================
# doc   = __revit__.ActiveUIDocument.Document
# uidoc = __revit__.ActiveUIDocument
app     = __revit__.Application
rvt_year = int(app.VersionNumber)

# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝ FUNCTION
# ==================================================
def select_similar_by_family(uidoc, mode):
    doc = uidoc.Document
    selected_elements = uidoc.Selection.GetElementIds()

    try:
        # Check that Only single item is selected!
        if len(selected_elements) != 1:
            from pyrevit import forms
            forms.alert('You need to select only 1 element.', title=__title__, exitscript=True)

        selected_element = doc.GetElement(selected_elements[0])

        # CREATE FILTER RULE
        elem_type_id = selected_element.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).AsElementId()
        elem_type = doc.GetElement(elem_type_id)
        elem_family_name = elem_type.FamilyName
        f_parameter = ParameterValueProvider(ElementId(BuiltInParameter.ALL_MODEL_FAMILY_NAME))
        f_parameter_value = elem_family_name

        if rvt_year < 2023:
            f_rule = FilterStringRule(f_parameter, FilterStringEquals(), f_parameter_value,True)
        else:
            f_rule = FilterStringRule(f_parameter, FilterStringEquals(), f_parameter_value)

        # CREATE FILTER
        filter_family_name = ElementParameterFilter(f_rule)

        # GET ELEMENTS
        elements_by_f_name = []
        if mode   == 'model':
            elements_by_f_name = FilteredElementCollector(doc)\
                    .WherePasses(filter_family_name).WhereElementIsNotElementType().ToElementIds()
        elif mode == 'view':
            elements_by_f_name = FilteredElementCollector(doc, doc.ActiveView.Id)\
                    .WherePasses(filter_family_name).WhereElementIsNotElementType().ToElementIds()

        # SET SELECTION
        if elements_by_f_name:
            uidoc.Selection.SetElementIds(List[ElementId](elements_by_f_name))
    except:
        print('{} is not supported with this tool.'.format(type(selected_element)))