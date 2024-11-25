# -*- coding: utf-8 -*-

__title__ = "Sheet Revision History"
__author__ = "Erik Frits"
__doc__ = """Version = 1.1
Date    = 20.01.2021
_____________________________________________________________________
Description:

Create a history of all revisions on selected sheets and export it 
to an Excel file.
_____________________________________________________________________
How-To:

-> Select sheets in Project Browser before running the script.
-> Run the script
-> Choose if you want to use other sheets if they share 
   same primary view.
-> It should open a folder with new Excel file.
_____________________________________________________________________
Prerequisite:

Revision clouds should not be deleted from their views, 
but hidden instead! Otherwise the script will not be able 
to detect which revisions were associated with the views.
_____________________________________________________________________
Last Updates:

- [25.07.2021] - 1.1 RELEASE
- [25.07.2021] - Refactoring
- [25.07.2021] - Script logic changed
- [25.07.2021] - Promt user if dependant views and their sheets 
should be included.
- [15.07.2021] - 1.0 RELEASE
- [15.07.2021] - Write to excel 
- [15.07.2021] - Refactoring
- [20.01.2021] - 0.1 RELEASE
_____________________________________________________________________
"""

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> IMPORTS
import os, datetime, csv
from xlsxwriter.workbook import Workbook, Worksheet
from Autodesk.Revit.DB import ( FilteredElementCollector,
                                BuiltInCategory,
                                BuiltInParameter)
from Snippets._selection import get_selected_sheets
from Snippets._views import get_sheet_from_view

#>>>>>>>>>> .NET IMPORTS
import clr
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import (DialogResult, MessageBox,MessageBoxButtons)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VARIABLES
app     = __revit__.Application
uidoc   = __revit__.ActiveUIDocument
doc     = __revit__.ActiveUIDocument.Document

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> FUNCTIONS

def promt_user_incl_primary_and_dependant():
    """Function to show Yes/No dialog box to a user asking
    'Incl primary and dependant views and sheets?' """
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PROMT USER YES/NO
    dialogResult = MessageBox.Show('Would you like to include Primary and Dependant views and their respective sheets that they are placed on as well?',
                                    __title__,
                                    MessageBoxButtons.YesNo)
    if (dialogResult == DialogResult.Yes):
        return True
    return False


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> CLASSES
class Revisions_on_sheet():
    def __init__(self, sheet, include_primary_and_dependant):
        """Class to get all revisions related to the given sheet.
        :param sheet:                           ViewSheet
        :param include_primary_and_dependant:   bool      - Include other sheets that share the same primary view! """

        self.include_primary_and_dependant = include_primary_and_dependant
        self.sheet      = sheet
        self.view_ids   = self.get_view_ids()

    def get_view_ids(self):
        """Function to get view ids from the sheet given in __init__.
        Dependant views will be added based on include_primary_and_dependant parameter.
        """

        #>>>>>>>>>> VIEWPORTS ON SELECTED SHEET
        viewports_ids       = self.sheet.GetAllViewports()
        viewports           = [doc.GetElement(viewport_id) for viewport_id in viewports_ids]

        #>>>>>>>>>> VIEWS ON SELECTED SHEET
        views_on_sheet_ids = [viewport.ViewId for viewport in viewports]
        views_on_sheet     = [doc.GetElement(view_id) for view_id in views_on_sheet_ids]

        # >>>>>>>>>> PRIMARY VIEWS - clouds always reside on primary views instead of dependant ones
        primary_view_ids   = [view.GetPrimaryViewId() for view in views_on_sheet]
        primary_views      = [doc.GetElement(view_id) for view_id in primary_view_ids if doc.GetElement(view_id)]

        #>>>>>>>>>> RETURN VIEWS WITH DEPENDANT ONES
        if self.include_primary_and_dependant:

            # >>>>>>>>>> RETURN VIEWS ON SHEET + PRIMARY VIEWS + DEPENDANT VIEWS
            all_dependant_views = {}
            views_ = views_on_sheet + primary_views
            for view in views_:
                dependant_views_ids = view.GetDependentViewIds()
                dependant_views     = [doc.GetElement(view_id) for view_id in dependant_views_ids]
                for view in dependant_views:
                    if view.Name not in all_dependant_views:
                        all_dependant_views[view.Name] = view

            dependant_views = all_dependant_views.values()

            #>>>>>>>>>> COMBINE ALL VIEWS
            all_views = views_on_sheet + primary_views + dependant_views
            all_view_ids = [view.Id for view in all_views]
            return all_view_ids

        #>>>>>>>>>> RETURN VIEWS ON SHEET + PRIMARY VIEWS(clouds always on primary)
        return views_on_sheet_ids + primary_view_ids

    @property
    def all_revisions(self):
        """Function to combine all cloud revisions and additional sheet revisions."""
        all_revisions = self.cloud_revisions + self.additional_revisions
        return all_revisions

    @property
    def additional_revisions(self):
        """Get all revisions from given sheet(s)."""

        #>>>>>>>>>> ADDITIONAL REVISIONS - FROM ALL RELATED SHEETS
        if self.include_primary_and_dependant:
            views       = [doc.GetElement(view_id) for view_id in self.view_ids]
            all_sheets  = [get_sheet_from_view(view) for view in views if get_sheet_from_view(view)] + [self.sheet]
            sheets      = list({sheet.SheetNumber : sheet for sheet in all_sheets}.values())

            #>>>>>>>>>> LOOP THROUGH SHEETS
            additional_revisions = {}
            for sheet in sheets:
                sheet_revisions = [doc.GetElement(revision_id) for revision_id in sheet.GetAdditionalRevisionIds()]
                for revision in sheet_revisions:
                    revision_seq = revision.get_Parameter(BuiltInParameter.PROJECT_REVISION_SEQUENCE_NUM).AsValueString()
                    if revision_seq not in additional_revisions:
                        additional_revisions[revision_seq] = revision
            return additional_revisions.values()

        #>>>>>>>>>> ADDITIONAL REVISIONS - FROM GIVEN SHEET
        additional_revisions_ids = self.sheet.GetAdditionalRevisionIds()
        additional_revisions     = [doc.GetElement(revision_id) for revision_id in additional_revisions_ids]
        return additional_revisions

    @property
    def cloud_revisions(self):
        """Get all revisions from clouds on views."""
        all_revision_clouds = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_RevisionClouds).WhereElementIsNotElementType().ToElements()
        cloud_revisions = [doc.GetElement(cloud.RevisionId) for cloud in all_revision_clouds if str(cloud.OwnerViewId) in [str(i) for i in self.view_ids]]
        return cloud_revisions



