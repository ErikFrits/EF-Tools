# -*- coding: utf-8 -*-
__title__   = "Element Sections Generator"
__version__ = 'Version = 0.2 (Beta)'
__doc__ = """Date    = 31.03.2024
_____________________________________________________________________
Description:
...

_____________________________________________________________________
Author: Erik Frits"""
# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
from Autodesk.Revit.UI.Selection import ISelectionFilter, ObjectType
from Autodesk.Revit.DB import *
import traceback

# pyRevit Imports
from pyrevit import script, forms

# Custom EF Imports
from Snippets._vectors import rotate_vector
from Snippets._views import SectionGenerator
from GUI.forms import select_from_dict


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
uidoc     = __revit__.ActiveUIDocument
doc       = __revit__.ActiveUIDocument.Document #type: Document

output = script.get_output()


# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝
def place_views_on_sheet(doc, views, new_sheet):
    positions = [
        XYZ(-0.85,0.65,0),
        XYZ(-0.5,0.65,0),
        XYZ(-0.85, 0.35,0)
    ]

    for n, view in enumerate(views):


        if Viewport.CanAddViewToSheet(doc, new_sheet.Id, view.Id):
            # ⏺️ Define position for placing views
            pt = positions[n]

            # 🖼️ Place Views on Sheets
            viewport = Viewport.Create(doc, new_sheet.Id, view.Id, pt)


# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝
class ElementProperties():
    """Helper Class to get necessary parameters based on the type of elements"""
    origin = None #type: XYZ
    vector = None #type: XYZ
    width  = None #type: float
    height = None #type: float

    offset       = 1.0 #type: float
    depth        = 1.0 #type: float
    depth_offset = 1.0 #type: float

    valid = False

    def __init__(self, el):
        self.el = el


        if type(el) == Wall:
            self.get_wall_properties()

        else:
            self.get_generic_properties()

        # elif el.Category.Id == ElementId(BuiltInCategory.OST_Windows):
        #     self.get_window_properties()
        #
        # elif el.Category.Id == ElementId(BuiltInCategory.OST_Doors):
        #     self.get_door_properties()


    # ╦ ╦╔═╗╦  ╦  ╔═╗
    # ║║║╠═╣║  ║  ╚═╗
    # ╚╩╝╩ ╩╩═╝╩═╝╚═╝ ✅WALLS
    def get_wall_properties(self):
        #TODO Include Walls inside of Generic Rules (2nd Curve Based)
        wall_curve  = self.el.Location.Curve         # type: Curve
        pt_start    = wall_curve.GetEndPoint(0)      # type: XYZ
        pt_end      = wall_curve.GetEndPoint(1)      # type: XYZ
        self.vector = pt_end - pt_start              # type: XYZ
        self.width  = self.vector.GetLength()        # type: float
        self.height = self.el.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).AsDouble()  # type: Float

        BB      = self.el.get_BoundingBox(None)
        self.origin = (BB.Max + BB.Min) / 2  # type: XYZ

    # ╔═╗╔═╗╔╗╔╔═╗╦═╗╦╔═╗
    # ║ ╦║╣ ║║║║╣ ╠╦╝║║
    # ╚═╝╚═╝╝╚╝╚═╝╩╚═╩╚═╝ GENERIC
    def get_generic_properties(self):
        el_type = doc.GetElement(self.el.GetTypeId())
        BB      = self.el.get_BoundingBox(None)
        BB_typ  = el_type.get_BoundingBox(None)


        el_fam  = el_type.Family
        el_placement = el_fam.FamilyPlacementType
        fpt = FamilyPlacementType

        #1️⃣ POINT BASED
        if el_placement in [fpt.OneLevelBased, fpt.TwoLevelsBased, fpt.WorkPlaneBased]:

            # Get Points
            self.origin = (BB.Max + BB.Min) / 2  # type: XYZ


            self.width  = (BB_typ.Max.X - BB_typ.Min.X)  # type: float
            self.height = (BB_typ.Max.Z - BB_typ.Min.Z)  # type: float
            self.depth  = (BB_typ.Max.Y - BB_typ.Min.Y)  # type: float


            pt_start = XYZ(BB_typ.Min.X, (BB_typ.Min.Y + BB_typ.Max.Y) / 2, BB_typ.Min.Z)  # type : XYZ
            pt_end   = XYZ(BB_typ.Max.X, (BB_typ.Min.Y + BB_typ.Max.Y) / 2, BB_typ.Min.Z)  # type : XYZ

            self.vector       = pt_end - pt_start                    # type : XYZ
            try:
                rotation_rad = self.el.Location.Rotation            # type: float
                self.vector  = rotate_vector(self.vector, rotation_rad)  # type : XYZ
            except:
                pass

            return

        #2️⃣ CURVE BASED
        elif el_placement in [fpt.CurveBased, fpt.CurveDrivenStructural]:
            curve = self.el.Location.Curve

            self.origin = (BB.Max + BB.Min) / 2  #type: XYZ
            pt_start    = curve.GetEndPoint(0)   #type: XYZ
            pt_end      = curve.GetEndPoint(1)   #type: XYZ

            if pt_start.Z != pt_end.Z:
                # Match Z Coordinate
                pt_start = XYZ(pt_start.X,pt_start.Y,pt_start.Z)
                pt_end   = XYZ(pt_end.X  ,pt_end.Y  ,pt_start.Z)

            self.vector = pt_end - pt_start      #type: XYZ

            # Get Dimensions
            self.width = self.vector.GetLength()        #type: float
            self.height = (BB.Max.Z - BB.Min.Z) #type: float
            return


        #3️⃣ Hosted
        elif el_placement == fpt.OneLevelBasedHosted:
            host = self.el.Host

            if type(host) == Wall:
                wall_curve = host.Location.Curve        # type: Curve
                pt_start = wall_curve.GetEndPoint(0)    # type: XYZ
                pt_end = wall_curve.GetEndPoint(1)      # type: XYZ
                self.vector = pt_end - pt_start         # type: XYZ

                try:
                    if self.el.FacingFlipped:
                        self.vector = -self.vector
                except:
                    pass


                self.origin = (BB.Max + BB.Min) / 2     # type: XYZ
                self.width  = (BB_typ.Max.X - BB_typ.Min.X)  # type: float
                self.height = (BB_typ.Max.Z - BB_typ.Min.Z)  # type: float
                return

        else:

            # Get Points
            self.origin = (BB.Max + BB.Min) / 2  # type: XYZ


            self.width  = (BB_typ.Max.X - BB_typ.Min.X)  # type: float
            self.height = (BB_typ.Max.Z - BB_typ.Min.Z)  # type: float
            self.depth  = (BB_typ.Max.Y - BB_typ.Min.Y)  # type: float


            pt_start = XYZ(BB_typ.Min.X, (BB_typ.Min.Y + BB_typ.Max.Y) / 2, BB_typ.Min.Z)  # type : XYZ
            pt_end   = XYZ(BB_typ.Max.X, (BB_typ.Min.Y + BB_typ.Max.Y) / 2, BB_typ.Min.Z)  # type : XYZ

            self.vector       = pt_end - pt_start                    # type : XYZ
            try:
                rotation_rad = self.el.Location.Rotation            # type: float
                self.vector  = rotate_vector(self.vector, rotation_rad)  # type : XYZ
            except:
                pass
            return


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
#----------------------------------------------------------------------
# 1️⃣ User Input - Select Elements
bic = BuiltInCategory
select_opts = {'Walls'             : bic.OST_Walls,
              'Windows'            : bic.OST_Windows,
              'Doors'              : bic.OST_Doors,
              'Columns'            : [bic.OST_Columns, bic.OST_StructuralColumns],
              'Beams/Framing'      : bic.OST_StructuralFraming,
              'Furniture'          : [bic.OST_Furniture, bic.OST_FurnitureSystems],
              'Plumbing Fixtures'  : [bic.OST_Furniture, bic.OST_PlumbingFixtures],
              'Generic Models'     : bic.OST_GenericModel,
              'Casework'           : bic.OST_Casework,
              'Curtain Walls'     : bic.OST_Walls,
              'Lighting Fixtures'  : bic.OST_LightingFixtures,
              'Mass'               : bic.OST_Mass,
              'Parking'            : bic.OST_Parking,
              'All Loadable Families': FamilyInstance,
              'Electrical Fixtures, Equipment, Circuits' : [bic.OST_ElectricalFixtures, bic.OST_ElectricalEquipment, bic.OST_ElectricalCircuit]
              }

#👉 Pick Selection Opts
selected_opts = select_from_dict(select_opts,
                            title = __title__,
                            label = 'Select Categories to Pick Elements',
                            version = __version__,
                            SelectMultiple = True)


#⬇️ Flatten List to break nested lists
def flatten_list(lst):
    new_lst = []
    for i in lst:
        if isinstance(i,list):
            new_lst += i
        else:
            new_lst.append(i)
    return new_lst

selected_opts = flatten_list(selected_opts)

if not selected_opts:
    forms.alert('No Category was selected. Please Try Again.', title=__title__, exitscript=True)
#----------------------------------------------------------------------
#2️⃣ Select Elements

