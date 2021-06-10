# -*- coding: utf-8 -*-
__title__ = "Super Select multiple: all in the model"
__author__ = "Erik Frits"
__highlight__ = 'updated'
__helpurl__ = "https://erikfrits.com/blog/super-select-multiple-elements-in-viewmodel/"
__doc__ = """Version = 1.1
Date    = 08.02.2021
_____________________________________________________________________
Description:

This is an improved version of BuiltIn tool named: 
'Select All Instances: Visible in Model' [SA]. 
You can now select similar instances visible in 
the view with multiple selected elements. 
_____________________________________________________________________
How-to:

Select a few instances in the model and run the script.
Your selection should be updated to similar instances 
visible in the model.
_____________________________________________________________________
Prerequisite:

-Select a few elements before running the script.
_____________________________________________________________________
Last update:
- [13.04.2021] - 1.1 RELEASE 
- [13.04.2021] - added rules for DetailArc, DetailElipse, 
DetailCurve, DetailNurbSpline
- [13.04.2021] - Fixed issue if nothing selected 
- [02.02.2021] - 1.0 RELEASE
- [08.02.2021] - Selection  tool works
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
You are welcome to give me a feedback about the 
tool if you will encounter any issues with it.

E: erikfrits.95@gmail.com
_____________________________________________________________________
"""


#____________________________________________________________________ IMPORTS
import clr
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
                                )

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document

#____________________________________________________________________ FUNCTIONS

def create_filter(key_parameter, element_value):
    """Function to create RevitAPI filter."""
    f_parameter = ParameterValueProvider(ElementId(key_parameter))
    f_parameter_value = element_value #e.g. element.Category.Id
    f_rule = FilterElementIdRule(f_parameter, FilterNumericEquals(), f_parameter_value)
    filter = ElementParameterFilter(f_rule)
    return filter

#____________________________________________________________________ MAIN

current_selection_ids =  uidoc.Selection.GetElementIds()
list_of_filters = List[ElementFilter]()

for id in current_selection_ids:
    element = doc.GetElement(id)
    element_type = type(element)

    # Rule - [Lines]
    line_types = [DetailLine, DetailCurve, DetailArc, DetailEllipse, DetailNurbSpline,
                  ModelLine , ModelCurve , ModelArc , ModelEllipse , ModelNurbSpline]
    if element_type in line_types:
        # *CATEGORY FILTER* RoomSeparation(-2000066)  / AreaBoundary(-2000079)
        if element.Category.Id == ElementId(-2000066) or element.Category.Id == ElementId(-2000079):
            filter = create_filter(key_parameter=BuiltInParameter.ELEM_CATEGORY_PARAM,
                                   element_value=element.Category.Id)
            list_of_filters.Add(filter)


        # *LINESTYLE FILTER* Other Lines
        else:
            filter = create_filter(key_parameter=BuiltInParameter.BUILDING_CURVE_GSTYLE,
                                   element_value=element.LineStyle.Id)
            list_of_filters.Add(filter)


    # Rule - [ReferencePlane]
    elif element_type == ReferencePlane:
        filter = create_filter(key_parameter=BuiltInParameter.CLINE_SUBCATEGORY,
                               element_value=element.get_Parameter(BuiltInParameter.CLINE_SUBCATEGORY).AsElementId())
        list_of_filters.Add(filter)


    # Rule - [PropertyLine]
    elif element_type == PropertyLine:
        filter = create_filter(key_parameter=BuiltInParameter.ELEM_CATEGORY_PARAM,
                               element_value=element.Category.Id)
        list_of_filters.Add(filter)

    # Rule - [RevisionClouds]
    elif element_type == RevisionCloud:

        filter = create_filter(key_parameter=BuiltInParameter.REVISION_CLOUD_REVISION,
                               element_value=element.get_Parameter(BuiltInParameter.REVISION_CLOUD_REVISION).AsElementId())
        list_of_filters.Add(filter)

    # Rule - [Others]
    else:
        filter = create_filter(key_parameter=BuiltInParameter.ELEM_TYPE_PARAM,
                               element_value=element.GetTypeId())
        list_of_filters.Add(filter)


if list_of_filters:
    multiple_filters = LogicalOrFilter(list_of_filters)
    elems = FilteredElementCollector(doc).WherePasses(multiple_filters).ToElementIds()

    # SET SELECTION
    if elems:
        uidoc.Selection.SetElementIds(List[ElementId](elems))


