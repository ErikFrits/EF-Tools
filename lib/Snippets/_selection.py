# -*- coding: utf-8 -*-
# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
#==================================================
import sys, clr
import traceback

from Autodesk.Revit.UI.Selection    import ISelectionFilter, ObjectType, Selection
from Autodesk.Revit.DB.Architecture import Room
from Autodesk.Revit.DB import *

# pyRevit IMPORTS
from pyrevit.forms import SelectFromList
from pyrevit import forms

#.NET
clr.AddReference('System')
from System.Collections.Generic import List

# CUSTOM IMPORTS
from Snippets._variables import ALL_VIEW_TYPES
from GUI.forms           import select_from_dict

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
#==================================================
uidoc     = __revit__.ActiveUIDocument
doc       = __revit__.ActiveUIDocument.Document
selection = uidoc.Selection                          # type: Selection

# ╔═╗╔═╗╔╦╗  ╔═╗╔═╗╦  ╔═╗╔═╗╔╦╗╔═╗╔╦╗
# ║ ╦║╣  ║   ╚═╗║╣ ║  ║╣ ║   ║ ║╣  ║║
# ╚═╝╚═╝ ╩   ╚═╝╚═╝╩═╝╚═╝╚═╝ ╩ ╚═╝═╩╝
#==================================================
def get_selected_elements(uidoc = uidoc, exitscript=True):
    """Property that retrieves selected views or promt user to select some from the dialog box."""
    doc       = uidoc.Document
    selection = uidoc.Selection  # type: Selection

    try:
        selected_elements = [doc.GetElement(e_id) for e_id in selection.GetElementIds()]
        if not selected_elements:
            forms.alert("No elements  were selected.\nPlease, try again.", exitscript=exitscript)
    except:
        return

    return selected_elements

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET ROOMS

def get_selected_rooms(uidoc=uidoc, exitscript = True):
    """Function to Pick Rooms.
    Previously selected rooms will be pre-selected."""
    doc       = uidoc.Document
    selection = uidoc.Selection  # type: Selection

    selected_elements = [doc.GetElement(e_id) for e_id in selection.GetElementIds()]
    selected_rooms    = [e for e in selected_elements if type(e) == Room]
    ref_rooms         = [Reference(r) for r in selected_rooms]
    ref_preselection  = List[Reference](ref_rooms)

    # Pick Walls (exterior walls are preselected)
    ISF_Rooms      = ISelectionFilter_Classes([Room,])
    selected_rooms = []

    try:
        with forms.WarningBar(title='Select Rooms and click "Finish"'):
            ref_selected_rooms = selection.PickObjects(ObjectType.Element,
                                                       ISF_Rooms,
                                                       'Select Rooms',
                                                       ref_preselection)

        selected_rooms  = [doc.GetElement(ref) for ref in ref_selected_rooms]
    except:
        pass

    if not selected_rooms:
        error_msg = 'No Rooms were selected.\nPlease Try Again'
        forms.alert(error_msg, title='Room Selection has Failed.', exitscript=exitscript)

    return selected_rooms



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET VIEWS
def get_selected_views(given_uidoc = uidoc, exit_if_none = False, title = '__title__', version = 'Version: _'):
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
    if not selected_views:
        all_views = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).WhereElementIsNotElementType().ToElements()
        dict_views = {view.Name:view for view in all_views}
        selected_views = select_from_dict(dict_views, title=title, label = 'Select Views', button_name='Select', version=version)

    # EXIT IF STILL NONE SELECTED
    if not selected_views and exit_if_none:
        forms.alert("No views were selected. Please try again.", exitscript=True)

    return selected_views

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET SHEETS
def get_selected_sheets(given_uidoc = uidoc, exit_if_none = False, title='__title__', label='Select Sheets',
                        btn_name = 'Select Sheets',  version = 'Version: _'):
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
        selected_sheets = select_from_dict(dict_sheets, title=title, label=label, button_name=btn_name, version=version)

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
    selected_title_block = select_from_dict(unique_title_blocks, SelectMultiple=False)

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
# ╦  ╔═╗╔═╗╦  ╔═╗╔═╗╔╦╗╦╔═╗╔╗╔  ╔═╗╦╦ ╔╦╗╔═╗╦═╗
# ║  ╚═╗║╣ ║  ║╣ ║   ║ ║║ ║║║║  ╠╣ ║║  ║ ║╣ ╠╦╝
# ╩  ╚═╝╚═╝╩═╝╚═╝╚═╝ ╩ ╩╚═╝╝╚╝  ╚  ╩╩═╝╩ ╚═╝╩╚═
class CustomISelectionFilter(ISelectionFilter):
    """Filter user selection to certain element."""
    def __init__(self, cats):
        self.cats = cats
    def AllowElement(self, e):
        if str(e.Category.Id) == str(self.cats):
        #if e.Category.Name == "Walls"
            return True
        return False

class ISelectionFilter_Classes(ISelectionFilter):
    def __init__(self, allowed_types):
        """ ISelectionFilter made to filter with types
        :param allowed_types: list of allowed Types"""
        self.allowed_types = allowed_types

    def AllowElement(self, element):
        if type(element) in self.allowed_types:
            return True


# ╔═╗╦╔═╗╦╔═  ╔═╗╦  ╔═╗╔╦╗╔═╗╔╗╔╔╦╗╔═╗
# ╠═╝║║  ╠╩╗  ║╣ ║  ║╣ ║║║║╣ ║║║ ║ ╚═╗
# ╩  ╩╚═╝╩ ╩  ╚═╝╩═╝╚═╝╩ ╩╚═╝╝╚╝ ╩ ╚═╝
#==================================================
#>>>>>>>>>> PICK WALL
def pick_wall(given_uidoc = uidoc):
    """Function to promt user to select a wall element in Revit UI."""
    wall_ref = given_uidoc.Selection.PickObject(ObjectType.Element, CustomISelectionFilter("-2000011"), "Select a Wall")    # -2000011 <- Id of OST_Walls
    wall     = given_uidoc.Document.GetElement(wall_ref)
    return wall

def pick_curve(given_uidoc = uidoc):
    """Function to promt user to select a curve element in Revit UI."""
    curve_ref = given_uidoc.Selection.PickObject(ObjectType.Element, CustomISelectionFilter("-2000051"), "Select a Curve")
    selected_curve = given_uidoc.Document.GetElement(curve_ref)
    curve = selected_curve.GeometryCurve
    return curve


