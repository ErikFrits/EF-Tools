
from pyrevit import forms
from Autodesk.Revit.DB import ( Transaction,
                                View,
                                ViewPlan,
                                ViewSection,
                                View3D,
                                ViewSchedule,
                                ViewDrafting)

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document






def get_selected_views():
    """Function to get selected views.
    :return: list of selected views."""
    # GET SELECTED ELEMENTS
    UI_selected = uidoc.Selection.GetElementIds()

    # FILTER SELECTION
    VIEW_TYPES = [  View, ViewPlan, ViewSection, View3D, ViewSchedule, ViewDrafting]
    selected_views = [doc.GetElement(view_id) for view_id in UI_selected if type(doc.GetElement(view_id)) in VIEW_TYPES]

    return selected_views