from Autodesk.Revit.DB import (ViewPlan, ViewSection,
                               View3D,ViewSchedule, ViewDuplicateOption,
                               Transaction, ViewType, View,
                               FilteredElementCollector,
                               BuiltInCategory,
                               BuiltInParameter)
from pyrevit.forms import SelectFromList
from pyrevit import forms

from Snippets.variables import ALL_VIEW_TYPES
import sys

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








def get_selected_views():
    """Function to get selected views.
    :return: list of selected views."""
    # GET SELECTED ELEMENTS
    UI_selected = uidoc.Selection.GetElementIds()

    # FILTER SELECTION
    selected_views = [doc.GetElement(view_id) for view_id in UI_selected if type(doc.GetElement(view_id)) in ALL_VIEW_TYPES]

    return selected_views





def select_title_block():
    """Function to let user select a title block."""





    # ______________________________ SELECT TITLE BLOCK
    all_title_blocks = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_TitleBlocks).WhereElementIsElementType().ToElements()
    unique_title_blocks = {}
    for tb in all_title_blocks:
        family_name = tb.FamilyName
        type_name = tb.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
        unique_title_blocks["{} - {}".format(family_name, type_name)] = tb.Id

    selected_option = SelectFromList.show(list(unique_title_blocks), title="TEST")
    if not selected_option:
        print("Nothing was selected")
        print("Script was cancelled. Try again.")
        sys.exit()
    selected_title_block = unique_title_blocks[selected_option]


    return selected_title_block