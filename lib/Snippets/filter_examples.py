# -*- coding: utf-8 -*-
__title__ = "Get sheet from View"
__author__ = "Erik Frits"

#>>>>>>>>>> IMPORTS
import clr, os
from Autodesk.Revit.DB import *

#>>>>>>>>>> VARIABLES
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

#>>>>>>>>>> STRING FILTER
def create_string_filter(key_parameter, element_value, caseSensitive = True):
    """Function to create a RevitAPI filter."""
    f_parameter         = ParameterValueProvider(ElementId(key_parameter))  #sheet.SheetNumber
    f_parameter_value   = element_value #e.g. element.Category.Id           #element.GetPara
    caseSensitive       = True
    f_rule              = FilterStringRule(f_parameter, FilterStringEquals(), f_parameter_value, caseSensitive)
    return ElementParameterFilter(f_rule)

#>>>>>>>>>> MAIN
if __name__ == '__main__':

    #>>>>>>>>>> ACTIVE VIEW
    view = doc.ActiveView
    #>>>>>>>>>> CREATE FILTER FROM VIEW's VIEWER SHEET NUMBER
    my_filter = create_string_filter(key_parameter = BuiltInParameter.SHEET_NUMBER,
                                     element_value= view.get_Parameter(BuiltInParameter.VIEWER_SHEET_NUMBER).AsString())
    #>>>>>>>>>> GET SHEET
    sheet = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().WherePasses(my_filter).FirstElement()

    #>>>>>>>>>> PRINT RESULTS
    if sheet:   print('Sheet Found: {} - {}'.format(sheet.SheetNumber, sheet.Name))
    else:       print('No sheet associated with the given view: {}'.format(view.Name))