class EF_SelectionFilter(ISelectionFilter):
    def __init__(self, list_types_or_cats):
        """ ISelectionFilter made to filter with types
        :param allowed_types: list of allowed Types"""

        # Convert BuiltInCategories to ElementIds, Keep Types the Same.
        self.list_types_or_cats = [ElementId(i) if type(i) == BuiltInCategory else i for i in list_types_or_cats]

    def AllowElement(self, element):
        if element.ViewSpecific:
            return False

        #🅰️ Check if Element's Type in Allowed List
        if type(element) in self.list_types_or_cats:
            return True

        #🅱️ Check if Element's Category in Allowed List
        elif element.Category.Id in self.list_types_or_cats:
            return True

selected_elems = []
try:
    ISF = EF_SelectionFilter(selected_opts)
    with forms.WarningBar(title='Select Elements and click "Finish"'):
        ref_selected_elems = uidoc.Selection.PickObjects(ObjectType.Element,ISF)

    selected_elems         = [doc.GetElement(ref) for ref in ref_selected_elems]
except:
    pass


#----------------------------------------------------------------------
#3️⃣ Ensure Elements Selected, Exit if Not
if not selected_elems:
    error_msg = 'No Elements were selected.\nPlease Try Again'
    forms.alert(error_msg, title='Selection has Failed.', exitscript=True)


#----------------------------------------------------------------------
#4️⃣ Ask ViewTemplate for Sections
views               = FilteredElementCollector(doc).OfClass(View).ToElements()
dict_view_templates = {v.Name:v for v in views if v.IsTemplate}
dict_view_templates['None'] = None


#👉 Pick Selection Opts
sel_view_template = select_from_dict(dict_view_templates,
                            title = __title__,
                            label = 'Select ViewTemplate for Sections',
                            version = __version__,
                            SelectMultiple = False) #type: list

if sel_view_template:
    sel_view_template = sel_view_template[0]


#----------------------------------------------------------------------
#🔏 Transaction
t = Transaction(doc, 'EF_Section Generator')
t.Start() #🔓

table_data = []
new_views  = []

from pyrevit.forms import ProgressBar

counter = 0
max_value = len(selected_elems)
with ProgressBar(cancellable=True) as pb:
    for el in selected_elems:
        if pb.cancelled:
            break

        counter +=1
        pb.update_progress(counter, max_value)

        try:
            #4️⃣ Get Element Properties
            E = ElementProperties(el)

            #5️⃣ Create Section Generator
            gen             = SectionGenerator(doc,
                                               origin       = E.origin,
                                               vector       = E.vector,
                                               width        = E.width,
                                               height       = E.height,
                                               offset       = E.offset,
                                               depth        = E.depth,
                                               depth_offset = E.depth_offset)

            el_type   = doc.GetElement(el.GetTypeId())
            type_name = Element.Name.GetValue(el_type)
            cat_name  = el.Category.Name

            view_name_base  = '{}_{}'.format(type_name,el.Id)
            elev,cross,plan = gen.create_sections(view_name_base=view_name_base)


            # Set Sections ViewTemplate
            if sel_view_template:
                elev.ViewTemplateId  = sel_view_template.Id
                cross.ViewTemplateId = sel_view_template.Id
                plan.ViewTemplateId  = sel_view_template.Id



            #6️⃣ Place Views on a New Sheet
            default_title_block_id = doc.GetDefaultFamilyTypeId(ElementId(BuiltInCategory.OST_TitleBlocks))
            new_sheet = ViewSheet.Create(doc, default_title_block_id)
            place_views_on_sheet(doc, [elev, cross, plan], new_sheet)

            # 📝 Rename Sheets
            sheet_number = 'EF_{}_{}'.format(type_name,el.Id)
            sheet_name   = '{} - Elev, Cross, Plan'.format(cat_name)

            #💡 Ensure Unique SheetNumber
            for i in range(10):
                try:
                    new_sheet.SheetNumber = sheet_number
                    new_sheet.Name        = sheet_name
                    break
                except:
                    sheet_number += '*'


            #✅ Create Table Row Data
            new_views.append( [new_sheet, elev, cross, plan] )

            row = [cat_name,type_name, output.linkify(el.Id), output.linkify(new_sheet.Id), output.linkify(elev.Id), output.linkify(cross.Id), output.linkify(plan.Id) ]
            table_data.append(row)

        except:
            output.log_error(traceback.format_exc())

t.Commit() #🔒



try:
    #👀 DISPLAY TABLE
    output.print_table(table_data=table_data,
                       title="New Sections",
                       columns=["Category","TypeName","Element", "Sheet", "Elevation", "Cross", "Plan"])
except:
    output.log_error(traceback.format_exc())





