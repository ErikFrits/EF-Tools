from Autodesk.Revit.DB import *



all_floor_types = FilteredElementCollector(doc).OfCategory(
    BuiltInCategory.OST_Floors).WhereElementIsElementType().ToElements()

def dict_name_element(given_elements, dotNet=False):
    dict_output = {Element.Name.GetValue(fr): fr for fr in given_elements}


    return dict_output
