# -*- coding: utf-8 -*-

__title__ = "Duplicate Sheets"   # Name of the button displayed in Revit
__author__ = "Erik Frits"
__doc__ = """Version = 0.5
Date    = 08.12.2020
_____________________________________________________________________
Description:

Duplicate selected sheets with control over copying elements.

_____________________________________________________________________
How-to:

-> Select sheets in Project Browser 
-> Run the script.
-> Select duplicate options 
-> Click duplicate button.
_____________________________________________________________________
Prerequisite:

You have to select sheets in ProjectBrowser.
_____________________________________________________________________
Last update:

- Creates Sheet Copy
- Copies Views
- Failsave ViewName and SheetNumber
- Copies Legends
- Additional Sheet Revisions
- Schedules
- Allign title block to original in case it was moved!
- Text on Sheet
- Lines on Sheets
- Revision
- Images
- Dimensions
- Duplicate Legend = bool
- Duplicate Schedule = bool

_____________________________________________________________________
To-do:

- MOVE VIEWPORT TITLE (RevitAPI workaround only)
- Set similar Viewport Title 
- Titleblock position
- COPY parameters from sheets too! (ALL/GUI to select parameter to copy?)
- BUG Warning when duplicating dimensioning!!! Some elements are reported 
to be deleted even ugh nothing is gone...? 
_____________________________________________________________________
"""

#todo reduce imports
import pyrevit
from pyrevit import forms
from pyrevit import revit
from pyrevit.forms import WPFWindow
import clr
from Autodesk.Revit import DB
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *
from pyrevit import revit
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application
import sys
from pyrevit.forms import SelectFromList
from System.Collections.Generic import List

from pyrevit import revit
from pyrevit import forms
from pyrevit.forms import WPFWindow

import clr
clr.AddReference("System")
from System.Diagnostics.Process import Start
from System.Collections.Generic import List
from System.Windows.Window import DragMove
from System.Windows.Input import MouseButtonState



###__________________________________________________________________________________________________APPLICATION______________###

