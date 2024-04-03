# -*- coding: utf-8 -*-
# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ==================================================
from pyrevit import forms
from Autodesk.Revit.DB import *

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ==================================================
uidoc    = __revit__.ActiveUIDocument
doc      = __revit__.ActiveUIDocument.Document
app      = __revit__.Application
rvt_year = int(app.VersionNumber)

# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
# ==================================================
def create_string_equals_filter(key_parameter, element_value, caseSensitive = True):
    """Function to create ElementParameterFilter based on FilterStringRule."""
    f_parameter         = ParameterValueProvider(ElementId(key_parameter))
    f_parameter_value   = element_value

    if rvt_year < 2022:
        f_rule = FilterStringRule(f_parameter, FilterStringEquals(), f_parameter_value, caseSensitive)
    else:
        f_rule = FilterStringRule(f_parameter, FilterStringEquals(), f_parameter_value)

    return ElementParameterFilter(f_rule)

def get_sheet_from_view(view):
    #type:(View) -> ViewPlan
    """Function to get ViewSheet associated with the given ViewPlan"""

    #>>>>>>>>>> CREATE FILTER
    my_filter = create_string_equals_filter(key_parameter=BuiltInParameter.SHEET_NUMBER,
                                            element_value=view.get_Parameter(BuiltInParameter.VIEWER_SHEET_NUMBER).AsString() )
    #>>>>>>>>>> GET SHEET
    return FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().WherePasses(my_filter).FirstElement()

# CREATE VIEW
def create_3D_view(uidoc, name=''):
    """Function to Create a 3D view.
    :param uidoc: UI Document of a project where View should be created
    :param name:  New View Name. '*' will be added in the end if name is not unique.
    :return:      Create 3D View"""

    # GET 3D VIEW TYPE
    all_view_types = FilteredElementCollector(uidoc.Document).OfClass(ViewFamilyType).ToElements()
    all_3D_Types = [i for i in all_view_types if i.ViewFamily == ViewFamily.ThreeDimensional]
    view_type_3D = all_3D_Types[0]

    # CREATE VIEW
    view = View3D.CreateIsometric(uidoc.Document, view_type_3D.Id)

    # RENAME VIEW
    for i in range(50):
        try:
            view.Name = name
            break
        except:
            name += '*'

    return view







# ╔═╗╔═╗╔═╗╔╦╗╔═╗╔╗╔  ╔═╗╔═╗╔╗╔╔═╗╦═╗╔═╗╔╦╗╔═╗╦═╗
# ╚═╗║╣ ║   ║ ║ ║║║║  ║ ╦║╣ ║║║║╣ ╠╦╝╠═╣ ║ ║ ║╠╦╝
# ╚═╝╚═╝╚═╝ ╩ ╚═╝╝╚╝  ╚═╝╚═╝╝╚╝╚═╝╩╚═╩ ╩ ╩ ╚═╝╩╚═



