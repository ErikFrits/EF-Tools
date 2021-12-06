from Autodesk.Revit.DB import (FilteredElementCollector,
                               BuiltInCategory,
                               BuiltInParameter,
                               ViewSheet,
                               Element,
                               FilledRegionType)

from Autodesk.Revit.DB.Architecture import Room
from pyrevit.forms import SelectFromList
from pyrevit import forms

from Snippets._variables import ALL_VIEW_TYPES
import sys

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
from Autodesk.Revit.UI.Selection import ISelectionFilter, ObjectType


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET ELEMENTS

def get_selected_elements(given_uidoc = uidoc):
    """Property that retrieves selected views or promt user to select some from the dialog box."""
    selected_elements = []

    #>>>>>>>>>> VIEWS SELECTED IN UI
    for element_id in given_uidoc.Selection.GetElementIds():
        element = given_uidoc.Document.GetElement(element_id)
        selected_elements.append(element)

    if not selected_elements:
        forms.alert("No elements  were selected.\nPlease, try again.", exitscript=True)
    return selected_elements


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET ROOMS
def get_selected_rooms(given_uidoc = uidoc, exit_if_none = False):
    """Function to get selected views.
    :return: list of selected views."""
    #>>>>>>>>>> GET SELECTED ELEMENTS
    UI_selected = given_uidoc.Selection.GetElementIds()

    #>>>>>>>>>> FILTER SELECTION
    selected_rooms = [given_uidoc.Document.GetElement(view_id) for view_id in UI_selected if type(given_uidoc.Document.GetElement(view_id)) == Room]

    #>>>>>>>>>> EXIT IF NONE SELECTED
    if not selected_rooms and exit_if_none:
        forms.alert("No views were selected. Please try again.", exitscript=True)

    return selected_rooms






#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET VIEWS

def get_selected_views(given_uidoc = uidoc, exit_if_none = False):
    """Function to get selected views.
    :return: list of selected views."""
    #>>>>>>>>>> GET SELECTED ELEMENTS
    doc = given_uidoc.Document
    UI_selected = given_uidoc.Selection.GetElementIds()

    #>>>>>>>>>> FILTER SELECTION
    selected_views = [given_uidoc.Document.GetElement(view_id) for view_id in UI_selected if type(doc.GetElement(view_id)) in ALL_VIEW_TYPES]

    #>>>>>>>>>> EXIT IF NONE SELECTED
    if not selected_views and exit_if_none:
        forms.alert("No views were selected. Please try again.", exitscript=True)

    return selected_views






#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET SHEETS
def get_selected_sheets(given_uidoc = uidoc, exit_if_none = False):
    """Function to get selected views.
    return list of selected views."""
    #>>>>>>>>>> GET SELECTED ELEMENTS
    doc = given_uidoc.Document
    UI_selected = given_uidoc.Selection.GetElementIds()

    #>>>>>>>>>> FILTER SELECTION
    selected_sheets = [doc.GetElement(sheet_id) for sheet_id in UI_selected if type(doc.GetElement(sheet_id)) == ViewSheet ]

    #>>>>>>>>>> EXIT IF NONE SELECTED
    if not selected_sheets and exit_if_none:
        forms.alert("No sheets were selected. Please try again.", exitscript=True)

    return selected_sheets






#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> SELECT TITLEBLOCK


def select_title_block(given_uidoc = uidoc):
    """Function to let user select a title block."""
    doc = given_uidoc.Document
    #>>>>>>>>>> SELECT TITLE BLOCK
    all_title_blocks = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_TitleBlocks).WhereElementIsElementType().ToElements()
    unique_title_blocks = {}
    for tb in all_title_blocks:
        family_name = tb.FamilyName
        type_name = tb.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
        unique_title_blocks["{} - {}".format(family_name, type_name)] = tb.Id

    #>>>>>>>>>> MAKE SURE IT'S SELECTED
    selected_option = SelectFromList.show(list(unique_title_blocks), title="Select Title Block")
    if not selected_option:
        forms.alerts("Nothing was selected. Please try again", exitscript=True)

    selected_title_block = unique_title_blocks[selected_option]
    return selected_title_block


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PICK WALL

#>>>>>>>>> LIMIT SELECTION
class CustomISelectionFilter(ISelectionFilter):
    """Filter user selection to certain element."""
    def __init__(self, nom_categorie):
        self.nom_categorie = nom_categorie

    def AllowElement(self, e):
        if str(e.Category.Id) == str(self.nom_categorie):
        #if e.Category.Name == "Walls"
            return True
        else:
            return False
    def AllowReference(self, ref, point):
        return True


#>>>>>>>>>> PICK WALL
def pick_wall(given_uidoc = uidoc):
    """Function to promt user to select a wall element."""
    wall_id = given_uidoc.Selection.PickObject(ObjectType.Element, CustomISelectionFilter("-2000011"), "Select a Wall")    # -2000011 <- Id of OST_Walls
    wall = given_uidoc.Document.GetElement(wall_id)
    return wall


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET RegionType
def select_region_type(given_uidoc = uidoc):
    all_filled_regions = FilteredElementCollector(given_uidoc.Document).OfClass(FilledRegionType)
    dict_filled_regions = {Element.Name.GetValue(fr):fr for fr in all_filled_regions}

    #>>>>>>>>>> PROMT USER TO SELECT FilledRegion TYPE
    selection           = forms.SelectFromList.show(dict_filled_regions.keys(),title="Select FilledRegion Type", button_name='Select')
    if not selection:     forms.alert("FilledRegion Type was not chosen. Please try again.", title='Select FilledRegion Type', exitscript=True)
    return dict_filled_regions[selection]

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET FloorType
def select_floor_type(given_uidoc = uidoc):
    all_floor_types = FilteredElementCollector(given_uidoc.Document).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsElementType().ToElements()
    dict_floor_types = {Element.Name.GetValue(fr):fr for fr in all_floor_types}


    #>>>>>>>>>> PROMT USER TO SELECT FilledRegion TYPE
    selection           = forms.SelectFromList.show(dict_floor_types.keys(),title="Select Floor Type", button_name='Select')
    if not selection:     forms.alert("Floor Type was not chosen. Please try again.", title='Select Floor Type', exitscript=True)
    return dict_floor_types[selection]


