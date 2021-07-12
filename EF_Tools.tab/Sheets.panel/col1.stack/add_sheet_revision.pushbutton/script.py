# -*- coding: utf-8 -*-

__title__   = "Add Sheet Revisions"
__author__  = "Erik Frits"
__doc__ = """Version = 1.2
Date    = 15.11.2019
_____________________________________________________________________
Description:

Create Sheet revision stamp on selected sheets.
e.g.  ***___Ausgabe_SheetNumber___***
_____________________________________________________________________
How-to:

-> Run the script
-> Select Sheets
_____________________________________________________________________
Prerequisite:

Output pattern has to be hardcoded inside the code!
Video will be available later!
_____________________________________________________________________
Last update:
- [11.07.2021] - V 1.2 RELEASED
- [11.07.2021] - Refactored
- [11.07.2021] - 
_____________________________________________________________________
To-do:
- Alternative sheet selection
- GUI Pattern controls?
- GUI
_____________________________________________________________________
"""

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> IMPORTS
from datetime import date
from pyrevit import forms
from Autodesk.Revit.DB import (BuiltInParameter,
                               RevisionNumberType,
                               Revision,
                               Transaction,
                               )

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VARIABLES
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application
doc = __revit__.ActiveUIDocument.Document

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> FUNCTIONS
def get_sheets():
    """Function to get selected sheets."""
    ###_______________SHEETS SELECTION
    Sheets = forms.select_sheets(title="Select sheets to Open Revision Batch", button_name="Create and Add Revision",
                                 width=1000)
    if not Sheets:
        forms.alert("No sheets were selected.\nPlease, try again.", exitscript=True, title="Script Cancelled.")
    return Sheets


def create_revision(sheet):
    """Function to create new revision and assign it to the given sheet."""
    # VALUES FOR PATTERN
    date_today = date.today().strftime("%d.%m.%Y")
    sheet_number = sheet.get_Parameter(BuiltInParameter.SHEET_NUMBER).AsString()

    # PATTERN
    description_pattern = "*** Ausgabe: {} ***".format(sheet_number)

    # NEW REVISION
    new_rev = Revision.Create(doc)
    new_rev.Description = description_pattern
    new_rev.RevisionDate = date_today
    new_rev.NumberType = RevisionNumberType.None

    # GET EXISTING ADDITIONAL REVISIONS
    exist_rev = sheet.GetAdditionalRevisionIds()

    # ADD NEW REVISION TO THE LIST
    exist_rev.Add(new_rev.Id)

    # SET NEW LIST OF ADDITIONAL REVISIONS
    sheet.SetAdditionalRevisionIds(exist_rev)

    print(description_pattern + " Revision - Was Created.")

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> MAIN
if __name__ == '__main__':
    selected_sheets = get_sheets()
    print("Total {} sheets selected.".format(len(selected_sheets)))

    t = Transaction(doc, __title__)
    t.Start()
    for sheet in selected_sheets:
        create_revision(sheet)
    t.Commit()



