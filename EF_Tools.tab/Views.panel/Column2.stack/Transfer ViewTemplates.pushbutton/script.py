# -*- coding: utf-8 -*-
__title__     = "Transfer ViewTemplates"
__version__   = 'Version = 1.0'
__doc__       = """Version = 1.0
Date    = 11.05.2022
_____________________________________________________________________
Description:

You can transfer selected ViewTemplates between Project A/B.
There is an option to override ViewTemplate if same name exists.
Otherwise it will duplicate it by adding a number in the end.
_____________________________________________________________________
How-to:

-> Click on the button
-> Select Project A/B
-> Choose Override or not
-> Select ViewTemplates
-> Click on Transfer ViewTemplates
_____________________________________________________________________
Last update:
- [14.05.2022] - 1.0 RELEASE
_____________________________________________________________________
Author: Erik Frits"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ==================================================
# Regular + Autodesk
import os, sys, math, datetime, time
from collections import defaultdict
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Transaction, FilteredElementCollector

# pyRevit
from pyrevit import forms

# Custom Imports
from GUI.forms import my_WPF, ListItem
from Snippets._context_manager import ef_Transaction

#>>>>>>>>>> .NET IMPORTS
import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System")
from System.Collections.Generic import List
from System.Windows.Controls import ComboBoxItem
from System.Windows          import Visibility
import wpf

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ==================================================
doc     = __revit__.ActiveUIDocument.Document
uidoc   = __revit__.ActiveUIDocument
app     = __revit__.Application
PATH_SCRIPT = os.path.dirname(__file__)

# GLOBAL VARIABLES
dict_projects = {d.Title:d for d in app.Documents if not d.IsFamilyDocument and not d.IsLinked}

# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝ CLASSES
# ==================================================
class CopyViewTemplate(my_WPF):
    doc_from            = None
    doc_to              = None
    List_ViewTemplates  = None
    def __init__(self):

        #>>>>>>>>>> SET RESOURCES FOR WPF
        self.add_wpf_resource()
        path_xaml_file = os.path.join(PATH_SCRIPT, 'CopyViewTemplate.xaml')
        wpf.LoadComponent(self, path_xaml_file )

        # UPDATE GUI ELEMENTS
        self.main_title.Text        = __title__
        self.footer_version.Text    = __version__
        self.ComboBox_add_items()

        # HIDE ViewTemplates + Button section until Projects selected
        self.UI_stack_button.Visibility = Visibility.Collapsed
        self.UI_Stack_ViewTemplates.Visibility = Visibility.Collapsed
        self.UI_Main.Height = 180
        self.ShowDialog()

    def __iter__(self):
        """Return selected items."""
        return iter(self.selected_items )

    #>>>>>>>>>> INHERIT WPF RESOURCES
    def add_wpf_resource(self):
        """Function to get resources from super()"""
        super(CopyViewTemplate, self).add_wpf_resource()

    def ComboBox_add_items(self):
        """Function to Add Project Titles to ComboBoxes on the start of the GUI."""
        for project_name in sorted(dict_projects.keys()):
            item  = ComboBoxItem()
            item2 = ComboBoxItem()
            item.Content    = project_name
            item2.Content    = project_name
            item.IsSelected = False
            item2.IsSelected = False
            self.UI_CopyFrom.Items.Add(item)
            self.UI_CopyTo.Items.Add(item2)

    # ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
    # ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
    # ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
    # ==================================================
    def remove_viewtemplate_same_name(self, selected_viewtemplates_names):
        """This function will scan Project where ViewTemplates is being copied to for ViewTemplates with the same name.
        If there are any matches, it will return a dictionary of a ViewTemplate name and views it is assigned to
        e.g. {ViewTemplate.Name : list(View1,View2)}
        And then it will delete it from the project."""

        # CONTAINER
        dict_used_view_templates_doc_to = defaultdict(list)

        # CHECK IF VIEWTEMPLATES EXISTS AND WHETHER TO OVERRIDE THEM OR NOT
        view_templates_doc_to = [v for v in FilteredElementCollector(self.doc_to).OfClass(View).ToElements() if v.IsTemplate]
        views_doc_to          = [v for v in FilteredElementCollector(self.doc_to).OfClass(View).ToElements() if not v.IsTemplate]

        # DELETE VIEWTEMPLATES WITH SAME NAME + MAKE DICT
        for vt in view_templates_doc_to:
            # CHECK IF SAME NAME EXISTS
            if vt.Name not in selected_viewtemplates_names:
                continue

            # FIND VIEWS WHERE VIEW TEMPLATE USED
            for v in views_doc_to:
                vt_id = v.ViewTemplateId
                if vt_id and vt_id != ElementId(-1):
                    vt_name = self.doc_to.GetElement(vt_id).Name
                    if vt_name in selected_viewtemplates_names:
                        dict_used_view_templates_doc_to[vt_name].append(v.Id)

        # DELETE SIMILAR VIEWTEMPLATES
        for vt in view_templates_doc_to:
            if vt.Name in selected_viewtemplates_names:
                if vt.Name not in dict_used_view_templates_doc_to:
                    dict_used_view_templates_doc_to[vt.Name] = []
                self.doc_to.Delete(vt.Id)

        return dict_used_view_templates_doc_to

    def assign_viewtemplates(self, dict_deleted_view_templates_doc_to):
        for vt_name, list_view_ids in dict_deleted_view_templates_doc_to.items():
            # FIND VIEWTEMPLATE WITH SAME NAME
            view_templates_doc_to = [v for v in FilteredElementCollector(self.doc_to).OfClass(View).ToElements() if
                                     v.IsTemplate]
            new_vt = [v for v in view_templates_doc_to if v.Name == vt_name][0]

            # SET VIEWTEMPLATE TO VIEWS
            for view_id in list_view_ids:
                view = self.doc_to.GetElement(view_id)
                view.ViewTemplateId = new_vt.Id

    # ╔═╗╦ ╦╦  ╔═╗╦  ╦╔═╗╔╗╔╔╦╗╔═╗
    # ║ ╦║ ║║  ║╣ ╚╗╔╝║╣ ║║║ ║ ╚═╗
    # ╚═╝╚═╝╩  ╚═╝ ╚╝ ╚═╝╝╚╝ ╩ ╚═╝ GUI EVENTS
    #==================================================


    def UIe_text_filter_updated(self, sender,e):
        List_filtered_items = List[type(ListItem())]()
        filter_keyword = self.UI_TextBox_Filter.Text

        # RESTORE ORIGINAL LIST
        if not filter_keyword:
            self.UI_ListBox_ViewTemplates.ItemsSource = self.List_ViewTemplates


        # FILTER ITEMS
        for item in self.List_ViewTemplates:
            if filter_keyword.lower() in item.Name.lower():
                List_filtered_items.Add(item)

        # UPDATE LIST OF ITEMS

        self.UI_ListBox_ViewTemplates.ItemsSource = List_filtered_items

    def UIe_ComboBox_Changed(self,sender,e):
        def get_selected(element):
            for item in element.Items:
                if item.IsSelected:
                    return item.Content

        if sender.Name == "UI_CopyTo":
            self.doc_to = dict_projects[get_selected(sender)]

        elif sender.Name == "UI_CopyFrom":
            self.doc_from = dict_projects[get_selected(sender)]


        # Display other settings
        if self.doc_to and self.doc_from:
            if self.doc_from.Title == self.doc_to.Title:
                self.UI_stack_button.Visibility         = Visibility.Collapsed
                self.UI_Stack_ViewTemplates.Visibility  = Visibility.Collapsed
                self.UI_Main.Height = 180

            else:
                self.UI_stack_button.Visibility         = Visibility.Visible
                self.UI_Stack_ViewTemplates.Visibility  = Visibility.Visible
                self.UI_Main.Height = 685


                # Update ViewTemplates ListBox

                view_templates = [v for v in FilteredElementCollector(self.doc_from).OfClass(View).ToElements() if v.IsTemplate]
                dict_view_templates = {v.Name: v for v in view_templates}

                List_viewtemplates = List[type(ListItem())]()

                for name in sorted(dict_view_templates):
                    item = ListItem(name, dict_view_templates[name], False)
                    List_viewtemplates.Add(item)

                self.List_ViewTemplates = List_viewtemplates
                self.UI_ListBox_ViewTemplates.ItemsSource = List_viewtemplates


    # ╔╗ ╦ ╦╔╦╗╔╦╗╔═╗╔╗╔╔═╗
    # ╠╩╗║ ║ ║  ║ ║ ║║║║╚═╗
    # ╚═╝╚═╝ ╩  ╩ ╚═╝╝╚╝╚═╝ BUTTONS
    #==================================================
    def select_mode(self, mode):
        """Helper function for following buttons:
        - button_select_all
        - button_select_none"""

        list_of_items = List[type(ListItem())]()
        checked = True if mode=='all' else False
        for item in self.UI_ListBox_ViewTemplates.ItemsSource:
            item.IsChecked = checked
            list_of_items.Add(item)

        self.UI_ListBox_ViewTemplates.ItemsSource = list_of_items

    def UIe_btn_select_all(self, sender, e):
        """ """
        self.select_mode(mode='all')

    def UIe_btn_select_none(self, sender, e):
        """ """
        self.select_mode(mode='none')

    def UIe_btn_run(self,sender,e):
        self.Close()

        # SELECTED VIEWTEMPLATES
        selected_viewtemplates = [item.element for item in self.UI_ListBox_ViewTemplates.ItemsSource if item.IsChecked]
        selected_viewtemplates_ids = [vt.Id for vt in selected_viewtemplates]
        selected_viewtemplates_names = [vt.Name for vt in selected_viewtemplates]

        # CHECK IF VIEWTEMPLATE SELECTED
        if not selected_viewtemplates_ids:
            forms.alert('There were no ViewTemplates selected. Please Try Again',title=__title__, exitscript=True)

        # REPORT
        print("Copying ViewTemplates")
        print('From: {}'.format(self.doc_from.Title))
        print('To: {}'.format(self.doc_to.Title))
        print('-'*50)

        with TransactionGroup(doc, __title__) as tg:
            tg.Start()

            # REMOVE VIEWTEMPLATES WITH SAME NAME AS SELECTED
            dict_deleted_view_templates_doc_to = {}
            if self.UI_check_override.IsChecked:
                with ef_Transaction(self.doc_to, 'Remove Same ViewTemplates', debug=True, exitscript=True):
                    dict_deleted_view_templates_doc_to = self.remove_viewtemplate_same_name(selected_viewtemplates_names)

            # COPY VIEWTEMPLATES
            List_selected_viewtemplates = List[ElementId](selected_viewtemplates_ids)
            copy_opts = CopyPasteOptions()
            with ef_Transaction(self.doc_to, 'Copy ViewTemplates', debug=True):
                ElementTransformUtils.CopyElements(self.doc_from,
                                                   List_selected_viewtemplates,
                                                   self.doc_to,
                                                   Transform.Identity,
                                                   copy_opts)

            # ASSIGN VIEWTEMLATE TO VIEWS THAT HAD SAME VIEWTEMPLATE NAME
            if self.UI_check_override.IsChecked:
                with ef_Transaction(self.doc_to,'Assign ViewTemplates', debug=True):
                    self.assign_viewtemplates(dict_deleted_view_templates_doc_to)

            tg.Assimilate()


        # REPORT
        for vt in selected_viewtemplates:
            if vt.Name in dict_deleted_view_templates_doc_to.keys():
                print("[Updated    ] - {}".format(vt.Name))
            else:
                print('[Added New] - {}'.format(vt.Name))
        print('-'*50)
        was_were = 'ViewTemplates were' if len(selected_viewtemplates) > 1 else 'ViewTemplate was'
        print('Script is complete.\n {} {} Transfered.'.format(len(selected_viewtemplates),was_were))

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
# ==================================================
if __name__ == '__main__':
    CopyViewTemplate()
