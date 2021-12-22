# -*- coding: utf-8 -*-
__title__   = "Generate Graphics Overviews"
__author__  = "Erik Frits"
__version__ = "Version: 1.0"
__doc__ = """Version = 1.0
Date    = 10.12.2021
_____________________________________________________________________
Description:

Generate multiple overviews of your Graphics:
- LineStyles
- LinePatterns
- LineWeights
- FilledRegionTypes
- FilledRegion Drafting Patterns
- Materials
_____________________________________________________________________
How-to:

-> Click on the button
-> Change Settings(optional)
-> Click on Generate Overviews
_____________________________________________________________________
Last update:

- [21.12.2021] - 1.0 RELEASE
_____________________________________________________________________
To-Do:

- Move functions to lib 
_____________________________________________________________________"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#====================================================================================================
import  os
from pyrevit import forms
from Autodesk.Revit.DB import *

#>>>>>>>>>> CUSTOM IMPORTS
from Snippets._context_manager import ef_Transaction, try_except
from GUI.forms import my_WPF

#>>>>>>>>>> .NET IMPORTS
import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System")
from System.Collections.Generic import List
from System.Windows.Controls import ComboBoxItem
import wpf

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#====================================================================================================
PATH_SCRIPT = os.path.dirname(__file__)

uidoc   = __revit__.ActiveUIDocument
app     = __revit__.Application
doc     = __revit__.ActiveUIDocument.Document

# GET ELEMENTS
all_text_types = FilteredElementCollector(doc).OfClass(TextNoteType).WhereElementIsElementType().ToElements()
dict_all_text_types = {i.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString(): i for i in all_text_types}

all_filled_patterns = FilteredElementCollector(doc).OfClass(FillPatternElement).ToElements()
solid_fill_pattern  = [i for i in all_filled_patterns if i.GetFillPattern().IsSolidFill][0]


# SETTINGS
DEFAULT_SCALE = 100


# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
# ==================================================

def create_text_note(view, x ,y ,text, text_note_type):
    """Function to create a TextNote"""
    text = '-' if not text else text

    # TEXTNOTE
    text_note = TextNote.Create(doc, view.Id, XYZ(x, y, 0),text, text_note_type.Id)
    return text_note


def convert_cm_to_feet(length):
    """Function to convert cm to feet."""
    return UnitUtils.Convert(length,
                           DisplayUnitType.DUT_CENTIMETERS,
                           DisplayUnitType.DUT_DECIMAL_FEET)

def rename_view(view, view_name):
    """Function with try/except statement to rename view"""
    # RENAME VIEW
    for i in range(10):
        try:
            view.Name = view_name
            break
        except:
            view_name += '*'

def create_region(view, X, Y, region_width_cm=120, region_height_cm=60):

    # VARIABLES
    region_width    = convert_cm_to_feet(region_width_cm)
    region_height   = convert_cm_to_feet(region_height_cm)
    region_type_id = doc.GetDefaultElementTypeId(ElementTypeGroup.FilledRegionType)

    # CONTAINER
    elements_line_text = []

    # REGION POINTS
    points_0 = XYZ(X, Y, 0.0)
    points_1 = XYZ(X+region_width, Y, 0.0)
    points_2 = XYZ(X+region_width, Y-region_height, 0.0)
    points_3 = XYZ(X, Y-region_height, 0.0)
    points = [points_0, points_1, points_2, points_3, points_0]

    # CREATE BOUNDARY
    list_boundary = List[CurveLoop]()
    boundary = CurveLoop()

    for n, point in enumerate(points):
        if n == 4: break
        # LINE POINTS
        p1, p2 = points[n], points[n + 1]
        # LINE
        boundary.Append(Line.CreateBound(p1, p2))
    list_boundary.Add(boundary)

    filled_region = FilledRegion.Create(doc, region_type_id, view.Id, list_boundary)
    return filled_region




class MaterialParser:
    def __init__(self, view, material, region_height_cm, region_width_cm, region_spacing_cm, text_column_width_cm, text_type, row=0):
        self.row = row
        self.view     = view
        self.material = material
        self.name     = material.Name

        self.material_category  = material.MaterialCategory

        self.region_height_feet     = convert_cm_to_feet(region_height_cm)
        self.region_width_feet      = convert_cm_to_feet(region_width_cm)
        self.region_spacing_feet    = convert_cm_to_feet(region_spacing_cm)
        self.text_column_width_feet = convert_cm_to_feet(text_column_width_cm)
        self.text_type_id           = text_type.Id

        self.region_spacing_X = self.region_width_feet + self.region_spacing_feet
        self.region_spacing_Y = self.region_height_feet + self.region_spacing_feet


        # ╦╔╦╗╔═╗╔╗╔╔╦╗╔═╗╔╦╗╦ ╦  ╔╦╗╔═╗╔╦╗╔═╗
        # ║ ║║║╣ ║║║ ║ ║╣  ║ ╚╦╝   ║║╠═╣ ║ ╠═╣
        # ╩═╩╝╚═╝╝╚╝ ╩ ╚═╝ ╩  ╩   ═╩╝╩ ╩ ╩ ╩ ╩ IDENTETY DATA
        # ==================================================
        self.material_description = material.get_Parameter(BuiltInParameter.ALL_MODEL_DESCRIPTION).AsString()
        self.material_class       = material.MaterialClass
        self.material_comments    = material.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString()

        # ╔═╗╦ ╦╔═╗╔╦╗╦╔╗╔╔═╗
        # ╚═╗╠═╣╠═╣ ║║║║║║║ ╦
        # ╚═╝╩ ╩╩ ╩═╩╝╩╝╚╝╚═╝ SHADING
        # ==================================================
        self.colour = material.Color

        # ╔═╗╦ ╦╦═╗╔═╗╔═╗╔═╗╔═╗
        # ╚═╗║ ║╠╦╝╠╣ ╠═╣║  ║╣
        # ╚═╝╚═╝╩╚═╚  ╩ ╩╚═╝╚═╝ SURFACE
        # ==================================================

        self.surf_foreground_color      = material.SurfaceForegroundPatternColor
        self.surf_foreground_pattern_id = material.SurfaceForegroundPatternId
        self.surf_background_color      = material.SurfaceBackgroundPatternColor
        self.surf_background_pattern_id = material.SurfaceBackgroundPatternId


        # ╔═╗╦ ╦╔╦╗
        # ║  ║ ║ ║
        # ╚═╝╚═╝ ╩ CUT
        # ==================================================
        self.cut_foreground_color      = material.CutForegroundPatternColor
        self.cut_foreground_pattern_id = material.CutForegroundPatternId
        self.cut_background_color      = material.CutBackgroundPatternColor
        self.cut_background_pattern_id = material.CutBackgroundPatternId

        # WRITE HEADERS
        if self.row == 0:
            self.write_headers()
        # WRITE ROW
        self.write_row()

    def write_headers(self):
        """Function to write headers above material data."""
        X = 0
        Y = self.region_spacing_Y

        self.create_text_note(X, Y + self.region_spacing_Y, "Materials Overview:")
        self.create_text_note(X, Y, "Name:")
        X += self.text_column_width_feet *2

        # ///GRAPHICS
        self.create_text_note(X, Y, "Shading:")
        X += self.region_spacing_X
        self.create_text_note(X, Y, "Surface:")
        X += self.region_spacing_X
        self.create_text_note(X, Y, "Cut:")
        X += self.region_spacing_X *2

        # ///DATA
        self.create_text_note( X, Y, "Description:")
        X += self.text_column_width_feet
        self.create_text_note( X, Y, "Class:")
        X += self.text_column_width_feet
        self.create_text_note( X, Y, "Comments:")
        X += self.text_column_width_feet


    def create_text_note(self, x ,y ,text):
        """Function to create a TextNote"""
        text = '-' if not text else text
        # TEXTNOTE
        text_note = TextNote.Create(doc, self.view.Id, XYZ(x, y, 0),text, self.text_type_id)
        return text_note

    def create_region(self, X, Y):

        # VARIABLES
        region_type_id = doc.GetDefaultElementTypeId(ElementTypeGroup.FilledRegionType)

        # CONTAINER
        elements_line_text = []

        # REGION POINTS
        points_0 = XYZ(X, Y, 0.0)
        points_1 = XYZ(X + self.region_width_feet, Y, 0.0)
        points_2 = XYZ(X + self.region_width_feet, Y - self.region_height_feet, 0.0)
        points_3 = XYZ(X, Y - self.region_height_feet, 0.0)
        points = [points_0, points_1, points_2, points_3, points_0]

        # CREATE BOUNDARY
        list_boundary = List[CurveLoop]()
        boundary = CurveLoop()

        for n, point in enumerate(points):
            if n == 4: break
            # LINE POINTS
            p1, p2 = points[n], points[n + 1]
            # LINE
            boundary.Append(Line.CreateBound(p1, p2))
        list_boundary.Add(boundary)

        filled_region = FilledRegion.Create(doc, region_type_id, self.view.Id, list_boundary)
        return filled_region

    def override_regions_graphics(self, region, fg_pattern_id, fg_color, bg_pattern_id, bg_color):
        """Function to ovverride given region with the override settings.
        :param region:          Region to apply OverrideGraphicsSettings
        :param fg_pattern_id:   Foreground - Pattern id
        :param fg_color:        Foreground - Colour
        :param bg_pattern_id:   Background - Pattern id
        :param bg_color:        Background - Colour
        :return: None
        """
        try:
            override_settings = OverrideGraphicSettings()
            if fg_pattern_id != ElementId(-1):
                override_settings.SetSurfaceForegroundPatternId(fg_pattern_id)
                override_settings.SetSurfaceForegroundPatternColor(fg_color)
            else:
                override_settings.SetSurfaceForegroundPatternColor(Color(255,255,255))

            if bg_pattern_id != ElementId(-1):
                override_settings.SetSurfaceBackgroundPatternId(bg_pattern_id)
                override_settings.SetSurfaceBackgroundPatternColor(bg_color)
            else:
                override_settings.SetSurfaceBackgroundPatternColor(Color(255,255,255))

            self.view.SetElementOverrides(region.Id, override_settings)

        except:
            #DELETE REGIONS IF MODEL PATTERN IS USED
            doc.Delete(region.Id)


    def write_row(self):
        """Function to write a single row for the given material."""
        X = 0
        Y = -self.region_spacing_Y * self.row

        # NAME
        self.create_text_note(X,Y,self.name)
        X += self.text_column_width_feet *2

        # SHADING
        shading = self.create_region(X, Y)
        override_settings = OverrideGraphicSettings()

        with try_except():
            override_settings.SetSurfaceForegroundPatternColor(self.colour)
            override_settings.SetSurfaceForegroundPatternId(solid_fill_pattern.Id)
            self.view.SetElementOverrides(shading.Id, override_settings)
        X+= self.region_spacing_X

        # SURFACE
        surface = self.create_region(X, Y)
        self.override_regions_graphics(surface, self.surf_foreground_pattern_id, self.surf_foreground_color,
                                                self.surf_background_pattern_id, self.surf_background_color)
        X+= self.region_spacing_X

        # CUT
        cut = self.create_region(X, Y)
        self.override_regions_graphics(cut, self.cut_foreground_pattern_id, self.cut_foreground_color,
                                            self.cut_background_pattern_id, self.cut_background_color)
        X+= self.region_spacing_X *2


        # DESCRIPTION
        self.create_text_note(X,Y,self.material_description)
        X+= self.text_column_width_feet


        # CLASS
        self.create_text_note(X,Y,self.material_class)
        X+=self.text_column_width_feet

        # COMMENTS
        self.create_text_note(X,Y,self.material_comments)
        X+=self.text_column_width_feet



# MAIN FUNCTION
class OverviewsGenerator(my_WPF):
    def __init__(self):
        self.new_views = []
        self.new_sheet = None
        # GUI
        self.add_wpf_resource()
        path_xaml_file = os.path.join(PATH_SCRIPT, 'CreateOverviews.xaml')
        wpf.LoadComponent(self, path_xaml_file)
        self.add_items_to_comboBox()

        self.main_title.Text = __title__
        self.footer_version.Text = __version__

        # REVIT
        self.drafting_view_type = self.get_drafting_view_type()
        self.ShowDialog()




    def add_items_to_comboBox(self):
        """Function to add all TextNoteTypes to ComboBox(self.UI_text_type)."""
        for n, type in enumerate(all_text_types):
            item = ComboBoxItem()
            item.Content    = type.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()
            item.IsSelected = True if n==0 else False
            self.UI_text_type.Items.Add(item)


    #>>>>>>>>>> INHERIT WPF RESOURCES
    def add_wpf_resource(self):
        """Function to get resources from super()"""
        super(OverviewsGenerator, self).add_wpf_resource()

    def get_line_styles_id(self):
        """Function to get all available LineStyles in the project."""
        # GET AVAILABLE LINE STYLES
        st = SubTransaction(doc)
        st.Start()
        temp_view           = self.create_drafting_view()
        line_constructor    = Line.CreateBound(XYZ(0, 0, 0), XYZ(4, 0, 0))
        default_line        = doc.Create.NewDetailCurve(temp_view, line_constructor)
        all_line_styles_ids = default_line.GetLineStyleIds()
        st.RollBack()

        return all_line_styles_ids

    def get_drafting_view_type(self):
        """Function to get DraftingView Type."""
        # GET DRAFTING VIEW TYPE ID
        drafting_view_type_id = None
        for view_type in FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements():
            #FIXME CHECK IN GERMAN REVIT.
            if "Drafting View" == view_type.FamilyName:
                return view_type

    def create_drafting_view(self, name = ""):
        """Function to create DraftingView"""
        view = ViewDrafting.Create(doc, viewFamilyTypeId=self.drafting_view_type.Id)
        if name: view.Name = name
        view.Scale = DEFAULT_SCALE
        return view

    def create_lines_in_view(self, view, n_lines, scale = 100):
        """Function to create lines and text notes(optonal) in the given view."""
        # VARIABLES
        line_width      = convert_cm_to_feet(float(self.UI_line_width.Text) * scale / 100)
        line_spacing    = convert_cm_to_feet(float(self.UI_line_spacing.Text) * scale / 100)

        # CONTAINER
        new_lines = []

        # CREATE LINE DEFAULT ELEMENTS
        line_constructor = Line.CreateBound(XYZ(0, 0, 0), XYZ(line_width, 0, 0))
        default_line = doc.Create.NewDetailCurve(view, line_constructor)

        # CREATE LIST[ElementId]
        default_elements = List[ElementId]([default_line.Id,])

        for n in range(n_lines):
            # LOCATION POINT
            offset = -line_spacing * (n + 1)
            copy_location = XYZ(0, offset, 0)

            # COPY ELEMENTS
            new_elements_id = ElementTransformUtils.CopyElements(doc, default_elements, copy_location)
            new_line     = doc.GetElement(new_elements_id[0])

            new_lines.append(new_line)
        # DELETE DEFAULT ELEMENTS
        doc.Delete(default_elements)

        return new_lines

    def create_regions_and_text_in_view(self, view, n_regions):
        """Function to add Regions and TextNotes to the given view.
        :param view:            DraftingView where to draw everything.
        :param n_regions:       Number of Regions
        :param region_width:    Width(cm) of single Region
        :param region_height:   Height(cm) of single Region
        :param region_spacing:  Spacing(cm) between regions
        :return:                List of tuples(region, text)
        """
        # VARIABLES

        region_width   = convert_cm_to_feet(float(self.UI_region_width.Text))
        region_height  = convert_cm_to_feet(float(self.UI_region_height.Text))
        region_spacing = convert_cm_to_feet(float(self.UI_region_spacing.Text))

        # CONTAINER
        elements_line_text = []

        # CREATE DEFAULT ELEMENTS

        # REGION
        points_0 = XYZ(0.0         , 0.0          , 0.0)
        points_1 = XYZ(region_width, 0.0          , 0.0)
        points_2 = XYZ(region_width, region_height, 0.0)
        points_3 = XYZ(0.0         , region_height, 0.0)
        points   = [points_0,points_1,points_2,points_3,points_0]

        list_boundary = List[CurveLoop]()
        boundary = CurveLoop()

        for n,point in enumerate(points):
            if n == 4: break

            # LINE POINTS
            p1, p2 = points[n], points[n+1]

            # LINE
            boundary.Append(Line.CreateBound(p1, p2))

        list_boundary.Add(boundary)

        region_type_id = doc.GetDefaultElementTypeId(ElementTypeGroup.FilledRegionType)
        filled_region = FilledRegion.Create(doc, region_type_id, view.Id, list_boundary)

        # TEXTNOTE
        text_note_type = doc.GetDefaultElementTypeId(ElementTypeGroup.TextNoteType)
        default_text_note = TextNote.Create(doc, view.Id, XYZ(region_width + region_spacing, region_height-0.25, 0), 'Default TextNote', self.selected_text_type.Id)

        # CREATE LIST[ElementId]
        default_elements = List[ElementId]([filled_region.Id, default_text_note.Id])


        for n in range(n_regions):
            # LOCATION POINT
            offset        = (-region_spacing -region_height) * (n + 1)
            copy_location = XYZ(0, offset, 0)

            # COPY ELEMENTS
            new_elements = ElementTransformUtils.CopyElements(doc, default_elements, copy_location)
            new_textnote = doc.GetElement(new_elements[1]) if type(doc.GetElement(new_elements[1])) == TextNote else doc.GetElement(new_elements[0])
            new_region   = doc.GetElement(new_elements[0]) if type(doc.GetElement(new_elements[0])) != TextNote else doc.GetElement(new_elements[1])

            elements_line_text.append((new_region, new_textnote))

        # DELETE DEFAULT ELEMENTS
        doc.Delete(default_elements)

        return elements_line_text

    def create_lines_and_text_in_view(self, view, n_lines):
        """Function to create lines and text notes(optonal) in the given view."""
        # VARIABLES
        line_width   = convert_cm_to_feet(float(self.UI_line_width.Text))
        line_spacing = convert_cm_to_feet(float(self.UI_line_spacing.Text))
        text_spacing = line_width + line_spacing
        text_size = self.selected_text_type.get_Parameter(BuiltInParameter.TEXT_SIZE).AsDouble()

        # CONTAINER
        elements_line_text = []

        # CREATE LINE DEFAULT ELEMENTS
        line_constructor = Line.CreateBound(XYZ(0, 0, 0), XYZ(line_width, 0, 0))
        default_line = doc.Create.NewDetailCurve(view, line_constructor)
        default_text_note = TextNote.Create(doc,view.Id, XYZ(text_spacing, text_size*100, 0), 'Default TextNote', self.selected_text_type.Id) # Y adjusted for scale. Text * 100

        # CREATE LIST[ElementId]
        default_elements = List[ElementId]([default_line.Id, default_text_note.Id])

        for n in range(n_lines):
            # LOCATION POINT
            offset = -line_spacing * (n + 1)
            copy_location = XYZ(0, offset, 0)

            # COPY ELEMENTS
            new_elements = ElementTransformUtils.CopyElements(doc, default_elements, copy_location)
            new_textnote = doc.GetElement(new_elements[1]) if type(doc.GetElement(new_elements[1])) == TextNote else doc.GetElement(new_elements[0])
            new_line     = doc.GetElement(new_elements[0]) if type(doc.GetElement(new_elements[0])) != TextNote else doc.GetElement(new_elements[1])

            elements_line_text.append((new_line, new_textnote))
        # DELETE DEFAULT ELEMENTS
        doc.Delete(default_elements)

        return elements_line_text

    # ╦  ╦╔╗╔╔═╗  ╔═╗╔═╗╔╦╗╔╦╗╔═╗╦═╗╔╗╔╔═╗
    # ║  ║║║║║╣   ╠═╝╠═╣ ║  ║ ║╣ ╠╦╝║║║╚═╗
    # ╩═╝╩╝╚╝╚═╝  ╩  ╩ ╩ ╩  ╩ ╚═╝╩╚═╝╚╝╚═╝ LINE PATTERNS
    #==================================================
    def overview_linepatterns(self):
        """Function to generate a drafting view with overview of all LinePatterns."""
        print("===CREATING OVERVIEW - LINEPATTERNS==")
        # GET ALL LINE PATTERNS
        all_line_patterns = list(FilteredElementCollector(doc).OfClass(LinePatternElement).ToElements())
        all_line_patterns.sort(key=lambda x: x.Name, reverse=False)

        # CREATE VIEW
        view     = self.create_drafting_view()
        elements = self.create_lines_and_text_in_view(view,n_lines=len(all_line_patterns))
        #CREATE TEXT NOTE
        title_text = TextNote.Create(doc, view.Id, XYZ(0, convert_cm_to_feet(float(self.UI_line_spacing.Text)), 0), 'Line Patterns:', self.selected_text_type.Id)

        for n,lp in enumerate(all_line_patterns):
            # GET ELEMENTS
            line      = elements[n][0]
            text_note = elements[n][1]

            # CHANGE TEXT
            text_note.Text = lp.Name

            #OVERRIDE LINE
            override_settings = OverrideGraphicSettings()
            override_settings.SetProjectionLinePatternId(lp.Id)
            view.SetElementOverrides(line.Id, override_settings)

        # RENAME VIEW
        rename_view(view, view_name='py_Overview - LinePatterns')
        self.new_views.append(view)

    # ╦  ╦╔╗╔╔═╗  ╔═╗╔╦╗╦ ╦╦  ╔═╗╔═╗
    # ║  ║║║║║╣   ╚═╗ ║ ╚╦╝║  ║╣ ╚═╗
    # ╩═╝╩╝╚╝╚═╝  ╚═╝ ╩  ╩ ╩═╝╚═╝╚═╝ LINE STYLES
    #==================================================
    def overview_linestyles(self):
        """Function to generate a drafting view with overview of all LinePatterns."""
        print("===CREATING OVERVIEW - LINESTYLES==")

        # GET ALL LINE STYLES
        all_line_styles_ids = list(self.get_line_styles_id())
        all_line_styles_ids.sort(key=lambda x: doc.GetElement(x).Name, reverse=False)


        # CREATE VIEW
        view = self.create_drafting_view()
        elements = self.create_lines_and_text_in_view(view, n_lines=len(all_line_styles_ids))

        #CREATE TEXT NOTE
        title_text = TextNote.Create(doc, view.Id, XYZ(0, convert_cm_to_feet(float(self.UI_line_spacing.Text)), 0), 'Line Styles:', self.selected_text_type.Id)

        # LOOP THROUGH LINE STYLES
        for n,line_style_id in enumerate(all_line_styles_ids):
            line_style = doc.GetElement(line_style_id)

            # GET ELEMENTS
            line      = elements[n][0]
            text_note = elements[n][1]

            # APPLY LINE STYLE
            line_param_line_style = line.get_Parameter(BuiltInParameter.BUILDING_CURVE_GSTYLE)
            line_param_line_style.Set(line_style_id)

            # CHANGE TEXT
            text_note.Text = line_param_line_style.AsValueString()

        # RENAME VIEW
        rename_view(view, view_name='py_Overview - LineStyles')
        self.new_views.append(view)


    # ╦  ╦╔╗╔╔═╗  ╦ ╦╔═╗╦╔═╗╦ ╦╔╦╗╔═╗
    # ║  ║║║║║╣   ║║║║╣ ║║ ╦╠═╣ ║ ╚═╗
    # ╩═╝╩╝╚╝╚═╝  ╚╩╝╚═╝╩╚═╝╩ ╩ ╩ ╚═╝ LINE WEIGHTS
    #==================================================
    def overview_lineweights(self):
        """Function to create multiple DraftingViews with overview of LineWeights."""
        print("===CREATING OVERVIEW - LINEWEIGHTS==")

        # VARIABLES
        # scales = [10, 25, 50, 100, 200, 500]
        scales = [int(i) for i in self.UI_line_weights.Text.split(',')]

        if not scales:
            return

        for scale in scales:
            # VARIABLES
            line_spacing_cm = float(self.UI_line_spacing.Text)
            line_spacing_feet = convert_cm_to_feet(line_spacing_cm)

            # CREATE VIEW
            view = self.create_drafting_view()
            lines = self.create_lines_in_view(view, n_lines=16, scale=scale)

            # CREATE LINE WEIGHT TEXT IN FIRST SCALE
            if scale == scales[0]:
                # new_title_text = TextNote.Create(doc, view.Id, XYZ(0, line_spacing_feet, 0), 'Line Weights:', self.selected_text_type.Id)
                text_size = self.selected_text_type.get_Parameter(BuiltInParameter.TEXT_SIZE).AsDouble() * scale
                for n in range(16):
                    text_spacing = -line_spacing_feet * (n+1) / scale
                    text_note = TextNote.Create(doc, view.Id, XYZ(-0.4, text_spacing + text_size, 0), str(n+1), self.selected_text_type.Id)

            # LOOP THROUGH ELEMENTS
            for n in range(16):
                # CREATE TITLE TEXT
                text_note = TextNote.Create(doc, view.Id, XYZ(0, line_spacing_feet * scale / 100 , 0), "1:{}".format(scale), self.selected_text_type.Id)
                line      = lines[n]

                #OVERRIDE LINE
                override_settings = OverrideGraphicSettings()
                override_settings.SetProjectionLineWeight(n+1)
                view.SetElementOverrides(line.Id, override_settings)

            # SET SCALE
            view.Scale = scale
            # RENAME VIEW
            rename_view(view, view_name= 'py_Overview - LineWeights ' + str(scale))
            self.new_views.append(view)


    # ╦═╗╔═╗╔═╗╦╔═╗╔╗╔╔═╗
    # ╠╦╝║╣ ║ ╦║║ ║║║║╚═╗
    # ╩╚═╚═╝╚═╝╩╚═╝╝╚╝╚═╝ REGIONS
    #==================================================
    def overview_regions(self):
        print("===CREATING OVERVIEW - FILLED REGIONS==")
        # GET ALL FILLED REGIONS AND SORT
        all_filled_regions_types = list(FilteredElementCollector(doc).OfClass(FilledRegionType).ToElements())
        all_filled_regions_types.sort(key=lambda x: x.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString(), reverse=False)

        # CREATE VIEW
        view = self.create_drafting_view()
        elements = self.create_regions_and_text_in_view(view, n_regions=len(all_filled_regions_types))

        #CREATE TEXT NOTE
        title_text = TextNote.Create(doc, view.Id, XYZ(0, convert_cm_to_feet(float(self.UI_region_spacing.Text)), 0), 'Filled Regions:', self.selected_text_type.Id)

        for n, filled_region_type in enumerate(all_filled_regions_types):
            # GET ELEMENTS
            region    = elements[n][0]
            text_note = elements[n][1]

            # CHANGE TEXT
            text_note.Text = filled_region_type.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()

            # CHANGE TYPE
            region.ChangeTypeId(filled_region_type.Id)

        # RENAME VIEW
        rename_view(view, view_name='py_Overview - FilledRegions')
        self.new_views.append(view)

    # ╔╦╗╦═╗╔═╗╔═╗╔╦╗╦╔╗╔╔═╗  ╔═╗╔═╗╔╦╗╔╦╗╔═╗╦═╗╔╗╔╔═╗
    #  ║║╠╦╝╠═╣╠╣  ║ ║║║║║ ╦  ╠═╝╠═╣ ║  ║ ║╣ ╠╦╝║║║╚═╗
    # ═╩╝╩╚═╩ ╩╚   ╩ ╩╝╚╝╚═╝  ╩  ╩ ╩ ╩  ╩ ╚═╝╩╚═╝╚╝╚═╝ DRAFTING PATTERNS
    #==================================================
    def overview_drafting_patterns(self):
        print("===CREATING OVERVIEW - DRAFTING PATTERNS==")

        # GET ALL DRAFTING PATTERNS AND SORT
        all_filled_patterns = FilteredElementCollector(doc).OfClass(FillPatternElement).ToElements()
        all_drafting_filled_patterns = [i for i in all_filled_patterns if str(i.GetFillPattern().Target) == "Drafting"]
        all_drafting_filled_patterns.sort(key=lambda x: x.Name, reverse=False)


        # CREATE VIEW
        view = self.create_drafting_view()
        elements = self.create_regions_and_text_in_view(view, n_regions=len(all_drafting_filled_patterns))
        #CREATE TEXT NOTE
        title_text = TextNote.Create(doc, view.Id, XYZ(0, convert_cm_to_feet(float(self.UI_region_spacing.Text)), 0), 'Drafting Patterns:', self.selected_text_type.Id)


        for n, filled_pattern in enumerate(all_drafting_filled_patterns):
            # GET ELEMENTS
            region    = elements[n][0]
            text_note = elements[n][1]


            # CHANGE TEXT
            text_note.Text = filled_pattern.Name

            # APPLY DRAFTING FILLED PATTERN TO REGION
            override_settings = OverrideGraphicSettings()
            override_settings.SetSurfaceForegroundPatternId(filled_pattern.Id)
            override_settings.SetSurfaceForegroundPatternColor(Color(0,0,0))
            view.SetElementOverrides(region.Id, override_settings)

        # RENAME VIEW
        rename_view(view, view_name='py_Overview - DraftingPatterns')
        self.new_views.append(view)

    # ╔╦╗╔═╗╔╦╗╔═╗╦═╗╦╔═╗╦  ╔═╗
    # ║║║╠═╣ ║ ║╣ ╠╦╝║╠═╣║  ╚═╗
    # ╩ ╩╩ ╩ ╩ ╚═╝╩╚═╩╩ ╩╩═╝╚═╝ MATERIALS
    #==================================================
    def overview_materials(self):
        print("===CREATING OVERVIEW - MATERIALS==")

        # GET ALL MATERIALS AND SORT
        all_materials = FilteredElementCollector(doc).OfClass(Material)
        all_materials = list(all_materials)
        all_materials.sort(key=lambda x: x.Name, reverse=False)

        # CREATE VIEW
        view        = self.create_drafting_view()
        view.Scale  = 100

        # LOOP THROUGH MATERIALS
        for n,material in enumerate(all_materials):
            mat = MaterialParser(view, material,
                                 region_height_cm       = float(self.UI_material_box_height.Text),
                                 region_width_cm        = float(self.UI_material_box_width.Text),
                                 region_spacing_cm      = float(self.UI_material_box_spacing.Text),
                                 text_column_width_cm   = float(self.UI_material_column_width.Text),
                                 text_type              = self.selected_text_type,
                                 row=n)
        # RENAME VIEW
        rename_view(view, view_name='py_Overview - Materials')
        self.new_views.append(view)

    # ╔═╗╦ ╦╦  ╔═╗╦═╗╔═╗╔═╗╔═╗╦═╗╔╦╗╦╔═╗╔═╗
    # ║ ╦║ ║║  ╠═╝╠╦╝║ ║╠═╝║╣ ╠╦╝ ║ ║║╣ ╚═╗
    # ╚═╝╚═╝╩  ╩  ╩╚═╚═╝╩  ╚═╝╩╚═ ╩ ╩╚═╝╚═╝ GUI PROPERTIES
    #==================================================
    def PROPERTIES(self):
        # OVERVIEWS
        self.UI_checkbox_linestyles         = self.UI_checkbox_linestyles
        self.UI_checkbox_linepatterns       = self.UI_checkbox_linepatterns
        self.UI_checkbox_lineweights        = self.UI_checkbox_lineweights
        self.UI_checkbox_drafting_patterns  = self.UI_checkbox_drafting_patterns
        self.UI_checkbox_regions            = self.UI_checkbox_regions
        self.UI_checkbox_materials          = self.UI_checkbox_materials

        # TEXT TYPE
        self.UI_text_type                   = self.UI_text_type

        # LINE SETTINGS
        self.UI_line_width                  = self.UI_line_width
        self.UI_line_spacing                = self.UI_line_spacing
        self.UI_line_weights                = self.UI_line_weights

        # REGION SETTINGS
        self.UI_region_spacing              = self.UI_region_spacing
        self.UI_region_height               = self.UI_region_height
        self.UI_region_width                = self.UI_region_width

        # MATERIAL SETTINGS
        self.UI_material_box_width          = self.UI_material_box_width
        self.UI_material_box_height         = self.UI_material_box_height
        self.UI_material_box_spacing        = self.UI_material_box_spacing
        self.UI_material_column_width       = self.UI_material_column_width



    # ╔═╗╦ ╦╦  ╔═╗╦  ╦╔═╗╔╗╔╔╦╗╔═╗
    # ║ ╦║ ║║  ║╣ ╚╗╔╝║╣ ║║║ ║ ╚═╗
    # ╚═╝╚═╝╩  ╚═╝ ╚╝ ╚═╝╝╚╝ ╩ ╚═╝
    #==================================================
    def button_run(self, sender, e):
        self.selected_text_type = self.get_selected_text_type()
        self.Close()

        # CREATE OVERVIEWS
        with ef_Transaction(doc, __title__, debug=True):
            if self.UI_checkbox_linestyles.IsChecked:         self.overview_linestyles()
            if self.UI_checkbox_linepatterns.IsChecked:       self.overview_linepatterns()
            if self.UI_checkbox_lineweights.IsChecked:        self.overview_lineweights()
            if self.UI_checkbox_regions.IsChecked:            self.overview_regions()
            if self.UI_checkbox_drafting_patterns.IsChecked:  self.overview_drafting_patterns()
            if self.UI_checkbox_materials.IsChecked:          self.overview_materials()

        if self.new_views:
            with ef_Transaction(doc, "py_Placing Overviews on Sheet", debug=True):
                self.place_views_on_sheet()

    def place_views_on_sheet(self):
        print("===CREATING SHEET WITH OVERVIEWS===")
        # CREATE SHEET     all_title_blocks = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_TitleBlocks).WhereElementIsElementType().ToElements()
        new_sheet = ViewSheet.Create(doc, ElementId(-1))

        X = 0
        for view in self.new_views:
            Viewport.Create(doc, new_sheet.Id, view.Id, XYZ(X, 0, 0))
            X += 0.5

        self.new_sheet = new_sheet


    def get_selected_text_type(self):
        """Function to get selected item from self.UI_text_type."""
        for item in self.UI_text_type.Items:
            if item.IsSelected:
                text_type = dict_all_text_types[item.Content]
                return text_type




    # def UI_event_checked_line(self, sender, e):
    #     print("HEY")
    def UI_event_checked_overview(self, sender, e):
        import System

        # LINE OVERVIEWS
        if  not self.UI_checkbox_lineweights.IsChecked  and not self.UI_checkbox_linestyles.IsChecked and not self.UI_checkbox_linepatterns.IsChecked:
            self.UI_stack_line_settings.Visibility = System.Windows.Visibility.Collapsed
        else:
            self.UI_stack_line_settings.Visibility = System.Windows.Visibility.Visible

        # REGION OVERVIEWS
        if not self.UI_checkbox_regions.IsChecked and not self.UI_checkbox_drafting_patterns.IsChecked:
            self.UI_stack_region_settings.Visibility = System.Windows.Visibility.Collapsed
        else:
            self.UI_stack_region_settings.Visibility = System.Windows.Visibility.Visible

        # MATERIAL OVERVIEWS
        if not  self.UI_checkbox_materials.IsChecked:
            self.UI_stack_material_settings.Visibility = System.Windows.Visibility.Collapsed
        else:
            self.UI_stack_material_settings.Visibility = System.Windows.Visibility.Visible

        # ALL OVERVIEWS
        if not self.UI_checkbox_lineweights.IsChecked  and not self.UI_checkbox_linestyles.IsChecked  and not self.UI_checkbox_linepatterns.IsChecked  \
                and not self.UI_checkbox_drafting_patterns.IsChecked  and not self.UI_checkbox_regions.IsChecked  and not self.UI_checkbox_materials.IsChecked :
            self.UI_stack_button.Visibility = System.Windows.Visibility.Collapsed
            self.UI_stack_text_type.Visibility = System.Windows.Visibility.Collapsed
        else:
            self.UI_stack_button.Visibility = System.Windows.Visibility.Visible
            self.UI_stack_text_type.Visibility = System.Windows.Visibility.Visible

        # LINE WEIGHTS SETTING
        if self.UI_checkbox_lineweights.IsChecked == False:
            self.UI_dock_lineweight_scale.Visibility = System.Windows.Visibility.Collapsed
        else:
            self.UI_dock_lineweight_scale.Visibility = System.Windows.Visibility.Visible


if __name__ == '__main__':
    gen = OverviewsGenerator()

    # CHANGE ACTIVE VIEW
    if gen.new_sheet:
        uidoc.ActiveView = gen.new_sheet
