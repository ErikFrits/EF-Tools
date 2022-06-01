# -*- coding: utf-8 -*-

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
#==================================================
import sys

from Autodesk.Revit.DB.Architecture import Room
from Autodesk.Revit.UI.Selection import ISelectionFilter, ObjectType
from Autodesk.Revit.DB import (FilteredElementCollector,
                               BuiltInCategory,
                               BuiltInParameter,
                               ViewSheet,
                               Element,
                               FilledRegionType)

# pyRevit IMPORTS
from pyrevit.forms import SelectFromList
from pyrevit import forms

# CUSTOM IMPORTS
from Snippets._variables import ALL_VIEW_TYPES
from GUI.forms           import select_from_dict

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
#==================================================
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document


# ╔═╗╔═╗╔╦╗  ╔═╗╔═╗╦  ╔═╗╔═╗╔╦╗╔═╗╔╦╗
# ║ ╦║╣  ║   ╚═╗║╣ ║  ║╣ ║   ║ ║╣  ║║
# ╚═╝╚═╝ ╩   ╚═╝╚═╝╩═╝╚═╝╚═╝ ╩ ╚═╝═╩╝
#==================================================
#TODO Create parmaeter 'filter' to pass to a list of Types to filter selection.
# e.g. get_selected_elements(uidoc, filter=[Room,Area]
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
#TODO OBSOLETE. UPDATE FUNCTION ABOVE TO BE ABLE TO FILTER ELEMENTS AND REPLACE WHERE IT IS USED.
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
def get_selected_views(given_uidoc = uidoc, exit_if_none = False, title = '__title__'):
    """Function to get selected views. If none selected give a menu for a user to select views.
    ALL_VIEW_TYPES = [ViewPlan, ViewSection, View3D , ViewSchedule, View, ViewDrafting]
    LastUpdates:
    [15.02.2022] - If no views selected -> Select from DialogBox
    :return: list of selected views."""

    # GET SELECTED ELEMENTS
    doc         = given_uidoc.Document
    UI_selected = given_uidoc.Selection.GetElementIds()

    # GET VIEWS FROM SELECTION
    selected_views = [given_uidoc.Document.GetElement(view_id) for view_id in UI_selected if type(doc.GetElement(view_id)) in ALL_VIEW_TYPES]

    # IF NONE SELECTED - OPEN A DIALOGBOX TO CHOOSE FROM.
    if not selected_views and exit_if_none:
        all_views = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).WhereElementIsNotElementType().ToElements()
        dict_views = {view.Name:view for view in all_views}
        selected_views = select_from_dict(dict_views, title=title, label = 'Select Views', button_name='Select')

    # EXIT IF STILL NONE SELECTED
    if not selected_views and exit_if_none:
        forms.alert("No views were selected. Please try again.", exitscript=True)

    return selected_views

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET SHEETS
def get_selected_sheets(given_uidoc = uidoc, exit_if_none = False, title='__title__', label='Select Sheets', btn_name = 'Select Sheets'):
    """Function to get selected views. return list of selected views.
    LastUpdates:
    [15.02.2022] - If no sheets selected -> Select from DialogBox
    [01.06.2022] - Bug Fixed + added more controls(label, btn_name)"""
    #>>>>>>>>>> GET SELECTED ELEMENTS
    doc         = given_uidoc.Document
    UI_selected = given_uidoc.Selection.GetElementIds()

    #>>>>>>>>>> GET SHEETS FROM SELECTION
    selected_sheets = [doc.GetElement(sheet_id) for sheet_id in UI_selected if type(doc.GetElement(sheet_id)) == ViewSheet]

    #>>>>>>>>>> IF NONE SELECTED - OPEN A DIALOGBOX TO CHOOSE FROM.
    if not selected_sheets:
        all_sheets      = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
        dict_sheets     = {'{} - {}'.format(sheet.SheetNumber, sheet.Name): sheet for sheet in all_sheets}
        selected_sheets = select_from_dict(dict_sheets, title=title, label=label, button_name=btn_name)

    #>>>>>>>>>> EXIT IF STILL NONE SELECTED
    if not selected_sheets and exit_if_none:
        forms.alert("No sheets were selected. Please try again.", exitscript=True)
    return selected_sheets

# ╔═╗╔═╗╦  ╔═╗╔═╗╔╦╗
# ╚═╗║╣ ║  ║╣ ║   ║
# ╚═╝╚═╝╩═╝╚═╝╚═╝ ╩
#==================================================
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> SELECT TITLEBLOCK
def select_title_block(given_uidoc = uidoc, exitscript = True):
    """Function to let user select a title block.
    LastUpdates:
    [15.02.2022] - SelectFromList -> select_from_dict()"""
    doc = given_uidoc.Document
    #>>>>>>>>>> SELECT TITLE BLOCK
    all_title_blocks = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_TitleBlocks).WhereElementIsElementType().ToElements()
    unique_title_blocks = {}
    for tb in all_title_blocks:
        family_name = tb.FamilyName
        type_name = tb.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
        unique_title_blocks["{} - {}".format(family_name, type_name)] = tb.Id

    #>>>>>>>>>> MAKE SURE IT'S SELECTED
    selected_title_block = select_from_dict(unique_title_blocks)

    # VERIFY SOMETHING IS SELECTED
    if not selected_title_block and exitscript:
        forms.alert("No TitleBlock was selected. Please try again.", exitscript = exitscript)

    return selected_title_block[0]

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


# ╔═╗╦╔═╗╦╔═  ╔═╗╦  ╔═╗╔╦╗╔═╗╔╗╔╔╦╗╔═╗
# ╠═╝║║  ╠╩╗  ║╣ ║  ║╣ ║║║║╣ ║║║ ║ ╚═╗
# ╩  ╩╚═╝╩ ╩  ╚═╝╩═╝╚═╝╩ ╩╚═╝╝╚╝ ╩ ╚═╝
#==================================================
#>>>>>>>>>> PICK WALL
def pick_wall(given_uidoc = uidoc):
    """Function to promt user to select a wall element in Revit UI."""
    wall_ref = given_uidoc.Selection.PickObject(ObjectType.Element, CustomISelectionFilter("-2000011"), "Select a Wall")    # -2000011 <- Id of OST_Walls
    wall = given_uidoc.Document.GetElement(wall_ref)
    return wall

def pick_curve(given_uidoc = uidoc):
    """Function to promt user to select a curve element in Revit UI."""
    curve_ref = given_uidoc.Selection.PickObject(ObjectType.Element, CustomISelectionFilter("-2000051"), "Select a Curve")
    selected_curve = given_uidoc.Document.GetElement(curve_ref)
    curve = selected_curve.GeometryCurve
    return curve
