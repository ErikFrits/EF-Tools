# -*- coding: utf-8 -*-

__title__ = "Sheet Revision History"   # Name of the button displayed in Revit
__author__ = "Erik Frits"
__doc__ = """Version = 0.9 
Date    = 12.07.2021
_____________________________________________________________________
Description:

Create a history of all revision on selected views and export it 
as .csv file.
_____________________________________________________________________
How-To:
>>>REWRITE<<<
1. Select views in Project Browser before running the script.
2. Run the script
3. It should open a folder with .excel files.
4. (optional) You can open them in Excel for readability.

_____________________________________________________________________
TODO:
- #TODO provide relative path.


- REFACTOR THE SCRIPT!!!! SOMETHING IS NOT COMPLETE>...


- Folder structure for output projects -> PROJECT_NAME/DATE_TIME/CSV + ExceL FILES
- CHECK IF VIEW HAS NO REVISIONS
- CHECK IF VIEW HAS NO ADDITIONAL REVISIONS ON SHEET
- CHECK IF VIEW IS NOT ON SHEET

- CHANGE TO SHEET SELECTION INSTEAD! 


_____________________________________________________________________
Last Updates:
- [12.07.2021] ...
_____________________________________________________________________
"""



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> IMPORTS
import os, datetime, csv
from xlsxwriter.workbook import Workbook
from Autodesk.Revit.DB import ( FilteredElementCollector,
                                BuiltInCategory,
                                BuiltInParameter)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> CUSTOM IMPORTS
from lib.Snippets.selection import get_selected_views

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VARIABLES
app = __revit__.Application
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> CLASSES

