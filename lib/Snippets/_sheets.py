from Autodesk.Revit.DB import (FilteredElementCollector,
                               ElementId,
                               ViewSheet,
                               BuiltInCategory)
default_uidoc = __revit__.ActiveUIDocument
default_doc = default_uidoc.Document




def get_views_on_sheet(sheet, uidoc=default_uidoc):
    """Function to return all views found on the given sheet."""
    doc = uidoc.Document
    viewports_ids   = sheet.GetAllViewports()
    viewports       = [doc.GetElement(viewport_id)  for viewport_id in viewports_ids]
    views_ids       = [viewport.ViewId              for viewport    in viewports]
    views           = [doc.GetElement(view_id)      for view_id     in views_ids]
    return views


def get_titleblock_on_sheet(sheet, uidoc=default_uidoc):
    """Function to get TitleBlock from given ViewSheet.
    It will not return any TitleBlocks if there are more than 1 on ViewSheet.
    :returns TitleBlock"""
    doc = uidoc.Document

    all_TitleBlocks = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_TitleBlocks).WhereElementIsNotElementType().ToElements()
    title_blocks_on_sheet = []

    for title_block in all_TitleBlocks:
        if title_block.OwnerViewId == sheet.Id:
            title_blocks_on_sheet.append(title_block)

    if not title_blocks_on_sheet:
        print("***No TitleBlocks were found on given ViewSheet ({}***".format(sheet.SheetNumber))

    elif len(title_blocks_on_sheet) > 1:
        print("***There are more than 1 TitleBlock on given ViewSheet ({})****".format(sheet.SheetNumber))

    else:
        return title_blocks_on_sheet[0]