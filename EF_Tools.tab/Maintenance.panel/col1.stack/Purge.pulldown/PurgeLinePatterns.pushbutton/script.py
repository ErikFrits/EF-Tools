# -*- coding: utf-8 -*-

#Date: 11.10.2019
__title__   = "Purge unused LinePatterns"
__doc__ = """Version = 1.0
Date    = 24.06.2024
_____________________________________________________________________
Description:
Purge Unused Line Patterns from your Revit Project.

To idenfity Unused Line Patterns:
- Check Object Styles
- View/ViewTemplate Overrides
- View Filters Overrides
- CAD Overrides

_____________________________________________________________________
How-To:
- Click the Button
- Select unused Line Patterns to purge
_____________________________________________________________________
Last update:
- [28.06.2024] - V1.0 RELEASE
_____________________________________________________________________
Author: Erik Frits from LearnRevitAPI.com"""



# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
from Autodesk.Revit.DB import *
from pyrevit import forms

from GUI.forms import select_from_dict

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application
doc   = __revit__.ActiveUIDocument.Document #type: Document

# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝

def get_line_style_ids():
    """Function to get all available LineStyles in the project."""
    # GET AVAILABLE LINE STYLES

    # Start Temp Transaction
    t = Transaction(doc,'Temp: Get LineStyles')
    t.Start()

    # Create Temp View
    view_type_draft = doc.GetDefaultElementTypeId(ElementTypeGroup.ViewTypeDrafting)
    temp_view = ViewDrafting.Create(doc, viewFamilyTypeId=view_type_draft)

    # Create Temp Line
    line_constructor = Line.CreateBound(XYZ(0, 0, 0), XYZ(4, 0, 0))
    default_line = doc.Create.NewDetailCurve(temp_view, line_constructor)

    # Get All LineStyles
    all_line_styles_ids = default_line.GetLineStyleIds()

    # Cancel Transaction
    t.RollBack()

    return all_line_styles_ids






def is_linepattern_solid(line_pattern_el):
    """Check if LinePatternElement is Solid or not."""
    linepattern = line_pattern_el.GetLinePattern()
    segments    = linepattern.GetSegments()

    if not segments:
        return True
    return False


# def get_category_LinePattern(cat):
#     ElementId = cat.GetLinePatternId(GraphicsStyleType.Projection)  # ElementId Object
#     if ElementId.ToString() == "-1":  # NoLinePattern assigned
#         return ""
#     elif ElementId.ToString() == "-3000010":  # BuiltIN: Solid linepattern assigned
#         return ""
#
#     else:  # Other Pattern Assigned
#         LinePatternElement = doc.GetElement(ElementId)  # Get LinePatternElement
#     return LinePatternElement
#
# def get_used_LinePatternElements(List):
#     used_LinePatternElements = []
#     for Category in all_Categories:
#         x = get_category_LinePattern(Category)
#         if x:
#             used_LinePatternElements.append(x)
#
#         for SubCategory in Category.SubCategories:
#             ElementId = SubCategory.GetLinePatternId(GraphicsStyleType.Projection)  # ElementId Object
#             if ElementId.ToString() == "-1":  # NoLinePattern assigned
#                 pass
#             elif ElementId.ToString() == "-3000010":  # BuiltIN: Solid linepattern assigned
#                 pass
#
#             else:  # Other Pattern Assigned
#                 LinePatternElement = doc.GetElement(ElementId)  # Get LinePatternElement
#                 used_LinePatternElements.append(LinePatternElement)  # append LinePatternElements that are in use
#     return used_LinePatternElements







# =====================================================================================================================================
# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝

# #B
# all_LinePatternsElements    = FilteredElementCollector(doc).OfClass(LinePatternElement).ToElements()
# all_Categories              = doc.Settings.Categories
# #A
# used_LinePatternElements    = get_used_LinePatternElements(all_Categories)  # used_LinePatternElements -> List of all LinePatternElements used in Object Styles, Imports, Line Styles, Schedules...
# filtered_LinePaternElements = exclude_LinePatternElements(used_LinePatternElements, "RLP")
# #C
# Solid_Patterns              = LinePatternIsSolid(all_LinePatternsElements)
#
# #Find unused patterns + Solid Line Patterns
# set_A = set([i.Name for i in filtered_LinePaternElements])
# set_B = set([i.Name for i in all_LinePatternsElements if "RLP" not in i.Name])
# set_C = set([i.Name for i in Solid_Patterns])  #exclude rlp :  if "RLP" not in i.Name
# set_DELETE = (set_B - set_A) | set_C # Names of unused LinePatternElements + Solid LinePatterns {Exclude all RLP}
#
# #Get List of unused LinePatternElements
# unused_linepatterns      = [i for i in all_LinePatternsElements if i.Name in set_DELETE]
# unused_linepatterns_dict = {lp.Name:lp for lp in unused_linepatterns}
# delete_linepatterns      = select_from_dict(unused_linepatterns_dict)
#
#
# if delete_linepatterns:
#     t = Transaction(doc, 'Delete LinePatterns')
#     t.Start()
#
#     for lp in delete_linepatterns:
#         print('Deleted LinePattern: {}'.format(lp.Name))
#         doc.Delete(lp.Id)
#     t.Commit()
#
#


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
#==================================================
#⏹️ Get All LinePatterns
todo = 'Can not read Built-In LineStyles.'
all_line_patterns = list(FilteredElementCollector(doc).OfClass(LinePatternElement).ToElements())
used_line_pattern_names = []


#1️⃣ Check LineStyles
linestyle_ids = get_line_style_ids()
linestyles    = [doc.GetElement(l_id) for l_id in linestyle_ids]

