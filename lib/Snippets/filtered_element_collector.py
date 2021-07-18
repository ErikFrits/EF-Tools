from Autodesk.Revit.DB import *

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application


# ELEMENTS
lines = FilteredElementCollector(doc, doc.ActiveView.Id).WherePasses(ElementClassFilter(CurveElement)).ToElements()

all_rooms               = FilteredElementCollector(doc).WherePasses(ElementCategoryFilter(BuiltInCategory.OST_Rooms)).ToElements()
all_worksets            = FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset).ToWorksets()
all_doors               = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()
all_windows             = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).WhereElementIsNotElementType().ToElements()
all_floors              = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElements()
all_structural_columns  = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralColumns).WhereElementIsNotElementType().ToElements()
all_columns             = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralColumns).WhereElementIsNotElementType().ToElements()
all_walls               = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
all_generic_models      = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()

# ANNOTATIONS
all_revision_clouds     = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_RevisionClouds).WhereElementIsNotElementType().ToElements()

# VIEWS
all_views               = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).ToElements()
all_sheets              = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()

# TAGS
view_window_tags        = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_WindowTags).WhereElementIsNotElementType().ToElements()
view_doors_tags         = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_DoorTags).WhereElementIsNotElementType().ToElements()

# DOC
all_Categories = doc.Settings.Categories

