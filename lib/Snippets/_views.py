# -*- coding: utf-8 -*-
# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ==================================================
from pyrevit import forms
from Autodesk.Revit.DB import ( Transaction,
                                View,
                                ViewPlan,
                                ViewSection,
                                View3D,
                                ViewSchedule,
                                ViewDrafting,
                                ParameterValueProvider,
                                FilterStringRule,
                                FilterStringEquals,
                                ElementParameterFilter,
                                FilteredElementCollector,
                                BuiltInParameter,
                                BuiltInCategory,
                                ElementId,
                                ViewFamily,
                                ViewFamilyType)

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ==================================================
uidoc    = __revit__.ActiveUIDocument
doc      = __revit__.ActiveUIDocument.Document
app      = __revit__.Application
rvt_year = int(app.VersionNumber)

# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
# ==================================================
def create_string_equals_filter(key_parameter, element_value, caseSensitive = True):
    """Function to create ElementParameterFilter based on FilterStringRule."""
    f_parameter         = ParameterValueProvider(ElementId(key_parameter))
    f_parameter_value   = element_value

    if rvt_year < 2022:
        f_rule = FilterStringRule(f_parameter, FilterStringEquals(), f_parameter_value, caseSensitive)
    else:
        f_rule = FilterStringRule(f_parameter, FilterStringEquals(), f_parameter_value)

    return ElementParameterFilter(f_rule)

def get_sheet_from_view(view):
    #type:(View) -> ViewPlan
    """Function to get ViewSheet associated with the given ViewPlan"""

    #>>>>>>>>>> CREATE FILTER
    my_filter = create_string_equals_filter(key_parameter=BuiltInParameter.SHEET_NUMBER,
                                            element_value=view.get_Parameter(BuiltInParameter.VIEWER_SHEET_NUMBER).AsString() )
    #>>>>>>>>>> GET SHEET
    return FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().WherePasses(my_filter).FirstElement()

# CREATE VIEW
def create_3D_view(uidoc, name=''):
    """Function to Create a 3D view.
    :param uidoc: UI Document of a project where View should be created
    :param name:  New View Name. '*' will be added in the end if name is not unique.
    :return:      Create 3D View"""

    # GET 3D VIEW TYPE
    all_view_types = FilteredElementCollector(uidoc.Document).OfClass(ViewFamilyType).ToElements()
    all_3D_Types = [i for i in all_view_types if i.ViewFamily == ViewFamily.ThreeDimensional]
    view_type_3D = all_3D_Types[0]

    # CREATE VIEW
    view = View3D.CreateIsometric(uidoc.Document, view_type_3D.Id)

    # RENAME VIEW
    for i in range(50):
        try:
            view.Name = name
            break
        except:
            name += '*'

    return view



