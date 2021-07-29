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
                                ElementId)

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document





#FIXME DELETE? IT WAS MOVED TO ANOTHER FOLDER
def get_selected_views():
    """Function to get selected views.
    :return: list of selected views."""
    # GET SELECTED ELEMENTS
    UI_selected = uidoc.Selection.GetElementIds()

    # FILTER SELECTION
    VIEW_TYPES = [  View, ViewPlan, ViewSection, View3D, ViewSchedule, ViewDrafting]
    selected_views = [doc.GetElement(view_id) for view_id in UI_selected if type(doc.GetElement(view_id)) in VIEW_TYPES]

    return selected_views






# >>>>>> CREATE FILTER
def create_string_equals_filter(key_parameter, element_value, caseSensitive = True):
    """Function to create ElementParameterFilter based on FilterStringRule."""
    f_parameter         = ParameterValueProvider(ElementId(key_parameter))
    f_parameter_value   = element_value
    caseSensitive       = True
    f_rule              = FilterStringRule(f_parameter, FilterStringEquals(), f_parameter_value, caseSensitive)
    return ElementParameterFilter(f_rule)

def get_sheet_from_view(view):
    #type:(View) -> ViewPlan
    """Function to get ViewSheet associated with the given ViewPlan"""

    #>>>>>>>>>> CREATE FILTER
    my_filter = create_string_equals_filter(key_parameter=BuiltInParameter.SHEET_NUMBER,
                                            element_value=view.get_Parameter(BuiltInParameter.VIEWER_SHEET_NUMBER).AsString() )
    #>>>>>>>>>> GET SHEET
    return FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().WherePasses(my_filter).FirstElement()




if __name__ == '__main__':

    #>>>>>>>>>> ACTIVE VIEW
    active_view = doc.ActiveView
    sheet       = get_sheet_from_view(active_view)

    #>>>>>>>>>> PRINT RESULTS
    if sheet:   print('Sheet Found: {} - {}'.format(sheet.SheetNumber, sheet.Name))
    else:       print('No sheet associated with the given view: {}'.format(view.Name))