class SectionGenerator():
    """

    Example:
        # Create Sections
        gen             = SectionGenerator(origin, vector, width, height, offset=1, depth=1, depth_offset=1)
        view_name_base  = 'Wall_{}'.format(wall.Id)
        gen.create_sections(view_name_base=view_name_base)"""
    def __init__(self, doc, origin, vector, width=1, height=1, offset=1, depth=1, depth_offset=1):
        """General class to create Sections and place them on sheets"""
        #type: XYZ, XYZ, float, float, float, float, float
        self.doc          = doc
        self.origin       = origin
        self.vector       = vector
        self.width        = width
        self.height       = height
        self.offset       = offset
        self.depth        = depth
        self.depth_offset = depth_offset


        scale            = None
        view_template    = None
        title_block_type = None
        section_type     = None


    def create_transform(self, mode = 'elevation'):
        """Function to create Transform for correct location
        :arg: mode
        :returns: Transform

        Needs:
        - origin
        - vector
        """

        #⏺️ CREATE TRANSFORM + ASSIGN ORIGIN
        trans        = Transform.Identity  # Create Instance of Transform
        trans.Origin = self.origin  # Set Origin Point (Window Insertion Point)

        #📐 NORMILIZE VECTOR
        vector = self.vector.Normalize()
        # if rotate:
        #     vector = vector * -1

        #1️⃣ ELEVATION
        if mode.lower() == 'elevation':
            trans.BasisX = vector
            trans.BasisY = XYZ.BasisZ
            trans.BasisZ = vector.CrossProduct(XYZ.BasisZ)
            # The cross product is defined as the vector which is perpendicular to both vectors

        #2️⃣ CROSS-SECTION
        elif mode.lower() == 'cross':
            vector_cross = vector.CrossProduct(XYZ.BasisZ)

            trans.BasisX = vector_cross
            trans.BasisY = XYZ.BasisZ
            trans.BasisZ = vector_cross.CrossProduct(XYZ.BasisZ)

        #3️⃣ - PLAN
        elif mode.lower() == 'plan':
            trans.BasisX = -vector
            trans.BasisY = -XYZ.BasisZ.CrossProduct(-vector).Normalize()
            trans.BasisZ = -XYZ.BasisZ

        return trans


    def create_section_box(self, mode='elevation'):
        """
        mode = ['elevation', 'cross', 'plan']
        """

        section_box = BoundingBoxXYZ()  # origin 0,0,0
        trans       = self.create_transform(mode=mode)

        W_half = self.width / 2
        H_half = self.height / 2
        D_half = self.depth / 2

        if mode == 'elevation':
            #1️⃣ SectionBox for Elevation (Offset section a bit)
            half            = self.width / 2
            section_box.Min = XYZ(-half - self.offset,  -H_half - self.offset,   0)
            section_box.Max = XYZ(half + self.offset ,   H_half + self.offset,  D_half + self.offset)

        elif  mode == 'cross':
            #1️⃣ SectionBox for Elevation
            section_box.Min = XYZ(-D_half - self.offset,  -H_half - self.offset, 0 )
            section_box.Max = XYZ(D_half + self.offset ,   H_half + self.offset, W_half + self.offset)
            # X - Width | Y - Height | Z - Depth

        elif mode =='plan':
            # 1️⃣ SectionBox for Elevation
            section_box.Min = XYZ(-W_half - self.offset, -D_half - self.offset  , 0)
            section_box.Max = XYZ(W_half + self.offset,  D_half + self.offset   , H_half + self.offset)


        section_box.Transform = trans  # Apply Transform (Origin + XYZ Vectors)

        return section_box

    def rename_view(self, view, new_name):
        for i in range(10):
            try:
                view.Name = new_name
                break
            except:
                new_name += '*'





    def create_sections(self, view_name_base):

        # Create SectionBoxes
        section_box_elev  = self.create_section_box('elevation')
        section_box_cross = self.create_section_box('cross')
        section_box_plan  = self.create_section_box('plan')

        # Create Sections
        section_type_id = self.doc.GetDefaultElementTypeId(ElementTypeGroup.ViewTypeSection)
        section_elev    = ViewSection.CreateSection(self.doc, section_type_id, section_box_elev)
        section_cross   = ViewSection.CreateSection(self.doc, section_type_id, section_box_cross)
        section_plan    = ViewSection.CreateSection(self.doc, section_type_id, section_box_plan)

        # Create New Names
        new_name_elev  = '{}_Elevation'.format(view_name_base)
        new_name_cross = '{}_Cross'.format(view_name_base)
        new_name_plan  = '{}_Plan'.format(view_name_base)

        # Rename Views
        self.rename_view(section_elev,  new_name_elev)
        self.rename_view(section_cross, new_name_cross)
        self.rename_view(section_plan,  new_name_plan)


        # # Print Linkify
        # from pyrevit import script
        # output = script.get_output()
        # print('Elevation: {}'.format(output.linkify(section_elev.Id)))
        # print('Cross    : {}'.format(output.linkify(section_cross.Id)))
        # print('Plan     : {}'.format(output.linkify(section_plan.Id)))

        return (section_elev, section_cross, section_plan)