class MyWindow(forms.WPFWindow):
    """GUI for View renaming tool."""

    # VARIABLES
    view_dupicate_option = ViewDuplicateOption.Duplicate  # Default

    def __init__(self, xaml_file_name):
        self.form = forms.WPFWindow.__init__(self, xaml_file_name)
        self.main_title.Text = __title__

    def remove_special_charachter(self, string_to_clean):
        """Function to remove special characters from the given string."""
        special_charachters = r"\:{}[]|;<>?`~"
        for char in special_charachters:
            while char in string_to_clean:
                string_to_clean= string_to_clean.replace(char,"")
        return string_to_clean if string_to_clean else "unnamed"


    def update_view_name(self, view , new_view):
        #type:(ViewSheet, ViewSheet) -> None
        """
        :param view:       View that is being duplicated
        :param new_view:   Newly created View.
        :return:
        """
        # CREATE VIEW NAME
        current_name = view.Name
        new_name = self.view_prefix + current_name.replace(self.view_find,self.view_replace) + self.view_suffix
        # FILTER SPECIAL CHARACHTERS
        new_name = self.remove_special_charachter(new_name)

        fail_count = 0 #FAIL SAVE
        while True:
            # RENAME IF DIFFERENT
            if new_name == new_view.Name:
                break

            try:
                # TRY TO RENAME
                new_view.Name =  new_name
                break
            except:
                new_name += "*"

            # STOP IF FAILED 5 TIMES
            fail_count+=1
            if fail_count > 5:
                break

    def update_sheet_name(self, sheet, new_sheet):
        #type:(ViewSheet, ViewSheet) -> None
        """
        :param sheet:       Sheet that is being duplicated
        :param new_sheet:   Newly created Sheet.
        :return:
        """
        # CREATE VIEW NAME
        current_sheet_name = sheet.Name

        new_name = self.sheet_name_prefix + current_sheet_name.replace(self.sheet_name_find, self.sheet_name_replace) + self.sheet_name_suffix
        # FILTER SPECIAL CHARACHTERS
        new_name = self.remove_special_charachter(new_name)

        fail_count = 0  # FAIL SAVE
        while True:
            # RENAME IF DIFFERENT
            if new_name == new_sheet.Name:
                break

            try:
                # TRY TO RENAME
                new_sheet.Name = new_name
                break
            except:
                new_name += "*"

            # STOP IF FAILED 5 TIMES
            fail_count += 1
            if fail_count > 5:
                break

    def update_sheet_number(self, sheet, new_sheet):
        #type:(ViewSheet, ViewSheet) -> None
        """
        :param sheet:       Sheet that is being duplicated
        :param new_sheet:   Newly created Sheet.
        :return:
        """
        # CREATE VIEW NAME
        current_sheet_number = sheet.SheetNumber

        new_name = self.sheet_number_prefix + current_sheet_number.replace(self.sheet_number_find, self.sheet_number_replace) + self.sheet_number_suffix
        # FILTER SPECIAL CHARACHTERS
        new_name = self.remove_special_charachter(new_name)

        fail_count = 0  # FAIL SAVE
        while True:
            # RENAME IF DIFFERENT
            if new_name == new_sheet.SheetNumber:
                break
            try:
                # TRY TO RENAME
                new_sheet.SheetNumber = new_name
                break
            except:
                new_name += "*"

            # STOP IF FAILED 5 TIMES
            fail_count += 1
            if fail_count > 5:
                print("count >5 = Break")
                break






    def duplicate_schedules(self,sheet, new_sheet):
        # type:(ViewSheet, ViewSheet) -> None
        """
        :param sheet:
        :param new_sheet:
        :return:
        """

        #todo Create filter to get the right schedules with FilteredElementCollector(doc).
        schedules_on_sheet = []
        schedules = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_ScheduleGraphics).ToElements()

        # Loop schedules s=scheduleSheetInstance
        for s in schedules:
            if s.OwnerViewId == sheet.Id:
                if not s.IsTitleblockRevisionSchedule:
                    origin = s.Point

                    # USE EXISTING
                    if self.use_existing_schedules :
                        schedule_view_id = s.ScheduleId
                    # DUPLICATE
                    else:


                        scheduleId = s.ScheduleId #s= scheduleSheetInstance
                        if scheduleId == ElementId.InvalidElementId:
                            continue

                        viewSchedule = doc.GetElement(scheduleId)



                        schedule_view_id = viewSchedule.Duplicate(self.view_dupicate_option)
                        #NAMING?

                    ScheduleSheetInstance.Create(doc, new_sheet.Id, schedule_view_id, origin)



    def duplicate_legends(self,sheet, new_sheet):
        # type:(ViewSheet, ViewSheet) -> None
        """
        :param sheet:
        :param new_sheet:
        :return:
        """

        viewports_ids = sheet.GetAllViewports()

        for viewport_id in viewports_ids:

            viewport = doc.GetElement(viewport_id)
            viewport_type_id = viewport.GetTypeId()
            viewport_origin = viewport.GetBoxCenter()
            view_id = viewport.ViewId
            view = doc.GetElement(view_id)
            new_view = None

            # Legends
            if view.ViewType == ViewType.Legend:
                legend_view = view


                if not self.use_existing_legends:
                    # DUPLICATE LEGEND
                    legend_view_id = view.Duplicate(ViewDuplicateOption.WithDetailing)  # DUplicate legend with detailing!
                    legend_view = doc.GetElement(legend_view_id)



                # PLACE NEW VIEWS ON A NEW SHEET
                new_viewport = Viewport.Create(doc, new_sheet.Id, legend_view.Id, viewport_origin)


                if new_viewport:
                    new_viewport_type_id = new_viewport.GetTypeId()

                    # SET SAME VIEWPORT TYPE
                    if viewport_type_id != new_viewport_type_id:
                        new_viewport.ChangeTypeId(viewport_type_id)












    def duplicate_views(self, sheet, new_sheet):
        #type:(ViewSheet, ViewSheet) -> None
        """
        Function to duplicate viewports.
        ViewPlan,ViewSection,View3D, ViewElevation?
        Legends

        :param sheet:
        :param new_sheet:
        :return:
        """
        #FIXME REFACTOR.
        viewports_ids = sheet.GetAllViewports()


        for viewport_id in viewports_ids:

            viewport = doc.GetElement(viewport_id)
            viewport_type_id = viewport.GetTypeId()
            viewport_origin = viewport.GetBoxCenter()
            view_id = viewport.ViewId
            view = doc.GetElement(view_id)
            new_view = None
            # Legends
            if view.ViewType == ViewType.Legend:
                # IGNORE LEGENDS (they have their own method)
                continue


            elif view.ViewType == ViewType.ThreeD and self.view_dupicate_option == ViewDuplicateOption.AsDependent:
                new_view_id = view.Duplicate(ViewDuplicateOption.Duplicate)
                new_view = doc.GetElement(new_view_id)
            # elif view.ViewType == ViewType.

            #TODO write each type, to avoid issues with unpredicted types...
            # ViewPlan,ViewSection,View3D
            else:

                new_view_id = view.Duplicate(self.view_dupicate_option) #todo user input options!
                new_view = doc.GetElement(new_view_id)

                # self.view_rename(new_view, view_name=str(view.Name))
                #todo rename view
                #todo remove View Template


            if new_view:
                # RENAME
                self.update_view_name(view,new_view)


                # PLACE NEW VIEWS ON A NEW SHEET
                new_viewport = Viewport.Create(doc, new_sheet.Id, new_view.Id, viewport_origin)
                new_viewport_type_id = new_viewport.GetTypeId()

                # SET SAME VIEWPORT TYPE
                if viewport_type_id != new_viewport_type_id:
                    new_viewport.ChangeTypeId(viewport_type_id)







    # def place_view_on_sheet(self, sheet_id, view_id, viewport_origin):
    #     """
    #
    #     :param sheet_id:
    #     :param view_id:
    #     :param viewport_origin:
    #     :return:
    #     """
    #
    #     # new_viewport = Viewport.Create(doc, newsheet.Id, new_view.Id, viewport_origin)
    #     # new_viewport_type_id = new_viewport.GetTypeId()
    #     # if viewport_type_id != new_viewport_type_id:
    #     #     new_viewport.ChangeTypeId(viewport_type_id)
    #
    #     pass

    def duplicate_elements(self, sourceView, elements_ids, destinationView):
        #type:(View, list , View) -> None
        """Function to duplicate elements from one view to another.
        :param sourceView:      View where elements are located.
        :param elements_ids:    List of elements_ids to copy
        :param destinationView: View where elements will be copied to.
        :return: None"""
        # Prepare parameters
        elementsToCopy      = List[ElementId](elements_ids)
        additionalTransform = None
        options             = CopyPasteOptions()

        # COPY ELEMENTS
        if elementsToCopy:
            ElementTransformUtils.CopyElements(sourceView,
                                           elementsToCopy,
                                           destinationView,
                                           additionalTransform,
                                           options)



    def duplicate_lines(self,sheet, new_sheet):
        #type:(ViewSheet, ViewSheet) -> None
        """
        :param sheet:
        :param new_sheet:
        :return:
        """

        lines_on_sheet = FilteredElementCollector(doc, sheet.Id).OfCategory(BuiltInCategory.OST_Lines).ToElementIds()
        self.duplicate_elements(sheet, lines_on_sheet, new_sheet)


    #TODO make unique function to get elements on a sheet with a list of Categories. 1 Function for all elements on the sheet.
    def duplicate_clouds(self, sheet, new_sheet):
        #type:(ViewSheet, ViewSheet) -> None
        """
        :param sheet:
        :param new_sheet:
        :return:
        """

        categories = [  BuiltInCategory.OST_RevisionClouds,
                        BuiltInCategory.OST_RevisionCloudTags]
        categories_list = List[BuiltInCategory](categories)
        filter = ElementMulticategoryFilter(categories_list)


        cloud_and_tags_ids = FilteredElementCollector(doc, sheet.Id).WherePasses(filter).ToElementIds()

        self.duplicate_elements(sheet, cloud_and_tags_ids, new_sheet)



    def duplicate_images(self, sheet, new_sheet):
        # type:(ViewSheet, ViewSheet) -> None
        """
        :param sheet:
        :param new_sheet:
        :return:
        """

        images_on_sheet = FilteredElementCollector(doc, sheet.Id).OfCategory(BuiltInCategory.OST_RasterImages).ToElementIds()
        self.duplicate_elements(sheet, images_on_sheet , new_sheet)

    def duplicate_text(self, sheet, new_sheet):
        # type:(ViewSheet, ViewSheet) -> None
        """
        :param sheet:
        :param new_sheet:
        :return:
        """

        text_on_sheet = FilteredElementCollector(doc, sheet.Id).OfCategory(BuiltInCategory.OST_TextNotes).ToElementIds()
        self.duplicate_elements(sheet, text_on_sheet , new_sheet)


    def duplicate_dimensons(self, sheet, new_sheet):
        # type:(ViewSheet, ViewSheet) -> None
        """ Function to duplicate all dimension placed on the sheet to a new sheet.
        :param sheet:
        :param new_sheet:
        :return:
        """
        # TODO [Warning] - 5 elements were deleted???
        dimensions_on_sheet = FilteredElementCollector(doc, sheet.Id).OfCategory(BuiltInCategory.OST_Dimensions).ToElementIds()
        self.duplicate_elements(sheet, dimensions_on_sheet , new_sheet)


    def duplicate_symbols(self, sheet, new_sheet):
        # type:(ViewSheet, ViewSheet) -> None
        """
        :param sheet:
        :param new_sheet:
        :return:
        """

        symbols_on_sheet = FilteredElementCollector(doc, sheet.Id).OfCategory(BuiltInCategory.OST_GenericAnnotation).ToElementIds()
        self.duplicate_elements(sheet, symbols_on_sheet , new_sheet)

    def duplicate_dwgs(self, sheet, new_sheet):
        # type:(ViewSheet, ViewSheet) -> None
        """
        :param sheet:
        :param new_sheet:
        :return:
        """

        dwgs = FilteredElementCollector(doc,sheet.Id).OfClass(ImportInstance).ToElementIds()
        self.duplicate_elements(sheet, dwgs, new_sheet)

        pass

        #fixme
        # def titleblock_location(self):
        #     origin = self.titleblock.Location.Point
        #     if origin != XYZ(0,0,0):
        #         return origin
        #     return None


    def duplicate_selected_sheets(self):
        """Main function that duplicates selected sheets."""

        # SELECTED SHEETS LOOP
        for sheet in self.selected_sheets:


            # TITLE BLOCK
            #todo more than 1 title block?
            title_block = self.get_sheet_title_block(sheet)
            # print(title_block)
            title_block_id = title_block.GetTypeId() if title_block else ElementId.InvalidElementId

            # TITLE BLOCK POSITION
            #todo save position(s) on sheet.



            # CREATE SHEET
            if title_block:
                new_sheet = ViewSheet.Create(doc, title_block.GetTypeId())
            else:
                new_sheet = ViewSheet.Create(doc, ElementId.InvalidElementId)




            # SHEET NUMBER
            self.update_sheet_number(sheet, new_sheet)

            # SHEET NAME
            self.update_sheet_name(sheet, new_sheet)




            # DUPLICATE VIEWPORTS  [Legends / ViewPlan,ViewSection,View3D]
            if self.checkbox_views:
                #todo split views and legends into seperate functions?
                self.duplicate_views(sheet, new_sheet)
                #todo place on sheet separate function?


            # DUPLICATE LEGENDS
            if self.checkbox_legends:
                self.duplicate_legends(sheet,new_sheet)


            # DUPLICATE SCHEDULE
            if self.checkbox_schedules:
                self.duplicate_schedules(sheet, new_sheet)

            # DUPLICATE IMAGES
            if self.checkbox_images:
                self.duplicate_images(sheet,new_sheet)

            # DUPLICATE LINES
            if self.checkbox_lines:
                self.duplicate_lines(sheet,new_sheet)

            # DUPLICATE CLOUDS
            if self.checkbox_clouds:
                self.duplicate_clouds(sheet, new_sheet)

            # DUPLICATE Text
            if self.checkbox_text:
                self.duplicate_text(sheet,new_sheet)


            # DUPLICATE DWGs
            if self.checkbox_dwgs:
                self.duplicate_dwgs(sheet,new_sheet)

            # DUPLICATE SYMBOLS
            if self.checkbox_symbols:
                self.duplicate_symbols(sheet,new_sheet)
            # DUPLICATE DIMENSIONS

            if self.checkbox_dimensions:
                self.duplicate_dimensons(sheet,new_sheet)

            # SET ADDITIONAL REVISIONS
            if self.checkbox_additional_revisions:
                self.set_additional_revisions_on_sheet(sheet, new_sheet)


    def set_additional_revisions_on_sheet(self,sheet, new_sheet):
        # type:(ViewSheet, ViewSheet) -> None
        """ Function to retrieve additional revisions and add them to duplicated sheet if any.
        :param sheet:
        :param new_sheet:
        :return: """
        additional_revisions_ids= sheet.GetAdditionalRevisionIds()
        if additional_revisions_ids:
            new_sheet.SetAdditionalRevisionIds(additional_revisions_ids)



    def get_sheet_title_block(self, sheet):
        """Get titleblock of a sheet.
        :param sheet:   ViewSheet
        :return:        titleblock element or None.
        """
        # Filter?
        #TODO - Improve efficiency?
        all_TitleBlocks = FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_TitleBlocks).WhereElementIsNotElementType().ToElements()
        for title_block in all_TitleBlocks:
            if title_block.OwnerViewId == sheet.Id:
                return title_block
        return None



    # GET SELECTION
    @property
    def selected_sheets(self):
        """Function to get selected elements in Revit UI ."""

        # one liner:
        # selected_sheets = [doc.GetElement(element_id) for element_id in uidoc.Selection.GetElementIds() if
        #                    type(doc.GetElement(element_id)) == ViewSheet]

        # GET SHEETS FROM CURRENT SELECTION
        selected_sheets = []
        selected_elements = uidoc.Selection.GetElementIds()
        for element_id in selected_elements:
            element = doc.GetElement(element_id)
            if type(element) == ViewSheet:
                selected_sheets.append(element)

        # CANCEL IF NO SHEETS SELECTED / Open a menu with all sheets in the project.
        if not selected_sheets:
            msg = "No Sheets were selected."
            pyrevit.forms.alert(msg, title=__title__, sub_msg=None, expanded=None, footer='', ok=True, warn_icon=True, exitscript=True)

        return selected_sheets


    # ELEMENTS ON THE SHEET
    def get_views_from_sheet(self,sheet):
        """Function to get views from sheet."""

        # FIlter legends and

        pass

    # [NAMING] VIEWS
    @property
    def view_find(self):
        return self.UI_view_find.Text

    @property
    def view_replace(self):
        return self.UI_view_replace.Text

    @property
    def view_prefix(self):
        return self.UI_view_prefix.Text

    @property
    def view_suffix(self):
        return self.UI_view_suffix.Text



    # [NAMING] SHEET NUMBER
    @property
    def sheet_number_find(self):
        return self.UI_sheet_number_find.Text

    @property
    def sheet_number_replace(self):
        return self.UI_sheet_number_replace.Text

    @property
    def sheet_number_prefix(self):
        return self.UI_sheet_number_prefix.Text

    @property
    def sheet_number_suffix(self):
        return self.UI_sheet_number_suffix.Text



    # [NAMING] SHEET NAME
    @property
    def sheet_name_find(self):
        return self.UI_sheet_name_find.Text

    @property
    def sheet_name_replace(self):
        return self.UI_sheet_name_replace.Text

    @property
    def sheet_name_prefix(self):
        return self.UI_sheet_name_prefix.Text

    @property
    def sheet_name_suffix(self):
        return self.UI_sheet_name_suffix.Text




    # [CHECKBOXES] - INCLUDE ELEMENTS

    @property
    def checkbox_views(self):
        return self.UI_checkbox_views.IsChecked

    @property
    def checkbox_legends(self):
        return self.UI_checkbox_legends.IsChecked

    @property
    def checkbox_schedules(self):
        return self.UI_checkbox_schedules.IsChecked

    @property
    def checkbox_images(self):
        return self.UI_checkbox_images.IsChecked

    @property
    def checkbox_lines(self):
        return self.UI_checkbox_lines.IsChecked

    @property
    def checkbox_text(self):
        return self.UI_checkbox_text.IsChecked

    @property
    def checkbox_clouds(self):
        return self.UI_checkbox_clouds.IsChecked

    @property
    def checkbox_dwgs(self):
        return self.UI_checkbox_dwgs.IsChecked

    @property
    def checkbox_symbols(self):
        return self.UI_checkbox_symbols.IsChecked

    @property
    def checkbox_dimensions(self):
        return self.UI_checkbox_dimensions.IsChecked

    @property
    def checkbox_additional_revisions(self):
        return self.UI_checkbox_additional_revisions.IsChecked

    # [Checkboxes] - USE EXISTING

    @property
    def use_existing_legends(self):
        return self.UI_checkbox_use_existing_legend.IsChecked

    @property
    def use_existing_schedules(self):
        return self.UI_checkbox_use_existing_schedules.IsChecked


    # GUI EVENT HANDLERS:

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

    def radiobutton_duplicate_option(self, sender, e):
        """[Event Handler] Grab the value of a radio button on its change."""
        checked_radiobutton = sender
        if checked_radiobutton.IsChecked:
            if checked_radiobutton.Content == "Duplicate":
                self.view_dupicate_option = ViewDuplicateOption.Duplicate
            elif checked_radiobutton.Content == "Duplicate detailing":
                self.view_dupicate_option = ViewDuplicateOption.WithDetailing
            elif checked_radiobutton.Content == "Duplicate Dependent":
                self.view_dupicate_option = ViewDuplicateOption.AsDependent

    def button_run(self,sender,e):
        """Main run button.
        Closes the dialog box anda start duplicating selected sheets."""

        self.Close()
        self.duplicate_selected_sheets()



















