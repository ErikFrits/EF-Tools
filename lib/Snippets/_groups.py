# -*- coding: utf-8 -*-

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗
# ║║║║╠═╝║ ║╠╦╝ ║
# ╩╩ ╩╩  ╚═╝╩╚═ ╩  IMPORT
#==================================================

from Autodesk.Revit.DB import *
from pyrevit import forms

# CUSTOM IMPORTS
from GUI.forms           import select_from_dict


default_doc     = __revit__.ActiveUIDocument.Document
default_uidoc   = __revit__.ActiveUIDocument
default_app     = __revit__.Application



def select_group_types(given_groups = None, uidoc = default_uidoc ,title='__title__', version = 'Version 0.1' ,exit_if_none = False):
    """Function to select group names from a list.
    :param given_groups: List of groups. If none then all groups in project will be used.
    :param uidoc:
    :param exit_if_none:
    :return: list of selected group types_names
    """

    #TODO if given_groups , verify that all elements are Groups
    if not given_groups:
        given_groups = FilteredElementCollector(uidoc.Document).OfCategory(BuiltInCategory.OST_IOSModelGroups).ToElements()


    dict_all_groups = {}
    for g in given_groups:
        group_name = g.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()
        if group_name and group_name not in dict_all_groups:
            dict_all_groups[group_name] = g

    selected_groups = select_from_dict(elements_dict=dict_all_groups,
                                       title=title,
                                       label='Select Groups:',
                                       version=version)

    #>>>>>>>>>> EXIT IF NONE SELECTED
    if not selected_groups and exit_if_none:
        forms.alert("No GroupTypes were selected. \nPlease try again.", exitscript=True)

    return selected_groups




def select_attached_groups(list_of_groups, uidoc = default_uidoc, title="__title__", label = "Select Groups:", version = 'Version 0.1', exit_if_none = False):
    """Function to select attached groups from given list of groups.
    :param list_of_groups: List containing groups from which to take attached groups.
    :return: List of selected attached groups
    """
    dict_of_attached_group_names = {}

    for g in list_of_groups:
        attached_groups_ids = g.GetAvailableAttachedDetailGroupTypeIds()
        for a_group_id in attached_groups_ids:
            a_group = uidoc.Document.GetElement(a_group_id)
            a_group_name = a_group.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()
            if a_group_name and a_group_name not in dict_of_attached_group_names:
                dict_of_attached_group_names[a_group_name] = a_group


    selected_a_groups = select_from_dict(elements_dict = dict_of_attached_group_names,
                                         title=title,
                                         label=label,
                                         version=version)

    # >>>>>>>>>> EXIT IF NONE SELECTED
    if not selected_a_groups and exit_if_none:
        forms.alert("No AttachedGroups were selected. \nPlease try again.", exitscript=True)

    return selected_a_groups




def show_attached_group(view, group, list_a_group_names_to_show, uidoc = default_uidoc):
    """Function to show attached groups that match list_a_groups_to_show in the selected view for selected groups.
    :param view:
    :param group:
    :param list_a_group_names_to_show:
    :return:
    """
    all_attached_groups = group.GetAvailableAttachedDetailGroupTypeIds()
    attached_group_id = None
    # print("\n\nAtached Groups:")
    for a_group_id in all_attached_groups:
        a_group = uidoc.Document.GetElement(a_group_id)
        a_group_name = a_group.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()
        # print(a_group_name)
        if a_group_name in list_a_group_names_to_show:
            attached_group_id = a_group_id


    if attached_group_id:
        print("Showing attached group on the group [{}] in view - [{}]".format(group.Id, view.Name))
        group.ShowAttachedDetailGroups(view,attached_group_id )
