# -*- coding: utf-8 -*-
__title__   = "Align Viewports"
__author__  = "Erik Frits"
__doc__ = """Version = 1.1
Date    = 08.11.2021
_____________________________________________________________________
Description:

This tool will align ViewPlans on selected sheets. 
It will hide everything from views, align them and then unhide.

Optional Settings:
- apply same CropBox/ScopeBox 
- Overlap multiple ViewPlans(same scale)
- align Legends(if same)
- apply same TitleBlock Type
_____________________________________________________________________
How-to:

-> Select Sheets in your ProjectBrowser
-> Run the script
-> Select settings if necessary
-> Click on Align Viewports
_____________________________________________________________________
Last update:
- [22.11.2021] - Minor bugs fixed.
- [08.11.2021] RELEASE 
_____________________________________________________________________
"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ====================================================================================================
from Autodesk.Revit.DB import (XYZ, BuiltInParameter, ElementId, TemporaryViewMode, View, ViewPlan, ViewSheet, Transaction, TransactionGroup,
                               FilteredElementCollector, )
# from Autodesk.Revit.UI.Selection import *

from pyrevit import forms

# .NET IMPORTS
import clr
clr.AddReference("System")
from System.Diagnostics.Process import Start
from System.Collections.Generic import List
from System.Windows.Window      import DragMove
from System.Windows.Input       import MouseButtonState

# CUSTOM IMPORTS
from Snippets._context_manager import ef_Transaction
from Snippets._sheets import get_titleblock_on_sheet

# VARIABLES
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# ╔═╗╦ ╦╔═╗╔═╗╔╦╗  ╔═╗╔╗  ╦╔═╗╔═╗╔╦╗
# ╚═╗╠═╣║╣ ║╣  ║   ║ ║╠╩╗ ║║╣ ║   ║
# ╚═╝╩ ╩╚═╝╚═╝ ╩   ╚═╝╚═╝╚╝╚═╝╚═╝ ╩  SHEET OBJECT
# ====================================================================================================
class SheetObject():
    def __init__(self, sheet):
        """Class to represent single Sheet with a few methods to align viewports."""
        # SHEET PROPERTIES
        self.sheet       = sheet
        self.Name        = sheet.Name
        self.SheetNumber = sheet.SheetNumber
        self.members_ids = list(sheet.GetAllViewports())

        # OBJECTS ON SHEET
        self.titleblock = get_titleblock_on_sheet(sheet, uidoc=uidoc)
        self.legend     = self.filter_viewport_with_type(view_type=View)

        self.viewport_viewplan           = self.get_viewplans()

    def get_viewplans (self):
        """Function to get single viewport or
        assign multiple viewports with similar scale to self.multiple_viewport_viewplan"""
        # COLLECT ALL ViewPlan ON THE SHEET
        container = []
        for n, viewport_id in enumerate(self.members_ids):
            viewport = doc.GetElement(viewport_id)
            view = doc.GetElement(viewport.ViewId)
            if type(view) == ViewPlan:
                container.append(viewport)
                # self.members_ids.pop(n) #remove this viewport from self.members_ids

        # RETURN SINGLE VIEWPORT
        if len(container) == 1:
            return container

        # RETURN MULTIPLE VIEWPORTS
        elif len(container) > 1:
            #CHECK SCALE
            container_copy = container[:]
            scale = container_copy.pop(0).get_Parameter(BuiltInParameter.VIEWPORT_SCALE).AsString() # First viewport in Container

            for viewport in container_copy:
                temp_scale = viewport.get_Parameter(BuiltInParameter.VIEWPORT_SCALE).AsString()
                if temp_scale != scale:
                    print("***There are multiple viewports with different scale on the given sheet: {}. They will not be aligned ***".format(self.SheetNumber))
                    return []
            return container

        else:
            print("***No ViewPlans were found on the sheet - {}***".format(self.SheetNumber))
            return []

    def filter_viewport_with_type(self, view_type, print_error = False):
        """Method to get single instance of given view_type from self.memebers_ids"""
        container = []
        for n, viewport_id in enumerate(self.members_ids):
            viewport    = doc.GetElement(viewport_id)
            view        = doc.GetElement(viewport.ViewId)
            if type(view) == view_type:
                container.append(viewport)
                self.members_ids.pop(n)

        if len(container) == 1:
            return container[0]

        if len(container) > 1:
            print("***There is more than 1 {} on the given sheet {}.***".format(str(view_type), self.sheet.SheetNumber))


        return None

    def ensure_titleblock_on_zero(self, MainSheet, apply_same = False):
        """Method to ensure that TitleBlocks's origin is XYZ(0,0,0). If not, align it!"""
        # ╔╦╗╦╔╦╗╦  ╔═╗  ╔╗ ╦  ╔═╗╔═╗╦╔═
        #  ║ ║ ║ ║  ║╣   ╠╩╗║  ║ ║║  ╠╩╗
        #  ╩ ╩ ╩ ╩═╝╚═╝  ╚═╝╩═╝╚═╝╚═╝╩ ╩ TITLE BLOCK
        # ==================================================
        main_titleblock  = MainSheet.titleblock
        other_titleblock = self.titleblock

        if not main_titleblock or not other_titleblock:
            return

        # ORIGINS
        main_origin  = main_titleblock.Location.Point
        other_origin = other_titleblock.Location.Point
        zero_origin  = XYZ(0,0,0)

        # SET TITLEBLOCK LOCATION TO 0 IF NOT
        with ef_Transaction(doc, "Seting TitleBlock to XYZ(0,0,0)"):
            # MAIN
            if str(main_origin) != str(zero_origin):
                MainSheet.titleblock.Location.Point = zero_origin

            # OTHER
            if str(other_origin) != str(zero_origin):
                self.titleblock.Location.Point = zero_origin

            # MATCH OTHER's TITLEBLOCK
            if apply_same:
                main_titleblock_type_id = main_titleblock.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).AsElementId()
                other_titleblock.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).Set( main_titleblock_type_id)

        # [OBSOLETE]
        # ALIGN OTHER TITLEBLOCK TO MAIN TITLEBLOCK's ORIGIN
        # if str(main_origin) == str(other_origin):
        #     return
        # #SIZES
        # main_sizes  =  (main_titleblock.get_Parameter(BuiltInParameter.SHEET_WIDTH).AsValueString(),  main_titleblock.get_Parameter(BuiltInParameter.SHEET_HEIGHT).AsValueString())
        # other_sizes = (other_titleblock.get_Parameter(BuiltInParameter.SHEET_WIDTH).AsValueString(), other_titleblock.get_Parameter(BuiltInParameter.SHEET_HEIGHT).AsValueString())
        # if main_sizes == other_sizes:
        #     with ef_Transaction(doc, "Align TitleBlock"):
        #         main_titleblock_origin = MainSheet.titleblock.Location.Point
        #         self.titleblock.Location.Point = main_titleblock_origin
        # else:
        #     print("***TitleBlocks have different sizes. They will not be aligned [Sheets: {}, {}].***".format(MainSheet.SheetNumber, self.SheetNumber))


    def align_legend(self, MainSheet):
        """Function to align Legend if it's the same to MainSheet's legend."""
        # VIEWPORTS
        main_legend_viewport  = MainSheet.legend
        other_legend_viewport = self.legend

        if  main_legend_viewport and other_legend_viewport:
            # VIEWS
            main_legend  = doc.GetElement(main_legend_viewport.ViewId)
            other_legend = doc.GetElement(other_legend_viewport.ViewId)

            if main_legend.Name == other_legend.Name:
                # ╔═╗╦  ╦╔═╗╔╗╔  ╦  ╔═╗╔═╗╔═╗╔╗╔╔╦╗
                # ╠═╣║  ║║ ╦║║║  ║  ║╣ ║ ╦║╣ ║║║ ║║
                # ╩ ╩╩═╝╩╚═╝╝╚╝  ╩═╝╚═╝╚═╝╚═╝╝╚╝═╩╝ ALIGN LEGEND
                #==================================================
                with ef_Transaction(doc,"Align Legends"):

                    try:    other_legend_viewport.SetBoxCenter(main_legend_viewport.GetBoxCenter())
                    except:
                        import traceback
                        print(traceback.format_exc())
                        print("***Could not align Legend on {}***".format(self.sheet.SheetNumber))
            else:
                print("***The legend is not matching the MainSheet. It will not be aligned on the given sheet - {} .***".format(self.SheetNumber))


    def align_viewports(self, MainSheet, apply_CropScopeBox = False, overlap = False):
        """Method to align Viewports."""
        # CHECK OVERLAP ARGUMENT
        if len(self.viewport_viewplan) > 1 and not overlap:
            print("***Multiple Viewports and Overlap set to False on Sheet - {}***".format(self.SheetNumber))
            return

        # ╔╦╗╔═╗╦╔╗╔  ╔═╗╦ ╦╔═╗╔═╗╔╦╗
        # ║║║╠═╣║║║║  ╚═╗╠═╣║╣ ║╣  ║
        # ╩ ╩╩ ╩╩╝╚╝  ╚═╝╩ ╩╚═╝╚═╝ ╩ MAIN SHEET
        main_viewport        = MainSheet.viewport_viewplan[0]
        main_view            = doc.GetElement(main_viewport.ViewId)
        main_scopebox_id     = main_view.get_Parameter(BuiltInParameter.VIEWER_VOLUME_OF_INTEREST_CROP).AsElementId()
        main_cropbox_manager = main_view.GetCropRegionShapeManager().GetCropShape()
        main_cropbox         = None

        # GET CROPBOX / ACTIVATE CROP IF CROPBOX NOT FOUND
        try:
            if main_cropbox_manager:
                main_cropbox = main_cropbox_manager[0] #IT WILL TAKE ONLY SINGLE CURVELOOP.
            else:
                view_crop_param = main_view.get_Parameter(BuiltInParameter.VIEWER_CROP_REGION)
                if not view_crop_param.AsInteger():
                    with ef_Transaction(doc, "Actiavte Crop"):
                        view_crop_param.Set(1)
                        main_cropbox = main_view.GetCropRegionShapeManager().GetCropShape()[0]
        except:
            msg = "Please activate CropBox or ScopeBox on your views that are placed on MainSheet[{}]. \nPlease Try again.\n If error still persist, please contact me in LinkedIn.".format(self.SheetNumber)
            forms.alert(msg, title=__title__,  exitscript=True)


        # ╦  ╔═╗╔═╗╔═╗  ╔╦╗╦ ╦╦═╗╔═╗╦ ╦╔═╗╦ ╦  ╔═╗╔╦╗╦ ╦╔═╗╦═╗╔═╗
        # ║  ║ ║║ ║╠═╝   ║ ╠═╣╠╦╝║ ║║ ║║ ╦╠═╣  ║ ║ ║ ╠═╣║╣ ╠╦╝╚═╗
        # ╩═╝╚═╝╚═╝╩     ╩ ╩ ╩╩╚═╚═╝╚═╝╚═╝╩ ╩  ╚═╝ ╩ ╩ ╩╚═╝╩╚═╚═╝

        for other_viewport in self.viewport_viewplan:
            other_view      = doc.GetElement(other_viewport.ViewId)

            # ╔═╗╦═╗╔═╗╔═╗╔╗ ╔═╗═╗ ╦       ╔═╗╔═╗╔═╗╔═╗╔═╗╔╗ ╔═╗═╗ ╦
            # ║  ╠╦╝║ ║╠═╝╠╩╗║ ║╔╩╦╝  ───  ╚═╗║  ║ ║╠═╝║╣ ╠╩╗║ ║╔╩╦╝
            # ╚═╝╩╚═╚═╝╩  ╚═╝╚═╝╩ ╚═       ╚═╝╚═╝╚═╝╩  ╚═╝╚═╝╚═╝╩ ╚═ CROPBOX / SCOPEBOX
            # ==================================================
            if apply_CropScopeBox:

                with ef_Transaction(doc, 'Crop View - True'):
                    # SET CROP VIEW TO TRUE
                    crop_param = other_view.get_Parameter(BuiltInParameter.VIEWER_CROP_REGION)
                    if not crop_param.AsInteger():
                        try:
                            crop_param.Set(1)
                        except:
                            pass

                with ef_Transaction(doc, "Apply Crop/Scope Box"):
                    # SCOPE BOX
                    try:
                        # SET SCOPE BOX
                        param_scopebox = other_view.get_Parameter(BuiltInParameter.VIEWER_VOLUME_OF_INTEREST_CROP)
                        param_scopebox.Set(main_scopebox_id)
                    except:
                        pass

                    # CROPBOX
                    if main_scopebox_id == ElementId(-1):
                        crop = other_view.GetCropRegionShapeManager()
                        crop.SetCropShape(main_cropbox)

            with ef_Transaction(doc, "Align viewport"):
                # ╔╦╗╔═╗╔╦╗╔═╗  ╦ ╦╦╔╦╗╔═╗
                #  ║ ║╣ ║║║╠═╝  ╠═╣║ ║║║╣
                #  ╩ ╚═╝╩ ╩╩    ╩ ╩╩═╩╝╚═╝ TEMP HIDE
                #==================================================
                #MAIN
                main_view_elements = FilteredElementCollector(doc,main_view.Id).WhereElementIsNotElementType().ToElementIds()
                main_view.HideElementsTemporary(main_view_elements)
                #OTHER
                other_view_elements = FilteredElementCollector(doc,other_view.Id).WhereElementIsNotElementType().ToElementIds()
                other_view.HideElementsTemporary(other_view_elements)

                # ╔═╗╦  ╦╔═╗╔╗╔  ╦  ╦╦╔═╗╦ ╦╔═╗╔═╗╦═╗╔╦╗╔═╗
                # ╠═╣║  ║║ ╦║║║  ╚╗╔╝║║╣ ║║║╠═╝║ ║╠╦╝ ║ ╚═╗
                # ╩ ╩╩═╝╩╚═╝╝╚╝   ╚╝ ╩╚═╝╚╩╝╩  ╚═╝╩╚═ ╩ ╚═╝ ALIGN VIEWPORTS
                #==================================================
                try:    other_viewport.SetBoxCenter(main_viewport.GetBoxCenter())
                except: print("***Could not align Viewport on {}***".format(self.sheet.SheetNumber))

                # ╔╦╗╔═╗╔╦╗╔═╗  ╦ ╦╔╗╔╦ ╦╦╔╦╗╔═╗
                #  ║ ║╣ ║║║╠═╝  ║ ║║║║╠═╣║ ║║║╣
                #  ╩ ╚═╝╩ ╩╩    ╚═╝╝╚╝╩ ╩╩═╩╝╚═╝ TEMP UNHIDE
                #==================================================
                other_view.DisableTemporaryViewMode(TemporaryViewMode.TemporaryHideIsolate)
                for main_viewport in MainSheet.viewport_viewplan:
                    main_view = doc.GetElement(main_viewport.ViewId)
                    main_view.DisableTemporaryViewMode(TemporaryViewMode.TemporaryHideIsolate)

                # [DEBUG] - RESTORE CROP
                if main_scopebox_id == ElementId(-1) and main_cropbox.IsRectangular(main_cropbox.GetPlane()):
                    crop.RemoveCropRegionShape()