for ls in linestyles: #type: GraphicsStyle
    # print('LineStyle {}'.format(ls))
    # print('LineStyle Name: {}'.format(ls.Name))

    # Access GraphicsStyle for the LineStyle
# #     # print(ls.GraphicsStyleType)
    gs_cat = ls.GraphicsStyleCategory
#     print('GraphicStyleCategory: {}'.format(gs_cat))
# #     print('GraphicStyleCategory Name: {}'.format(gs_cat.Name))

    lp_id = gs_cat.GetLinePatternId(GraphicsStyleType.Projection)
#     print('LinePatternId: {}'.format(lp_id))

    if lp_id != ElementId(-1):
        # line_pattern = LinePatternElement.GetLinePatternElement(doc, lp_id)
        line_pattern = LinePatternElement.GetLinePattern(doc, lp_id)

#         print('Line Pattern: {}'.format(line_pattern.Name))

        if int(str(lp_id)) > 0: #ignore Built-In Patterns, they all have negative ElementId e.g. -3000010
#             print(lp_id)
#             print('id above')
            lp = doc.GetElement(lp_id)
#             print(lp)
            used_line_pattern_names.append(lp.Name)
#             print('LinePatternName: {}'.format(lp.Name))
#     print('---')

# print('Total LinePatterns: {}'.format(len(all_line_patterns)))
# print('Used in LineStyle LinePatterns: {}'.format(len(used_line_pattern_names)))
# for lp_name in used_line_pattern_names:
#     print(lp_name)




# 2️⃣ Check View/ViewTemplate GraphicSettings


# GET ALL CATEGORIES
all_categories = doc.Settings.Categories

# FILTER TO ANNOTATION CATEGORIES
cats_model = [cat for cat in all_categories if cat.CategoryType == CategoryType.Model]
cats_annotation = [cat for cat in all_categories if cat.CategoryType == CategoryType.Annotation]
cats_analytical = [cat for cat in all_categories if cat.CategoryType == CategoryType.AnalyticalModel]
cats_internal = [cat for cat in all_categories if cat.CategoryType == CategoryType.Internal]




#👉 Get Views and ViewTemplates
all_views_and_vt = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views)\
                .WhereElementIsNotElementType().ToElements()
all_views  = [v for v in all_views_and_vt if not v.IsTemplate]
all_vts    = [v for v in all_views_and_vt if     v.IsTemplate]

def get_linepattern_names(overrides):
    # type: OverrideGraphicSettings
    used_line_patterns = []

    # Check Pattern Overrides
    line_pattern_cut = doc.GetElement(overrides.CutLinePatternId)
    if line_pattern_cut:
        if line_pattern_cut.Name not in used_line_patterns:
            used_line_patterns.append(line_pattern_cut.Name)

    # Check Projection Overrides
    line_pattern_projection = doc.GetElement(overrides.ProjectionLinePatternId)
    if line_pattern_projection:
        if line_pattern_projection.Name not in used_line_patterns:
            used_line_patterns.append(line_pattern_projection.Name)

    return used_line_patterns




for view in all_views_and_vt: #type: View
    print(view.Name)


    #2️⃣ Check Model Categories
    for cat in cats_model:

        cat_overrides = view.GetCategoryOverrides(cat.Id) #type: OverrideGraphicSettings

        # print(overrides)
        line_pattern_cut        = doc.GetElement(overrides.CutLinePatternId )
        line_pattern_projection = doc.GetElement(overrides.ProjectionLinePatternId )

        if line_pattern_cut and line_pattern_projection:
            print(line_pattern_cut.Name)
            print(line_pattern_projection.Name)

        if cat.Name == 'Walls':
            print('WALLS')

            for subcat in cat.SubCategories:
                print(subcat.Name)
                overrides = view.GetCategoryOverrides(subcat.Id)
                line_pattern_cut        = doc.GetElement(overrides.CutLinePatternId)
                line_pattern_projection = doc.GetElement(overrides.ProjectionLinePatternId)
                if line_pattern_cut:
                    print(line_pattern_cut.Name)

                if line_pattern_projection:
                    print(line_pattern_projection.Name)




    # Check Annotation Categories

    # Check Imports

    # Check View Filters

    # Check Analytical

    # Phase Overrides (Not Available in Revit API)

    break

#
# #TODO check view overrides
#
# # Check Object Styles
# cats = doc.Settings.Categories




# Phase Overrides (Not Available)
# https://forums.autodesk.com/t5/revit-api-forum/phase-graphic-overrides/td-p/5670583

# # Collect all phases in the document
# phases = FilteredElementCollector(doc).OfClass(Phase).ToElements()

# for phase in phases:
#     print(phase)
#     print(phase.Name)














# # Get all object styles?
# colle = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_ImportObjectStyles)
#
#
# cat = doc.Settings.Categories.get_Item(BuiltInCategory.OST_ImportObjectStyles)
# for importObjectStyle in cat.SubCategories:
#     print(importObjectStyle)
#
# # Here’s a macro that lists all subcategories of the Lines category:
#
# # public
# # void
# # GetListOfLinestyles(Document
# # doc )
# # {
# #     Category
# # c = doc.Settings.Categories.get_Item(
# #     BuiltInCategory.OST_Lines);
# #
# # CategoryNameMap
# # subcats = c.SubCategories;
# #
# # foreach(Category
# # lineStyle in subcats )
# # {
# #     TaskDialog.Show("Line style", string.Format(
# #         "Linestyle {0} id {1}", lineStyle.Name,
# #         lineStyle.Id.ToString()));
# # }
# # }
#
#
#
#
#
#
