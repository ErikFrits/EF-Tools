# -*- coding: UTF-8 -*-
from pyrevit.preflight import PreflightTestCase
from pyrevit import script, revit, DB

output = script.get_output()
output.close_others()
doc = revit.doc

# get the linked documents
links_instances = DB.FilteredElementCollector(doc).OfClass(DB.RevitLinkInstance).ToElements()
if links_instances:
    link_docs = []
    for link in links_instances:
        link_doc = link.GetLinkDocument()
        link_docs.append(link_doc)


def ef_tools_check(document = doc, op = output):
    # get the document info
    document_info(document, op)
    # get the walls
    walls_info(document, op)
    # get the grids
    grids_info(document, op)


def walls_info(document, op):
    walls = DB.FilteredElementCollector(document).OfCategory(DB.BuiltInCategory.OST_Walls)
    walls_instances = walls.WhereElementIsNotElementType()
    #get the wall count
    walls_count = walls_instances.GetElementCount()
    op.print_md("**Walls: **{}".format(walls_count))
    # get the wall name
    walls_names = [wall.Name for wall in walls_instances]
    # get the wall id
    walls_ids = []
    for wall in walls_instances.ToElements():
        walls_ids.append(op.linkify(wall.Id))
    # get wall length
    wall_length = []
    for wall in walls_instances.ToElements():
        try:
            wall_length.append(wall.get_Parameter(DB.BuiltInParameter.CURVE_ELEM_LENGTH).AsValueString()+"mm")
        except:
            wall_length.append("N/A")

    op.print_table(title="Walls", columns=["Wall name", "Wall id", "Wall Length"], table_data=zip(walls_names, walls_ids, wall_length))


def grids_info(document, op):
    grids = DB.FilteredElementCollector(document).OfCategory(DB.BuiltInCategory.OST_Grids)
    grid_instances = grids.WhereElementIsNotElementType()
    #get the grid count
    grids_count = grid_instances.GetElementCount()
    op.print_md("**Grids: **{}".format(grids_count))
    # get the grid name
    grid_names = [grid.Name for grid in grid_instances]
    # get the grid id
    grids_ids = []
    for grid in grid_instances.ToElements():
        grids_ids.append(op.linkify(grid.Id))
    # get grid workset
    worksets = []
    for grid in grid_instances.ToElements():
        try:
            worksets.append(grid.get_Parameter(DB.BuiltInParameter.ELEM_PARTITION_PARAM).AsValueString())
        except:
            worksets.append("N/A")

    op.print_table(title="Grids", columns=["Grids name", "Grids id", "Workset"], table_data=zip(grid_names, grids_ids, worksets))


def document_info(document, op):
    op.print_md("# Ef_tools check")
    # get the project name
    project_title = document.Title
    project_name = document.ProjectInformation.Name
    # get the project number
    project_number = document.ProjectInformation.Number
    # get the project address
    project_address = document.ProjectInformation.Address

    op.print_md("## Project Info")
    op.print_md("###{}".format(project_name))
    op.print_md(project_title)
    op.print_md(project_number)
    op.print_md(project_address)


class ModelChecker(PreflightTestCase):
    """
    List all walls and their info and get some of the model info
    This QC tools returns you with the following data:
        Model info: project name, project number, project address
        Wall count, wall name, wall id
        Grid count, grid name, grid id, grid workset
    """

    name = "EF_tools Masterclass Example Check"
    author = "Jean-Marc Couffin"


    def setUp(self, doc, output):
        pass


    def startTest(self, doc, output):
        ef_tools_check()
        for link_doc in link_docs:
            if link_doc:
                ef_tools_check(link_doc)


    def tearDown(self, doc, output):
        pass


    def doCleanups(self, doc, output):
        pass