class GenerateRevisionHistoryFromView:
    """Class for parsing all revisions from the view(clouds + additional revisions) and exporting into a .csv file"""

    def __init__(self,view_id):
        """
        :param view_id: [ElementId]
        """

        self.view_id    = view_id
        self.view_name  = doc.GetElement(view_id).Name


        # >>>>>>>>>> WRITE CSV IF REVISIONS FOUND
        if self.all_revisions:
            self.write_csv_file(self.all_revisions)

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PROPERTIES
    @property
    def all_revisions(self):
        """Function to combine all revisions found related to the view."""
        # >>>>>>>>>> GET REVISIONS FROM VIEW
        cloud_revisions     = self.get_cloud_revision_from_view()
        additional_revision = self.get_additional_revisions_from_sheet()

        if cloud_revisions or additional_revision:
            #>>>>>>>>>> MERGE CLOUD REVISION WITH ADDITIONAL REVISIONS
            all_revisions = cloud_revisions.copy()
            all_revisions.update(additional_revision)
            return all_revisions
        else:
            print("No revisions were found on the view [{}]".format(self.view_name))


    @property
    def filename(self):
        """Function to generate a filename"""


        dir_path = os.path.dirname(os.path.realpath(__file__))
        path_csv_folder = os.path.join(dir_path, 'CSV_FILES_')

        now = datetime.datetime.now().strftime('%y%m%d_%H%M%S')
        filename = path_csv_folder + '\\' + self.view_name + '_' + now + '.csv'

        #>>>>>>>>>> CREATE A FOLDER IF DOESNT EXIST
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(filename)

        #fixme #>>>>>>>>>> OPEN FOLDER
        # os.startfile(path_csv_folder)  # open folder

        return filename


    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> METHODS
    def write_csv_file(self, list_of_revisions):

        all_keys = list_of_revisions.keys()
        all_keys_int = [int(i) for i in all_keys]

        with open(self.filename, mode='wb') as file:
            csv_writer = csv.writer(file, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(['Revit_Seq ', 'Date ', 'Description '])

            for i in sorted(all_keys_int):
                seq = str(i)
                (date, raw_description) = list_of_revisions[seq]
                encoded_description = raw_description.encode("ascii", "ignore")  # remove unwanted chars.
                description = encoded_description.decode()
                csv_writer.writerow([seq, date, description])


    def get_cloud_revision_from_view(self):
        """Get revision from clouds on the view. Both visible and hidden.
        output example: {"Seq_number" : (date, description),}
        """

        all_revision_clouds = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_RevisionClouds).WhereElementIsNotElementType().ToElements()
        revisions = {}

        for cloud in all_revision_clouds:
            if cloud.OwnerViewId == self.view_id:

                #>>>>>>>>>> GET REVISION
                revision_id = cloud.RevisionId
                revision = doc.GetElement(revision_id)

                #>>>>>>>>>> GET REVISION DATA
                description = revision.get_Parameter(BuiltInParameter.PROJECT_REVISION_REVISION_DESCRIPTION).AsString()
                date = revision.get_Parameter(BuiltInParameter.PROJECT_REVISION_REVISION_DATE).AsString()
                seq_num = revision.get_Parameter(BuiltInParameter.PROJECT_REVISION_SEQUENCE_NUM).AsValueString()

                if seq_num not in revisions:
                    revisions[seq_num] = (date, description)

        return revisions


    def get_additional_revisions_from_sheet(self):
        """Get additional revision from sheets. Both visible and hidden.
        output example: {"Seq_number" : (date, description)}
        """
        all_sheets = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()

        out_additional_revisions = dict()

        view = doc.GetElement(self.view_id)
        dependant_views = view.GetDependentViewIds()
        all_related_views = [view] + [doc.GetElement(d_view_id)for d_view_id in dependant_views]

        for view in all_related_views:
            sheet_number = view.get_Parameter(BuiltInParameter.VIEWPORT_SHEET_NUMBER).AsString()
            additional_revisions= None

            if sheet_number:
                #>>>>>>>>>> FIND SHEET
                for sheet in all_sheets:
                    if sheet_number == sheet.SheetNumber:
                        additional_revisions = sheet.GetAdditionalRevisionIds()
                        break
            if additional_revisions:
                for i in additional_revisions:
                    revision        = doc.GetElement(i)
                    description     = revision.get_Parameter(BuiltInParameter.PROJECT_REVISION_REVISION_DESCRIPTION).AsString()
                    date            = revision.get_Parameter(BuiltInParameter.PROJECT_REVISION_REVISION_DATE).AsString()
                    seq_num         = revision.get_Parameter(BuiltInParameter.PROJECT_REVISION_SEQUENCE_NUM).AsValueString()

                    if seq_num not in out_additional_revisions:
                        out_additional_revisions[seq_num] = (date, description)
                        # print("Extra Seq_{} - {} - {}".format(seq_num, date, description))

        return out_additional_revisions




#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> MAIN FUNCTION


def main():

    #>>>>>>>>>> GET SELECTED VIEWS
    selected_views = get_selected_views(exit_if_none=True)


    #>>>>>>>>>> LOOP THROUGH VIEWS
    for view_id in selected_views:
        view_revisions_generator = GenerateRevisionHistoryFromView(view_id)




    #>>>>>>>>>> CREATE EXCEL WORKBOOK
    #fixme RELATIVE PATH
    path = r"N:\2019_STANDARDS\05_Plugin Development Folder\RLP_Dev.extension\RLP_Dev.tab\WorkInProgress.panel\Empty Button 8.pushbutton\CSV_files"
    workbook = Workbook(path +'/test.xlsx')

    #>>>>>>>>>> COMBINE CSV FILES INTO EXCEL
    for csvfile in os.listdir(path):
        if '.csv' in csvfile:
            csvfile_path = os.path.join(path,csvfile)

            worksheet_name = csvfile[:-4]
            if len(worksheet_name)>30:
                worksheet_name = worksheet_name[:30]
            worksheet = workbook.add_worksheet(worksheet_name)
            with open(csvfile_path, 'rt') as f:
                # reader = csv.reader(f, delimiter=',')
                reader = csv.reader(f, delimiter='|')
                for r, row in enumerate(reader):
                    #todo improve on writing/reading .csv
                    for c, col in enumerate(row):
                        worksheet.write(r, c, col)
    workbook.close()



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> MAIN
if __name__ == '__main__':
    main()