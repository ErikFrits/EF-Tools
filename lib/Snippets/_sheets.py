
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document




def get_views_on_sheet(sheet):
    """Function to return all views found on the given sheet."""
    viewports_ids   = sheet.GetAllViewports()
    viewports       = [doc.GetElement(viewport_id)  for viewport_id in viewports_ids]
    views_ids       = [viewport.ViewId              for viewport    in viewports]
    views           = [doc.GetElement(view_id)      for view_id     in views_ids]
    return views