class ExcelWriter:

    def __init__(self, data):
        """Class to create an Excel file and write there list of revision based on given data.
        :param data:  Data format - { 'Sheet_Number' : list_Revisions }"""

        self.data       = data
        self.count      = 0
        self.workbook   = self.create_excel_workbook()

        try     : self.write_data()
        except  : raise(Exception("Exception occured while writting data to an Excel file."))
        finally : self.workbook.close()

    def write_data(self):
        """[MAIN]Function to iterate through the given data and write each to a worksheet."""
        for sheet_number in self.data:
            new_worksheet = self.create_excel_worksheet(sheet_number)
            revisions       = self.data[sheet_number]
            self.write_revision_data(new_worksheet, revisions, sheet_number)

    def write_revision_data(self, worksheet, revisions, sheet_number):
        #type:(Worksheet, list,str) -> None
        """ Function to write given list of revisions to worksheet
        :param worksheet:    Worksheet
        :param revisions:    list of Revisions
        :param sheet_number: sheet.SheetNumber
        :return: None """

        #>>>>>>>>>> REVISION DATA CONTAINER
        dict_all_revisions = {}

        #>>>>>>>>>> GET REVISION DATA
        for revision in revisions:
            description     = revision.get_Parameter(BuiltInParameter.PROJECT_REVISION_REVISION_DESCRIPTION).AsString()
            date            = revision.get_Parameter(BuiltInParameter.PROJECT_REVISION_REVISION_DATE).AsString()
            seq_num         = int(revision.get_Parameter(BuiltInParameter.PROJECT_REVISION_SEQUENCE_NUM).AsValueString().replace("Seq.",""))

            if seq_num not in dict_all_revisions:
                dict_all_revisions[seq_num] = (date, description)


        #>>>>>>>>>> SORT
        ordered_seq = sorted([int(seq) for seq in dict_all_revisions.keys()])

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PREPARE DATA FOR EXCEL
        #>>>>>>>>>> ADD FIRST 3 LINES OF WORKSHEET HARDCODED
        list_of_data = [
            ("SheetNumber: " ,sheet_number),
            ('',),
            ('Seq.', 'Date', 'Description')
        ]

        print("Sheet [{}]".format(sheet.Name))
        for seq in ordered_seq:
            date        = dict_all_revisions[seq][0]
            description = dict_all_revisions[seq][1]
            print("Seq.{} ({}) - {}".format(seq, date, description))
            list_of_data.append((seq, date, description))

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> WRITE IN EXCEL
        for r, row in enumerate(list_of_data):
            for c, col in enumerate(row):
                worksheet.write(r, c, col)
        print('_' * 120)

    def create_excel_worksheet(self, sheet_number):
        #type:(str) -> Worksheet
        """Function to add a worksheet to the created self.workbook with its name derived from sheet_number
        :param sheet_number: str(sheet.SheetNumber)
        :return: Worksheet  """

        #>>>>>>>>>> CREATE WORKSHEET
        worksheet_name = sheet_number if len(sheet_number) < 26 else sheet_number[:26]  # max lenght = 30!
        worksheet_name = '{}_'.format(self.count) + worksheet_name
        self.count +=1
        worksheet = self.workbook.add_worksheet(worksheet_name)
        return worksheet

    def create_excel_workbook(self):
        """Function to create an Excel Workbook."""
        path = self.excel_filename
        path_dir = os.path.dirname(path)
        if not os.path.exists(path_dir): os.makedirs(path_dir)
        workbook = Workbook(path)
        return workbook

    @property
    def excel_filename(self):
        """Generate filename with a timestamp for an Excel file."""
        dir = os.path.dirname(__file__)
        doc_name = doc.Title
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return "{}/Excel/{}_{}.xlsx".format(dir, doc_name, timestamp)



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> MAIN
if __name__ == '__main__':

    #>>>>>>>>>> GET SELECTED SHEETS
    selected_sheets = get_selected_sheets(exit_if_none=True, title=__title__)

    #>>>>>>>>>> ASK USER TO INCLUDE PRIMARY AND DEPENDANT
    incl_primary_and_dependant = promt_user_incl_primary_and_dependant()

    #>>>>>>>>>> CONTAINER FOR ALL REVISIONS ON SELECTED SHEETS
    all_sheets_revisions = {}

    #>>>>>>>>>> GET REVISIONS FROM EACH SELECTED SHEET
    for sheet in selected_sheets:
        revision_seeker = Revisions_on_sheet(sheet, incl_primary_and_dependant)
        sheet_revisions = revision_seeker.all_revisions
        all_sheets_revisions[sheet.SheetNumber] = sheet_revisions

    #>>>>>>>>>> EXCEL WRITER
    xlsx = ExcelWriter(all_sheets_revisions)

    # >>>>>>>>>> OPEN FOLDER WITH EXCEL
    os.startfile(os.path.dirname(xlsx.excel_filename))