# ====================================================================================================


class ListItem:
    """Helper Class for displaying selected sheets in my custom GUI."""
    def __init__(self,  Name='Unnamed', IsChecked = False, element = None):
        self.Name       = Name
        self.IsChecked  = IsChecked
        self.element    = element


# ╔╦╗╔═╗╦╔╗╔    ╔═╗╦ ╦╦
# ║║║╠═╣║║║║    ║ ╦║ ║║
# ╩ ╩╩ ╩╩╝╚╝    ╚═╝╚═╝╩ MAIN + GUI
# ==================================================
class AlignViewports(forms.WPFWindow):
    def __init__(self):
        """Main class for GUI and initiating Viewports alignment."""
        self.selected_sheets = self.get_selected_sheets()
        if self.selected_sheets:
            self.form                       = forms.WPFWindow.__init__(self, "Script.xaml")
            self.test_ListBox.ItemsSource   = self.generate_list_items()
            self.main_title.Text            = __title__
            self.ShowDialog()

    # ╔═╗╦  ╦╔═╗╔╗╔  ╦  ╦╦╔═╗╦ ╦╔═╗╔═╗╦═╗╔╦╗╔═╗
    # ╠═╣║  ║║ ╦║║║  ╚╗╔╝║║╣ ║║║╠═╝║ ║╠╦╝ ║ ╚═╗
    # ╩ ╩╩═╝╩╚═╝╝╚╝   ╚╝ ╩╚═╝╚╩╝╩  ╚═╝╩╚═ ╩ ╚═╝ ALIGN VIEWPORTS
    # ====================================================================================================
    def align_other_sheets(self):
        MainSheet = SheetObject(self.main_sheet)
        # CHECK MAINSHEET
        if not MainSheet.viewport_viewplan:
            return
        if not self.check_if_main_aligned(MainSheet):
            return
        # HIDE ELEMENTS ON ALL VIEWS HERE TO SPEED UP!???

        print("- MainSheet selected: {}".format(MainSheet.SheetNumber))
        OtherSheets = [SheetObject(other_sheet) for other_sheet in self.other_sheets]
        for n, OtherSheet in enumerate(OtherSheets):
            print('- Aligning Viewports on Sheet {} [{}/{}]'.format(OtherSheet.SheetNumber, n+1, len(OtherSheets)))
            OtherSheet.align_viewports(MainSheet, apply_CropScopeBox=self.apply_crop, overlap=self.overlap)
            OtherSheet.ensure_titleblock_on_zero(MainSheet, apply_same=self.apply_titleblock)
            if self.align_legend:
                OtherSheet.align_legend(MainSheet)

    # ╔═╗╦ ╦╔═╗╔═╗╦╔═  ╔╦╗╔═╗╦╔╗╔  ╔═╗╦ ╦╔═╗╔═╗╔╦╗
    # ║  ╠═╣║╣ ║  ╠╩╗  ║║║╠═╣║║║║  ╚═╗╠═╣║╣ ║╣  ║
    # ╚═╝╩ ╩╚═╝╚═╝╩ ╩  ╩ ╩╩ ╩╩╝╚╝  ╚═╝╩ ╩╚═╝╚═╝ ╩ CHECK MAIN SHEET
    # ==================================================
    def check_if_main_aligned(self,MainSheet):
        """Function to check if multiple ViewPlans on MainSheet are aligned."""

        def XYZ_to_str(XYZ_obj):
            """Convert XYZ object into readable string for further comparison."""
            return "{},{}".format(XYZ_obj.X, XYZ_obj.Y)

        if not MainSheet.viewport_viewplan:
            return False

        # SINGLE VIEWPORT
        elif len(MainSheet.viewport_viewplan) == 1 :
            return True

        # NO VIEWPORTS
        elif len(MainSheet.viewport_viewplan) == 0:
            print("***There are no Viewports on the MainSheet - {}***".format(MainSheet.SheetNumber))
            return False

        # MULTIPLE VIEWPORTS
        elif len(MainSheet.viewport_viewplan) > 1:
            if not self.overlap:
                print("***There are multiple Viewports on MainSheet and Overlap is set to False - {}***".format(MainSheet.SheetNumber))
                return


            # MainSheet's Viewports
            viewports = MainSheet.viewport_viewplan[:]

            # [CHECK: 1] - CROP ACTIVATED ON ALL
            for viewport in viewports:
                # CROP ACTIAVTED
                if not viewport.get_Parameter(BuiltInParameter.VIEWER_CROP_REGION).AsInteger():
                    print("***All Viewports on MainSheet should have crop activated.***")
                    return

            # [CHECK: 2] - SAME SCALE
            scale = None
            for viewport in viewports:
                if not scale:
                    scale = viewport.get_Parameter(BuiltInParameter.VIEWPORT_SCALE).AsString()
                    continue
                if scale != viewport.get_Parameter(BuiltInParameter.VIEWPORT_SCALE).AsString() :
                    print("***There are ViewPorts with different scale on MainSheet - {} ***".format(MainSheet.SheetNumber))

            # [CHECK: 3] - SAME CROPBOX
            cropboxes       = [doc.GetElement(viewport.ViewId).CropBox for viewport in viewports]
            crop_max_points = [XYZ_to_str(cropbox.Max) for cropbox in cropboxes]
            crop_min_points = [XYZ_to_str(cropbox.Min) for cropbox in cropboxes]

            if len(set(crop_max_points)) > 1 or len(set(crop_min_points)) > 1:
                print("***There are different CropBoxes/ScopBoxes assigned to viewports on MainSheet - {}.***".format(MainSheet.SheetNumber))
                return

            # [CHECK: 4] - SAME POSITION ON SHEET (with same cropbox)
            with ef_Transaction(doc, "Check if MainSheet's viewports aligned."):
                viewports = MainSheet.viewport_viewplan[:]

                # TEMP HIDE ELEMENTS ON VIEWPORTS
                for main_viewport in viewports:
                    view = doc.GetElement(main_viewport.ViewId)
                    main_view_elements = FilteredElementCollector(doc, view.Id).WhereElementIsNotElementType().ToElementIds() #todo combine all viewports into single filter
                    view.HideElementsTemporary(main_view_elements)

                # COMPARE VIEWPORT's POSITIONS (works only if same CropBox/ScopeBox )
                positions = [XYZ_to_str(viewport.GetBoxCenter()) for viewport in viewports]
                if len(set(positions)) > 1 :
                    # TEMP UNHIDE VIEWS
                    for main_viewport in viewports:
                        main_view = doc.GetElement(main_viewport.ViewId)
                        main_view.DisableTemporaryViewMode(TemporaryViewMode.TemporaryHideIsolate)

                    print("***There are multiple Viewports on MainSheet and they are not aligned. Main - {}.***\n ***Viewports will not be aligned!***".format(MainSheet.SheetNumber))
                    return False
            return True

    # ╔═╗╔═╗╦  ╔═╗╔═╗╔╦╗╔═╗╔╦╗  ╔═╗╦ ╦╔═╗╔═╗╔╦╗╔═╗
    # ╚═╗║╣ ║  ║╣ ║   ║ ║╣  ║║  ╚═╗╠═╣║╣ ║╣  ║ ╚═╗
    # ╚═╝╚═╝╩═╝╚═╝╚═╝ ╩ ╚═╝═╩╝  ╚═╝╩ ╩╚═╝╚═╝ ╩ ╚═╝ SELECTED SHEETS
    # ====================================================================================================
    def get_selected_sheets(self):
        """Function to get selected elements in Revit UI ."""
        from Snippets._selection import get_selected_sheets
        selected_sheets = get_selected_sheets(given_uidoc=uidoc ,title=__title__,
                                              label='Select Sheet to Align Viewports', exit_if_none=True)

        # CANCEL IF NOT ENOUGH SHEETS SELECTED
        if len(selected_sheets) < 2:
            msg ="Not enough sheets were selected. Min 2 is required. Please, Try again."
            forms.alert(msg, title=__title__,  exitscript=True)

        # FORMAT AND RETURN
        selected_sheets = {"{} - {}".format(sheet.SheetNumber, sheet.Name): sheet for sheet in selected_sheets}
        return selected_sheets

    # ==================================================
    def generate_list_items(self):
        """This function prepares the List[ListItem] to display elements in custom GUI."""
        list_of_items = List[type(ListItem())]()

        # if my_array.index(member) == 0:

        first = True
        for sheet_name, sheet in sorted(self.selected_sheets.items()):
            checked = True if first else False
            first = False
            list_of_items.Add(ListItem(sheet_name, checked, sheet))
        return list_of_items




    # ╔═╗╦═╗╔═╗╔═╗╔═╗╦═╗╔╦╗╦╔═╗╔═╗
    # ╠═╝╠╦╝║ ║╠═╝║╣ ╠╦╝ ║ ║║╣ ╚═╗
    # ╩  ╩╚═╚═╝╩  ╚═╝╩╚═ ╩ ╩╚═╝╚═╝ PROPERTIES
    # ==================================================
    @property
    def ListBox(self):
        return self.test_ListBox

    @property
    def apply_crop(self):
        return self.UI_checkbox_apply_same_crop.IsChecked

    @property
    def apply_titleblock(self):
        return self.UI_checkbox_apply_same_titleblock.IsChecked

    @property
    def align_legend(self):
        return self.UI_checkbox_align_legend.IsChecked

    @property
    def overlap(self):
        return self.UI_checkbox_overlap.IsChecked

    # ╔═╗╦  ╦╔═╗╔╗╔╔╦╗  ╦ ╦╔═╗╔╗╔╔╦╗╦  ╔═╗╦═╗╔═╗
    # ║╣ ╚╗╔╝║╣ ║║║ ║   ╠═╣╠═╣║║║ ║║║  ║╣ ╠╦╝╚═╗
    # ╚═╝ ╚╝ ╚═╝╝╚╝ ╩   ╩ ╩╩ ╩╝╚╝═╩╝╩═╝╚═╝╩╚═╚═╝ GUI EVENT HANDLERS:
    # ==================================================

    def button_close(self,sender,e):
        """Stop application by clicking on a <Close> button in the top right corner."""
        self.Close()

    def Hyperlink_RequestNavigate(self, sender, e):
        """Forwarding for a Hyperlink"""
        Start(e.Uri.AbsoluteUri)

    def header_drag(self,sender,e):
        """Drag window by holding LeftButton on the header."""
        if e.LeftButton == MouseButtonState.Pressed:
            DragMove(self)

    def button_run(self,sender,e):
        """Main run button.
        Closes the dialog box and starts duplicating selected sheets."""
        self.Close()


        # GET SELECTED MAIN SHEET
        selected_sheet_name = None
        items = self.test_ListBox.Items
        for item in items:
            if item.IsChecked:
                selected_sheet_name = item.Name
                break

        # VARIABLES MAIN/OTHER SHEETS
        self.main_sheet     = self.selected_sheets.pop(selected_sheet_name)
        self.other_sheets   = self.selected_sheets.values()

        # ALIGN VIEWPORTS
        self.align_other_sheets()



# ====================================================================================================
# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
# ====================================================================================================
if __name__ == '__main__':
    tg = TransactionGroup(doc,__title__)
    tg.Start()
    x = AlignViewports()
    tg.Assimilate()

    if x.selected_sheets:
        print('_'*120)
        print('Align Viewports is finished.')