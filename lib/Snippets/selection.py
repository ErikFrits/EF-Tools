from Autodesk.Revit.DB import ViewPlan, ViewSection, View3D,ViewSchedule, ViewDuplicateOption, Transaction, ViewType, View
from pyrevit import forms



uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document



def get_selected_elements(self):
    """Property that retrieves selected views or promt user to select some from the dialog box."""
    selected_elements = []

    # VIEWS SELECTED IN UI
    for element_id in uidoc.Selection.GetElementIds():
        element = doc.GetElement(element_id)
        selected_elements.append(element)

    if not selected_elements:
        forms.alert("No elements  were selected.\nPlease, try again.", exitscript=True, title=__title__)

    return selected_elements
