# -*- coding: utf-8 -*-
__title__ = "Super Select"
__author__ = "Erik Frits"
__helpurl__ = "https://erikfrits.com/blog/super-select-multiple-elements-in-viewmodel/"
__doc__ = """Version = 1.2
Date    = 08.02.2021
_____________________________________________________________________
Description:

This is an improved version of Built-In tools named: 
'Select All Instances: Visible in View' [SS] and
'Select All Instances: In Model'        [SA]

You can now select multiple similar instances in the 
model/view with multiple selected elements. This tool also
supports selection of many unusual elements unlike built-in tool.
_____________________________________________________________________
How-to:

Select a few instances in the model and run the script.
_____________________________________________________________________
Last update:
- [10.06.2021] - 1.2 RELEASE
- [10.06.2021] - Script was refactorred and placed in lib/Selection/ 
- [10.06.2021] - Selection rule added - [Rooms/Area]
- [10.06.2021] - Selection rule added - [PlanRegion]
- [10.06.2021] - Selection rule added - [ScopeBox]
- [13.04.2021] - 1.1 RELEASE 
- [13.04.2021] - added rules for DetailArc, DetailElipse, 
                 DetailCurve, DetailNurbSpline
- [13.04.2021] - Fixed issue if nothing selected 
- [08.02.2021] - 1.0 RELEASE
- [08.02.2021] - Selection rule added - [Refference Planes]
- [08.02.2021] - Selection rule added - [RevisionClouds]
- [08.02.2021] - Selection rule added - [PropertyLine]
- [08.02.2021] - Selection rule added - [Lines]
- [08.02.2021] - Selection rule added - [RoomSeparation/AreaBoundary]
- [08.02.2021] - Imports reduced
_____________________________________________________________________
To-do:
-
_____________________________________________________________________
If you select an element and it changes your selection to many other
unwanted types, please let me know the Category of the elmenet, 
it might need an individual filtering rule.
_____________________________________________________________________
"""

#____________________________________________________________________ IMPORTS
import clr, sys
clr.AddReference("System")
from System.Collections.Generic import List
# from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import ( ModelLine,
                                DetailLine,
                                PropertyLine,
                                RevisionCloud,
                                ReferencePlane,
                                FilteredElementCollector,
                                FilterNumericEquals,
                                FilterElementIdRule,
                                ElementFilter,
                                ElementParameterFilter,
                                LogicalOrFilter,
                                ParameterValueProvider,
                                BuiltInParameter,
                                ElementId,
                                DetailCurve,
                                DetailArc,
                                DetailEllipse,
                                DetailNurbSpline,
                                ModelCurve,
                                ModelArc,
                                ModelEllipse,
                                ModelNurbSpline,
                                ElementCategoryFilter,
                                BuiltInCategory,
                                )





#____________________________________________________________________ FUNCTIONS
def create_filter(key_parameter, element_value):
    """Function to create a RevitAPI filter."""
    f_parameter = ParameterValueProvider(ElementId(key_parameter))
    f_parameter_value = element_value #e.g. element.Category.Id
    f_rule = FilterElementIdRule(f_parameter, FilterNumericEquals(), f_parameter_value)
    filter = ElementParameterFilter(f_rule)
    return filter
#____________________________________________________________________ MAIN

