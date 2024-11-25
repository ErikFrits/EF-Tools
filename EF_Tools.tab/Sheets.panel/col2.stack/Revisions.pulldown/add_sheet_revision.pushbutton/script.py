# -*- coding: utf-8 -*-
__title__   = "Create Sheet Revision Stamps"
__version__ = "Version: 1.3"
__author__  = "Erik Frits"
__highlight__ = 'updated'
__doc__ = """Version = 1.3
Date    = 15.11.2019
_____________________________________________________________________
Description:

This tool can create stamp Revision and add it to selected sheets.
You can control description and date of your new revisions.
e.g.  ***___Ausgabe:_SheetNumber___***
_____________________________________________________________________
How-to:

-> Run the script
-> Select Sheets
-> Change setting(optional)
-> Create Revisions
_____________________________________________________________________
Prerequisite:

- At least 1 Sheet in the Project
_____________________________________________________________________
Last update:
- [19.02.2022] - V 1.3 RELEASED
- [19.02.2022] - Added GUI with controls
- [11.07.2021] - V 1.2 RELEASED
- [11.07.2021] - Refactored
_____________________________________________________________________
"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#====================================================================================================
import os
from datetime import date
from pyrevit import forms
from Autodesk.Revit.DB import *
    # (BuiltInParameter,
    #                            RevisionNumberType,
    #                            Revision,
    #                            Transaction,
    #                             FilteredElementCollector
    #
    #                            )
#>>>>>>>>>> CUSTOM IMPORTS
from Snippets._context_manager  import ef_Transaction, try_except
from Snippets._revisions        import create_revision, add_revision_to_sheet
from GUI.forms                  import my_WPF, ListItem

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
uidoc       = __revit__.ActiveUIDocument
app         = __revit__.Application
doc         = __revit__.ActiveUIDocument.Document

PATH_SCRIPT = os.path.dirname(__file__)

all_sheets = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
if not all_sheets: forms.alert('There are no sheets in the project. Please create one and Try Again.',title=__title__,exitscript=True)

# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝
#====================================================================================================
def create_dict_sheet_params():
    #type:()->dict
    """Function to get and filter sheet parameters to display in GUI."""
    PARAMETER_TYPES_ALLOWED = ['String', 'Double', 'Integer']
    PARAMETER_EXCLUDE       = ['Family','Type']
    sheet_parameters        = [s for s in all_sheets[0].Parameters if str(s.StorageType) in PARAMETER_TYPES_ALLOWED]
    dict_sheet_parameters   = {}
    for p in sheet_parameters:
        p_name = p.Definition.Name

        # EXCLUDE PARAMETERS WITH DIFFERENT STORAGE TYPE
        if str(p.StorageType) not in PARAMETER_TYPES_ALLOWED:
            continue

        # REMOVE UNNECESSARY PARAMETERS
        for exclude_p in PARAMETER_EXCLUDE:
            if exclude_p in p_name:
                continue

        # IGNORE EMPTY DUPLICATE OF SHEET NUMBER PARAMETER
        if p_name == "Sheet Number":
            if p.UserModifiable:
                continue

        dict_sheet_parameters[p_name] = p.Id
    return dict_sheet_parameters
dict_sheet_parameters = create_dict_sheet_params() # VARIABLE


def create_List(list_sheets):
    #type:(list) -> List
    """Helper function to create a List<ListItem> to parse it in GUI ComboBox.
    :param list_sheets:   list of sheets
    :return:                List<ListItem>"""
    List_of_sheets= List[type(ListItem())]()
    dict_sheets = {'{} - {}'.format(sheet.SheetNumber, sheet.Name): sheet for sheet in list_sheets}
    for name, sheet in sorted(dict_sheets.items()):
        List_of_sheets.Add(ListItem(name, sheet))
    return List_of_sheets


# ╔═╗╦  ╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝
#==================================================

class CreateSheetRevisions(my_WPF):
    List_all_sheets      = create_List(all_sheets)
    List_filtered_sheets = create_List(all_sheets)

    def __init__(self):
        # GUI
        self.add_wpf_resource()
        path_xaml_file = os.path.join(PATH_SCRIPT, 'CreateSheetRevisions.xaml')
        wpf.LoadComponent(self, path_xaml_file)
        self.UI_ListBox_Sheets.ItemsSource = self.List_filtered_sheets

        self.main_title.Text     = __title__
        self.footer_version.Text = __version__
        self.UI_date.Text = date.today().strftime("*%d.%m.%Y*")

        self.combobox_add_parameters()
        self.ShowDialog()

    #>>>>>>>>>> INHERIT WPF RESOURCES
    def add_wpf_resource(self):
        """Function to get resources from super()"""
        super(CreateSheetRevisions, self).add_wpf_resource()

    def combobox_add_parameters(self):
        """Function to add all TextNoteTypes to ComboBox(self.UI_text_type)."""
        for n, p_name in enumerate(sorted(dict_sheet_parameters.keys())):
            item = ComboBoxItem()
            item.Content    = p_name
            item.IsSelected = True if p_name=='Sheet Number' else False
            self.UI_parameters.Items.Add(item)

    # ╔═╗╔═╗╔╦╗╔╦╗╔═╗╦═╗╔═╗
    # ║ ╦║╣  ║  ║ ║╣ ╠╦╝╚═╗
    # ╚═╝╚═╝ ╩  ╩ ╚═╝╩╚═╚═╝ GETTERS
    #==================================================

    def get_selected_sheets(self):
        """Get a list of selected sheets from ListBox."""
        selected_sheets = []
        for item in self.List_filtered_sheets:
            if item.IsChecked:
                selected_sheets.append(item.element)
        return selected_sheets

    def get_selected_parameter_id(self):
        """Function to get selected parameter.Id from self.parmaeters"""
        for item in self.UI_parameters.Items:
            if item.IsSelected:
                parameter_id = dict_sheet_parameters[item.Content]
                return parameter_id

    # ╔═╗╦ ╦╦  ╔═╗╦  ╦╔═╗╔╗╔╔╦╗╔═╗
    # ║ ╦║ ║║  ║╣ ╚╗╔╝║╣ ║║║ ║ ╚═╗
    # ╚═╝╚═╝╩  ╚═╝ ╚╝ ╚═╝╝╚╝ ╩ ╚═╝
    # ==================================================
    def UI_filter_updated(self, sender, e):
        """EventHandler to filter items in the UI_ListBox_Sheets."""
        List_filtered_sheets = List[type(ListItem())]()
        filter_keyword = self.UI_filter.Text

        # RESTORE ORIGINAL SHEETS
        if not filter_keyword:
            self.List_filtered_sheets = self.List_all_sheets

        # FILTER ITEMS
        dict_sheet_elements = {s.Name:s for s in self.List_all_sheets}
        for sheet_element in dict_sheet_elements.values():
            if filter_keyword.lower() in sheet_element.Name.lower():
                List_filtered_sheets.Add(sheet_element)
            self.List_filtered_sheets = List_filtered_sheets

        # UPDATE LIST OF ITEMS
        self.UI_ListBox_Sheets.ItemsSource = self.List_filtered_sheets
    # ╦═╗╦ ╦╔╗╔
    # ╠╦╝║ ║║║║
    # ╩╚═╚═╝╝╚╝ RUN
    #==================================================
    def button_run(self, sender, e):
        self.Close()
        selected_param_id = self.get_selected_parameter_id()

        # LOOP THROUGH SELECTED SHEETS
        selected_sheets = self.get_selected_sheets()
        if not selected_sheets:
            forms.alert('No Sheets selected. Please Try Again.',title=__title__,exitscript=True)

        print("Total: {} sheets selected.".format(len(selected_sheets)))
        with ef_Transaction(doc, __title__, debug=True):
            for sheet in selected_sheets:
                with try_except(debug=True):
                    # GET PARAMETER
                    sheet_params = sheet.Parameters
                    selected_param = [p for p in sheet_params if p.Id == selected_param_id][0]

                    # GET PARAMETER VALUE
                    p_value = None
                    if   str(selected_param.StorageType) == "String":  p_value = str(selected_param.AsString())
                    elif str(selected_param.StorageType) == "Integer": p_value = str(selected_param.AsInteger())
                    elif str(selected_param.StorageType) == "Double":  p_value = str(selected_param.AsDouble())
                    else: raise("Selected Parameter has unsupported StorageType.")

                    # REVISION NAME + DATE
                    rev_description = self.UI_prefix.Text + p_value + self.UI_suffix.Text
                    rev_date        = self.UI_date.Text
                    rev_type        = None

                    # CREATE and ADD REVISION TO SHEET
                    revision = create_revision(description=rev_description, date=rev_date, revision_type = RevisionNumberType.None)
                    add_revision_to_sheet(sheet=sheet, revision_id=revision.Id)
                    print("Revision [{}] added on the sheet [{}]".format(sheet.SheetNumber, rev_description))

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> MAIN
if __name__ == '__main__':
    x = CreateSheetRevisions()