#
#
#
#
#
#
#
# selected_views = []
# UI_Selected = uidoc.Selection.GetElementIds()
#
# # selected_views = [doc.GetElement(view_id) if type(doc.GetElement(view_id)) == ViewPlan or  type(doc.GetElement(view_id)) == ViewSection or  type(doc.GetElement(view_id)) == View3D]
#
# for view_id in UI_Selected:
#     element = doc.GetElement(view_id)
#     if type(element) == ViewPlan or  type(element) == ViewSection or  type(element) == View3D:
#         selected_views.append(element)
t = Transaction(doc,__title__)
t.Start()

MyWindow("Script.xaml").ShowDialog()
t.Commit()



#todo Create Config for Project Browser values.
#todo remove View Template



# else:
#     forms.alert("No views were selected.\nPlease, try again.", exitscript=True, title="Script Cancelled.")
# #

#fixme
#     def viewport_label_visible(self,viewport_type_id):
#         """returns 0/1 depending if Viewport Title is visible or not."""
#         viewport_type = doc.GetElement(viewport_type_id)
#         label_shown = viewport_type .get_Parameter(BuiltInParameter.VIEWPORT_ATTR_SHOW_LABEL)
#         return label_shown.AsInteger()


#





#todo
# label_attempt = """
#             # #TODO: Find a way to adjust right position of viewport title.
#             # label_shown = self.viewport_label_visible(viewport_type_id)
#             # viewport_label = None
#             # if label_shown:
#             #     viewport_label = viewport.GetLabelOutline()
#             #
#             # if label_shown:
#             #     #TODO There is no direct way to move Viewport's label in RevitAPI at the moment...
#             #     # There are a few workaround that do not seem efficient or elegant, but it might get the job done!
#             #     new_label_shown = self.viewport_label_visible(new_viewport_type_id)
#             #     new_viewport_label = new_viewport.GetLabelOutline()
#             #     # new_viewport_label.MinimumPoint = viewport_label.MinimumPoint
#             #     # new_viewport_label.MaximumPoint = viewport_label.MaximumPoint
#             #     # new_viewport_label.MaximumPoint = viewport_label.MaximumPoint
#             #     workaround_1="""Its not clever but as work around you can;
#             #                     Get viewport's view
#             #                     Halve view's size in x direction to the right
#             #                     Remove viewport and then replace, (title now at left of half size VP).
#             #                     Reset size of view to original, title remain in place
#             #                     It would be good if the API had a method.  Mine is a very "messy" workaround.
#             #                 """+
#
#
#             print("_"*40)
#
#





