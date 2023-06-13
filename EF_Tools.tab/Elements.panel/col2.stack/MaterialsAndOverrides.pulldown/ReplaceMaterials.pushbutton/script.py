# -*- coding: utf-8 -*-
__title__ = "Replace Materials"
__version__ = 'Version = 1.1'
__doc__ = """Version = 1.1
Date    = 31.08.2022
_____________________________________________________________________
Description:
This tool will let you replace materials in your project.

It will search for material in all Instance and Type parameters,
and in case of WallType, FloorType, RoofType and CeilingType it 
will also look in the compound structure.

_____________________________________________________________________
How-to:
-> Click on the button
-> Select Categories
-> Choose Material to Find
-> Choose Material to Replace
-> Replace Materials
_____________________________________________________________________
Last update:
-[31.08.2022] - 1.0 RELEASE
_____________________________________________________________________
To-Do:
- Fix Reporting Materials changed 
- InPlace Elements Materials
- Only used materials in Find!
- ComboBox Filtering 
- Painted Surfaces (Replace/Remove?)
_____________________________________________________________________
Author: Erik Frits"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ==================================================
# Regular + Autodesk
from Autodesk.Revit.DB import *
import os

# pyRevit
from pyrevit import forms

# Custom Imports
from GUI.forms import  my_WPF
from Snippets._context_manager import ef_Transaction

# .NET Imports
import clr
clr.AddReference("System")
from System.Collections.Generic import List
from System.Windows.Controls import ComboBoxItem
import wpf

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ==================================================
doc   = __revit__.ActiveUIDocument.Document # Document   class from RevitAPI that represents project. Used to Create, Delete, Modify and Query elements from the project.
uidoc = __revit__.ActiveUIDocument          # UIDocument class from RevitAPI that represents Revit project opened in the Revit UI.
app   = __revit__.Application               # Represents the Autodesk Revit Application, providing access to documents, options and other application wide data and settings.
PATH_SCRIPT = os.path.dirname(__file__)     # Absolute path to the folder where script is placed.

# MATERIALS
all_materials   = list(FilteredElementCollector(doc).OfClass(Material).ToElements())
dict_materials  = {mat.Name : mat for mat in all_materials}
all_materials.sort(key=lambda x: x.Name)


# ╔═╗╦  ╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝
class ReplaceMaterials(my_WPF):
    mat_find_id    = None
    mat_replace_id = None
    count          = 0

    def __init__(self):
        # Add Resources and XAML
        self.add_wpf_resource()
        path_xaml_file = os.path.join(PATH_SCRIPT, 'ReplaceMaterials.xaml')
        wpf.LoadComponent(self, path_xaml_file)

        # Add Materials to Comboboxes
        self.combobox_add_items()

        # Replace GUI Text Values
        self.main_title.Text     = __title__
        self.footer_version.Text = __version__

        self.ShowDialog()

    # ╔═╗╦ ╦╦  ╔═╗╔═╗╔╗╔╔╦╗╦═╗╔═╗╦  ╔═╗
    # ║ ╦║ ║║  ║  ║ ║║║║ ║ ╠╦╝║ ║║  ╚═╗
    # ╚═╝╚═╝╩  ╚═╝╚═╝╝╚╝ ╩ ╩╚═╚═╝╩═╝╚═╝ GUI CONTROLS
    # ==================================================
    #>>>>>>>>>> GUI CONTROLS
    def add_wpf_resource(self):
        """Function to get resources from super()"""
        super(ReplaceMaterials, self).add_wpf_resource()

    def combobox_add_items(self):
        """Function to add all Materials to ComboBox(self.UI_mat_replace, self.UI_mat_find)."""

        def create_item(name, selected):
            """Function to create new ComboBoxItem."""
            item            = ComboBoxItem()
            item.Content    = name
            item.IsSelected = selected
            return item

        # ADD 'None' TO THE COMBOBOXES
        self.UI_mat_find.Items.Add(create_item('<By Category>', False))
        self.UI_mat_replace.Items.Add(create_item('<By Category>', False))

        for n, mat in enumerate(all_materials):
            self.UI_mat_find.Items.Add(create_item(mat.Name, True if n==0 else False))
            self.UI_mat_replace.Items.Add(create_item(mat.Name, True if n==0 else False))


    def get_selected_materials(self):
        """Function to get selected items from ComboBoxes."""
        def get_mat(items):
            """Function to get selected item from Combobox.Items."""
            for item in items:
                if item.IsSelected:
                    if item.Content == '<By Category>' or item.Content == None:
                        return ElementId(-1)
                    else:
                        return dict_materials[item.Content].Id

        self.mat_find_id    = get_mat(self.UI_mat_find.Items)
        self.mat_replace_id = get_mat(self.UI_mat_replace.Items)


    # ╔╦╗╔═╗╔╦╗╦ ╦╔═╗╔╦╗╔═╗
    # ║║║║╣  ║ ╠═╣║ ║ ║║╚═╗
    # ╩ ╩╚═╝ ╩ ╩ ╩╚═╝═╩╝╚═╝
    # ==================================================
    def get_elements(self):
        #type:() -> FilteredElementCollector
        """Function to create a ElementMulticategoryFilter based on
        categories selected in GUI."""

        # GET SELECTED CATEGORIES
        List_categories = List[BuiltInCategory]()

        if self.UI_cat_walls.IsChecked:
            List_categories.Add(BuiltInCategory.OST_Walls)

        if self.UI_cat_floors.IsChecked:
            List_categories.Add(BuiltInCategory.OST_Floors)

        if self.UI_cat_roofs.IsChecked:
            List_categories.Add(BuiltInCategory.OST_Roofs)

        if self.UI_cat_ceilings.IsChecked:
            List_categories.Add(BuiltInCategory.OST_Ceilings)

        if self.UI_cat_columns.IsChecked:
            List_categories.Add(BuiltInCategory.OST_Columns)
            List_categories.Add(BuiltInCategory.OST_StructuralColumns)

        if self.UI_cat_beams.IsChecked:
            List_categories.Add(BuiltInCategory.OST_StructuralFraming)

        if self.UI_cat_foundation.IsChecked:
            List_categories.Add(BuiltInCategory.OST_StructuralFoundation)

        if self.UI_cat_windows.IsChecked:
            List_categories.Add(BuiltInCategory.OST_Windows)

        if self.UI_cat_doors.IsChecked:
            List_categories.Add(BuiltInCategory.OST_Doors)

        if self.UI_cat_generic_models.IsChecked:
            List_categories.Add(BuiltInCategory.OST_GenericModel)

        if self.UI_cat_stairs.IsChecked:
            List_categories.Add(BuiltInCategory.OST_Stairs)

        if self.UI_cat_casework.IsChecked:
            List_categories.Add(BuiltInCategory.OST_Casework)

        if self.UI_cat_furniture.IsChecked:
            List_categories.Add(BuiltInCategory.OST_Furniture)
            List_categories.Add(BuiltInCategory.OST_FurnitureSystems)

        if self.UI_cat_plumbing.IsChecked:
            List_categories.Add(BuiltInCategory.OST_PlumbingFixtures)

        if self.UI_cat_pipes.IsChecked:
            List_categories.Add(BuiltInCategory.OST_PipeCurves)
            List_categories.Add(BuiltInCategory.OST_PipeFitting)
            List_categories.Add(BuiltInCategory.OST_PipeInsulations)
            List_categories.Add(BuiltInCategory.OST_PipeAccessory)

        if self.UI_cat_ducts.IsChecked:
            List_categories.Add(BuiltInCategory.OST_DuctCurves)
            List_categories.Add(BuiltInCategory.OST_DuctFitting)
            List_categories.Add(BuiltInCategory.OST_DuctInsulations)
            List_categories.Add(BuiltInCategory.OST_DuctAccessory)


        # COMBINE FILTERS AND GET ELEMENTS
        filter_multi_cat = ElementMulticategoryFilter(List_categories)
        self.elements    = FilteredElementCollector(doc).WherePasses(filter_multi_cat).ToElements()


    def change_mat_compound(self, elem_type):
        """Function to change material in Types with CompoundStructure
        such as: WallType, FloorType, RoofType, CeilingType"""
        Exclude = ['Curtain Wall', 'Sloped Glazing', 'Basic Ceiling']
        try:
            if elem_type.FamilyName in Exclude:
                return

            # GET LAYERS
            structure = elem_type.GetCompoundStructure()

            # LOOP THROUGH LAYERS
            for layer in structure.GetLayers():
                if self.mat_find_id == ElementId(-1):
                    if layer.MaterialId == ElementId(-1):
                        structure.SetMaterialId(layer.LayerId, self.mat_replace_id)
                        elem_type.SetCompoundStructure(structure)
                        self.count += 1

                elif layer.MaterialId != ElementId(-1):
                    # GET MATERIAL
                    mat = doc.GetElement(layer.MaterialId)
                    # CHANGE MATERIAL
                    if mat.Id == self.mat_find_id:
                        structure.SetMaterialId(layer.LayerId, self.mat_replace_id)
                        elem_type.SetCompoundStructure(structure)
                        self.count += 1

        except:
            # This exception will be triggered on 'Curtain Wall', 'Sloped Glazing', 'Basic Ceiling'
            # import traceback
            # print(traceback.format_exc())
            pass

    def change_mat_param(self, elem):
        """This function will go through all available parameters and look
        for Material parameter. If there is a match with mat_find then it will
        replace this material if it's not inside a group and not VariesAcrissGroups."""
        # Check if Element is part of a group and VariesAcross
        groupped = False if elem.GroupId == ElementId(-1) else True

        for p in elem.Parameters:
            try:
                if groupped and not p.Definition.VariesAcrossGroups:
                    continue

                if p.Definition.ParameterType == ParameterType.Material:
                    if p.AsElementId() == self.mat_find_id:
                        if not p.IsReadOnly:
                            p.Set(self.mat_replace_id)
                            self.count += 1
            except:
                pass

    def replace_materials(self):
        """Function to Find and Replace Materials in selected categories."""
        with ef_Transaction(doc, __title__):
            compound_types = [WallType, FloorType, RoofType, CeilingType]
            for el in self.elements:
                # Element with Compound Structure (Wall,Floor,Roof,Ceiling)
                if type(el) in compound_types:
                    self.change_mat_compound(el)

                self.change_mat_param(el)

    # ╦═╗╦ ╦╔╗╔
    # ╠╦╝║ ║║║║
    # ╩╚═╚═╝╝╚╝ RUN
    #==================================================

    def button_run(self, sender, e):
        """Replace Materials"""
        if not self.UI_keep_open.IsChecked:
            self.Close()

        self.get_selected_materials()

        # if self.mat_find_id == ElementId(-1):
        #     forms.alert("You Can't choose 'None' in Find.\nPlease change and Try Again",title=__title__)
        #     return

        self.get_elements()
        self.get_selected_materials()
        self.replace_materials()

        print('In Total: Material was replaced in {} Parameters.'.format(self.count))

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
# ==================================================
if __name__ == '__main__':
    x = ReplaceMaterials()
