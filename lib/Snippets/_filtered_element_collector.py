#>>>>>>>>>> IMPORTS
from Autodesk.Revit.DB import *

#>>>>>>>>>> .NET IMPORTS
import clr, sys
clr.AddReference("System")
from System.Collections.Generic import List

#>>>>>>>>>> VARIABLES
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> FilteredElementCollector(doc).

all_text               = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_TextNotes).WhereElementIsNotElementType().ToElements()

all_lines               = FilteredElementCollector(doc, doc.ActiveView.Id).WherePasses(ElementClassFilter(CurveElement)).ToElements()
all_rooms               = FilteredElementCollector(doc).WherePasses(ElementCategoryFilter(BuiltInCategory.OST_Rooms)).ToElements()
all_doors               = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()
all_windows             = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).WhereElementIsNotElementType().ToElements()
all_floors              = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElements()
all_structural_columns  = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralColumns).WhereElementIsNotElementType().ToElements()
all_columns             = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralColumns).WhereElementIsNotElementType().ToElements()
all_walls               = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
all_generic_models      = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()

#>>>>>>>>>> ANNOTATIONS
all_revision_clouds     = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_RevisionClouds).WhereElementIsNotElementType().ToElements()

#>>>>>>>>>> VIEWS
all_views               = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).ToElements()
all_legends             = [view for view in all_views if view.ViewType == ViewType.Legend]
all_sheets              = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()

#>>>>>>>>>> TAGS
view_window_tags        = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_WindowTags).WhereElementIsNotElementType().ToElements()
view_doors_tags         = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_DoorTags).WhereElementIsNotElementType().ToElements()

#>>>>>>>>>> DOC
all_Categories = doc.Settings.Categories

#>>>>>>>>>> SPECIAL
materials    = FilteredElementCollector(doc).OfClass(Material)
all_worksets = FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset).ToWorksets()





# ElementMulticategoryFilter
list_of_categories  = List[BuiltInCategory]([BuiltInCategory.OST_Walls, BuiltInCategory.OST_Floors, BuiltInCategory.OST_Roofs])
multi_cat_filter    = ElementMulticategoryFilter(list_of_categories)
all_builtin_types   = FilteredElementCollector(doc).WherePasses(multi_cat_filter).ToElements()






#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
# #>>>>>>>>>> CREATE FILTER
# def create_filter(key_parameter, element_value):
#     """Function to create a RevitAPI filter."""
#     f_parameter         = ParameterValueProvider(ElementId(key_parameter))  #sheet.SheetNumber
#     f_parameter_value   = element_value #e.g. element.Category.Id           #element.GetPara
#     f_rule              = FilterElementIdRule(f_parameter, FilterNumericEquals(), f_parameter_value)
#
#     return ElementParameterFilter(f_rule)
#
#
#
# random_view = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).FirstElement()
#
# def get_sheet_from_view():
#
#     sheet              = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
#
#     filter_sheets   = ElementCategoryFilter(BuiltInCategory.OST_Sheets)
#     filter_specific_view_id = []
#
#     list_of_filters = List[ElementFilter]()
#
#
#
#
#     filter = create_filter(key_parameter=BuiltInParameter.ELEM_TYPE_PARAM,
#                            element_value=element.GetTypeId())
#     list_of_filters.Add(filter)
#
#
#
#     if list_of_filters:
#         # COMBINE FILTERS
#         multiple_filters = LogicalOrFilter(list_of_filters)
#
#
#     elems = FilteredElementCollector(doc).WherePasses(multiple_filters).ToElementIds()




