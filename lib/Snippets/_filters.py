# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import ParameterValueProvider, ElementId, FilterNumericEquals, FilterElementIdRule,ElementParameterFilter

def create_filter(key_parameter, element_value):
    """Function to create a RevitAPI filter."""
    f_parameter = ParameterValueProvider(ElementId(key_parameter))
    f_parameter_value = element_value  # e.g. element.Category.Id
    f_rule = FilterElementIdRule(f_parameter, FilterNumericEquals(), f_parameter_value)
    filter = ElementParameterFilter(f_rule)
    return filter

# EXAMPLE GET GROUP INSTANCE
# filter = create_filter(BuiltInParameter.ELEM_TYPE_PARAM, group_type_id)
# group = FilteredElementCollector(doc).WherePasses(filter).FirstElement()