def select(mode):
    """Run Super Select: all in model/view based on given mode."""

    uidoc = __revit__.ActiveUIDocument
    doc = __revit__.ActiveUIDocument.Document
    # print(doc.Title)


    # FILTERS CONTAINER
    list_of_filters = List[ElementFilter]()

    # GET CURRENT SELECTION
    current_selection_ids = uidoc.Selection.GetElementIds()

    # LOOP THROUGH SELECTION
    for id in current_selection_ids:
        element = doc.GetElement(id)
        element_type = type(element)

        # [RULE] - LINES
        line_types = [DetailLine, DetailCurve, DetailArc, DetailEllipse, DetailNurbSpline,
                      ModelLine, ModelCurve, ModelArc, ModelEllipse, ModelNurbSpline]
        if element_type in line_types:
            # [FILTER FOR CATEGORY] - RoomSeparation(-2000066)  / AreaBoundary(-2000079)
            if element.Category.Id == ElementId(-2000066) or element.Category.Id == ElementId(-2000079):
                filter = create_filter(key_parameter=BuiltInParameter.ELEM_CATEGORY_PARAM,
                                       element_value=element.Category.Id)
                list_of_filters.Add(filter)

            # [FILTER FOR LINESTYLE] - Other Lines
            else:
                filter = create_filter(key_parameter=BuiltInParameter.BUILDING_CURVE_GSTYLE,
                                       element_value=element.LineStyle.Id)
                list_of_filters.Add(filter)


        # [RULE] - ReferencePlane
        elif element_type == ReferencePlane:
            filter = create_filter(key_parameter=BuiltInParameter.CLINE_SUBCATEGORY,
                                   element_value=element.get_Parameter(
                                       BuiltInParameter.CLINE_SUBCATEGORY).AsElementId())
            list_of_filters.Add(filter)

        # [RULE] - PropertyLine
        elif element_type == PropertyLine:
            filter = create_filter(key_parameter=BuiltInParameter.ELEM_CATEGORY_PARAM,
                                   element_value=element.Category.Id)
            list_of_filters.Add(filter)

        # [RULE] - RevisionClouds
        elif element_type == RevisionCloud:
            filter = create_filter(key_parameter=BuiltInParameter.REVISION_CLOUD_REVISION,
                                   element_value=element.get_Parameter(
                                       BuiltInParameter.REVISION_CLOUD_REVISION).AsElementId())
            list_of_filters.Add(filter)

        # [RULE] - ROOMS(-2000160)
        elif element.Category.Id == ElementId(-2000160):
            list_of_filters.Add(ElementCategoryFilter(BuiltInCategory.OST_Rooms))

        # [RULE] - AREAS(-2003200)
        elif element.Category.Id == ElementId(-2003200):
            list_of_filters.Add(ElementCategoryFilter(BuiltInCategory.OST_Areas))

        # [RULE] - ScopeBox(-2006000)
        elif element.Category.Id == ElementId(-2006000):
            filter = create_filter(key_parameter=BuiltInParameter.ELEM_CATEGORY_PARAM,
                                   element_value=element.Category.Id)
            list_of_filters.Add(filter)

        # [RULE] - PlanRegion(-2000191)
        elif element.Category.Id == ElementId(-2000191):
            filter = create_filter(key_parameter=BuiltInParameter.ELEM_CATEGORY_PARAM,
                                   element_value=element.Category.Id)
            list_of_filters.Add(filter)

        # [RULE] - MatchLine(-2000193)
        elif element.Category.Id == ElementId(-2000191):
            filter = create_filter(key_parameter=BuiltInParameter.ELEM_CATEGORY_PARAM,
                                   element_value=element.Category.Id)
            list_of_filters.Add(filter)

        # [RULE] - Others
        else:
            filter = create_filter(key_parameter=BuiltInParameter.ELEM_TYPE_PARAM,
                                   element_value=element.GetTypeId())
            list_of_filters.Add(filter)

    if list_of_filters:
        # COMBINE FILTERS
        multiple_filters = LogicalOrFilter(list_of_filters)

        # GET ELEMENTS BASED ON SELECTION MODE
        if mode == "view":
            elems = FilteredElementCollector(doc, doc.ActiveView.Id).WherePasses(multiple_filters).ToElementIds()
        elif mode == "model":
            elems = FilteredElementCollector(doc).WherePasses(multiple_filters).ToElementIds()
        else:
            print("ERROR occured: 'wrong mode'.\n Please contact developer.")
            sys.exit()

        # SET SELECTION
        if elems:
            uidoc.Selection.SetElementIds(List[ElementId](elems))