# # # Create similar sheets
# #
# # # Duplicate views ( Detailed, not
# # #  // all views but schedules
# # #                 foreach (ElementId eid in vs.GetAllPlacedViews())
# # #                 {
# # #                     View ev = doc.GetElement(eid) as View;
# # #
# # #                     View newview = null;
# # #
# # #                     // legends
# # #                     if (ev.ViewType == ViewType.Legend)
# # #                     {
# # #                         newview = ev;
# # #                     }
# # #                     // all non-legend and non-schedule views
# # #                     else
# # #                     {
# # #                         ElementId newviewid = ev.Duplicate(ViewDuplicateOption.WithDetailing);
# # #                         newview = doc.GetElement(newviewid) as View;
# # #                         newview.Name = ev.Name + "-DUP";
# # #                     }
# # #
# # #                     foreach (Viewport vp in new FilteredElementCollector(doc).OfClass(typeof(Viewport)))
# # #                     {
# # #
# # #                         if (vp.SheetId == vs.Id && vp.ViewId == ev.Id)
# # #                         {
# # #                             BoundingBoxXYZ vpbb = vp.get_BoundingBox(vs);
# # #                             XYZ initialCenter = (vpbb.Max + vpbb.Min) / 2;
# # #
# # #                             Viewport newvp = Viewport.Create(doc, newsheet.Id, newview.Id, XYZ.Zero);
# # #
# # #                             BoundingBoxXYZ newvpbb = newvp.get_BoundingBox(newsheet);
# # #                             XYZ newCenter = (newvpbb.Max + newvpbb.Min) / 2;
# # #
# # #                             ElementTransformUtils.MoveElement(doc, newvp.Id, new XYZ(
# # #                             initialCenter.X - newCenter.X,
# # #                             initialCenter.Y - newCenter.Y,
# # #                             0));
# # #                         }
# #
# # # detailed)
# # # Suffix = Hardcoded COPY_
# # # place views on sheets in the right position (get position)
# #
# #
# # # foreach(ScheduleSheetInstance
# # # si in (new FilteredElementCollector(doc).OfClass(typeof(ScheduleSheetInstance))))
# # # {
# # # if (si.OwnerViewId == vs.Id)
# # # {
# # # if (!si.IsTitleblockRevisionSchedule)
# # # {
# # #     foreach(ViewSchedule
# # # vsc in new
# # # FilteredElementCollector(doc).OfClass(typeof(ViewSchedule)))
# # # {
# # # if (si.ScheduleId == vsc.Id)
# # # {
# # #     BoundingBoxXYZ
# # # sibb = si.get_BoundingBox(vs);
# # # XYZ
# # # initialCenter = (sibb.Max + sibb.Min) / 2;
# # #
# # # ScheduleSheetInstance
# # # newssi = ScheduleSheetInstance.Create(doc, newsheet.Id, vsc.Id, XYZ.Zero);
# # #
# # # BoundingBoxXYZ
# # # newsibb = newssi.get_BoundingBox(newsheet);
# # # XYZ
# # # newCenter = (newsibb.Max + newsibb.Min) / 2;
# # #
# # # ElementTransformUtils.MoveElement(doc, newssi.Id, new
# # # XYZ(
# # #     initialCenter.X - newCenter.X,
# # #     initialCenter.Y - newCenter.Y,
# # #     0));
# # # }
# #
# # c_shart = """
# #
# #
# #
# # using System;
# # using System.Collections.Generic;
# # using System.Linq;
# # using System.Data.Linq;
# # using System.Text;
# # using System.IO;
# # //using System.Windows.Forms;
# # using System.Collections;
# #
# # using Autodesk.Revit.ApplicationServices;
# # using Autodesk.Revit.Attributes;
# # using Autodesk.Revit.DB;
# # using Autodesk.Revit.UI;
# # using Autodesk.Revit.UI.Selection;
# # using Autodesk.Revit.DB.Architecture;
# # using Autodesk.Revit.DB.Mechanical;
# # using Autodesk.Revit.DB.Structure;
# #
# # namespace TestDuplicateSheet
# # {
# #     [Autodesk.Revit.Attributes.Transaction(Autodesk.Revit.Attributes.TransactionMode.Manual)]
# #     [Autodesk.Revit.DB.Macros.AddInId("6EF458B5-2974-4A59-994D-BDFA407B2CF6")]
# #     public partial class ThisApplication
# #     {
# #         private void Module_Startup(object sender, EventArgs e)
# #         {
# #
# #         }
# #
# #         private void Module_Shutdown(object sender, EventArgs e)
# #         {
# #
# #         }
# #
# #         #region Revit Macros generated code
# #         private void InternalStartup()
# #         {
# #             this.Startup += new System.EventHandler(Module_Startup);
# #             this.Shutdown += new System.EventHandler(Module_Shutdown);
# #         }
# #         #endregion
# #
# #         public void DuplicateSheet()
# #         {
# #             UIDocument uidoc = this.ActiveUIDocument;
# #             Document doc = uidoc.Document;
# #             ViewSheet vs = doc.ActiveView as ViewSheet;
# #
# #             using (Transaction t = new Transaction(doc, "Duplicate Sheet"))
# #             {
# #                 t.Start();
# #
# #                 FamilyInstance titleblock = new FilteredElementCollector(doc).OfClass(typeof(FamilyInstance)).OfCategory(BuiltInCategory.OST_TitleBlocks).Cast<​FamilyInstance>().First(q => q.OwnerViewId == vs.Id);
# #
# #                 ViewSheet newsheet = ViewSheet.Create(doc, titleblock.GetTypeId());
# #                 newsheet.SheetNumber = vs.SheetNumber + "-DUP";
# #                 newsheet.Name = vs.Name;
# #
# #                 // all views but schedules
# #                 foreach (ElementId eid in vs.GetAllPlacedViews())
# #                 {
# #                     View ev = doc.GetElement(eid) as View;
# #
# #                     View newview = null;
# #
# #                     // legends
# #                     if (ev.ViewType == ViewType.Legend)
# #                     {
# #                         newview = ev;
# #                     }
# #                     // all non-legend and non-schedule views
# #                     else
# #                     {
# #                         ElementId newviewid = ev.Duplicate(ViewDuplicateOption.WithDetailing);
# #                         newview = doc.GetElement(newviewid) as View;
# #                         newview.Name = ev.Name + "-DUP";
# #                     }
# #
# #                     foreach (Viewport vp in new FilteredElementCollector(doc).OfClass(typeof(Viewport)))
# #                     {
# #
# #                         if (vp.SheetId == vs.Id && vp.ViewId == ev.Id)
# #                         {
# #                             BoundingBoxXYZ vpbb = vp.get_BoundingBox(vs);
# #                             XYZ initialCenter = (vpbb.Max + vpbb.Min) / 2;
# #
# #                             Viewport newvp = Viewport.Create(doc, newsheet.Id, newview.Id, XYZ.Zero);
# #
# #                             BoundingBoxXYZ newvpbb = newvp.get_BoundingBox(newsheet);
# #                             XYZ newCenter = (newvpbb.Max + newvpbb.Min) / 2;
# #
# #                             ElementTransformUtils.MoveElement(doc, newvp.Id, new XYZ(
# #                             initialCenter.X - newCenter.X,
# #                             initialCenter.Y - newCenter.Y,
# #                             0));
# #                         }
# #
# #                     }// end for each
# #
# #                 }// end foreach
# #
# #                 // schedules
# #
# #                 foreach (ScheduleSheetInstance si in (new FilteredElementCollector(doc).OfClass(typeof(ScheduleSheetInstance))))
# #                 {
# #                     if (si.OwnerViewId == vs.Id)
# #                     {
# #                         if (!si.IsTitleblockRevisionSchedule)
# #                         {
# #                             foreach (ViewSchedule vsc in new FilteredElementCollector(doc).OfClass(typeof(ViewSchedule)))
# #                             {
# #                                 if (si.ScheduleId == vsc.Id)
# #                                 {
# #                                     BoundingBoxXYZ sibb = si.get_BoundingBox(vs);
# #                                     XYZ initialCenter = (sibb.Max + sibb.Min) / 2;
# #
# #                                     ScheduleSheetInstance newssi = ScheduleSheetInstance.Create(doc, newsheet.Id, vsc.Id, XYZ.Zero);
# #
# #                                     BoundingBoxXYZ newsibb = newssi.get_BoundingBox(newsheet);
# #                                     XYZ newCenter = (newsibb.Max + newsibb.Min) / 2;
# #
# #                                     ElementTransformUtils.MoveElement(doc, newssi.Id, new XYZ(
# #                                         initialCenter.X - newCenter.X,
# #                                         initialCenter.Y - newCenter.Y,
# #                                         0));
# #                                 }
# #                             }
# #                         }
# #
# #                     }
# #                 }// end foreach
# #
# #
# #                 t.Commit();
# #             }// end using
# #
# #
# #
# #
# #
# #     }// end public void duplicate sheet
# #
# #
# #     }// end this applicaton
# # }// end namespace
# #
# #
# # """
