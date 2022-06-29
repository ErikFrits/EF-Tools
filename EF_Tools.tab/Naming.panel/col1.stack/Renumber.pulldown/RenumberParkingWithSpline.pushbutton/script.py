# -*- coding: utf-8 -*-
__title__ = "Renumber Parking with Spline"
__author__ = "Erik Frits"
__version__ = "Version 1.0"
__doc__ = """Version = 1.0
Date    = 17.04.2022
_____________________________________________________________________
Description:
Renumber parking spaces visible in an ActiveView with selected Curve
_____________________________________________________________________
How-to:
-> Click on Button
-> Provide required parameters
-> Renumber Parkings
_____________________________________________________________________
Last update:
- [17.04.2022] - 1.0 RELEASE
_____________________________________________________________________
TO-DO:
- Get points on Line with a fixed distance!!!! 
Check Elements on Curve Prototype


_____________________________________________________________________
Author:  Erik Frits"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
#==================================================
import os, traceback
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *

# pyRevit
from pyrevit import forms


# Custom
from GUI.forms                  import my_WPF, ListItem
from Snippets._selection        import pick_curve
from Snippets._lines            import get_points_along_a_curve
from Snippets._boundingbox      import is_point_in_BB_2D
from Snippets._context_manager  import ef_Transaction

#>>>>>>>>>> .NET IMPORTS
import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System")
from System.Collections.Generic import List
from System.Windows.Controls import ComboBoxItem
import wpf

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
#==================================================
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application
PATH_SCRIPT = os.path.dirname(__file__)

# SELECT CURVE
with forms.WarningBar(title="Pick Curve for Parkings Numbering:", handle_esc=True):
    selected_curve = pick_curve(uidoc)
if not selected_curve:
    forms.alert("Curve was not selected. \nPlease Try Again.", title = __title__, exitscript=True)

# ╔═╗╦  ╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝
#==================================================
class ParkingRenumbering(my_WPF):
    step = 0.1

    def __init__(self):
        self.add_wpf_resource()
        path_xaml_file = os.path.join(PATH_SCRIPT, 'RenumberParking.xaml')
        wpf.LoadComponent(self, path_xaml_file)
        self.combobox_add_parameters()

        self.main_title.Text     = __title__
        self.footer_version.Text = __version__
        self.ShowDialog()
    #>>>>>>>>>> INHERIT WPF RESOURCES
    def add_wpf_resource(self):
        """Function to get resources from super()"""
        super(ParkingRenumbering, self).add_wpf_resource()

    def combobox_add_parameters(self):
        """Function to add all TextNoteTypes to ComboBox(self.UI_text_type)."""
        random_parking = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Parking).WhereElementIsNotElementType().FirstElement()
        if not random_parking:
            forms.alert('Could not find any Parking in the Project. \nPlease Try Again', title=__title__, exitscript=True)

        text_params = [p for p in random_parking.Parameters if p.StorageType == StorageType.String and not p.IsReadOnly]
        self.dict_text_params = {p.Definition.Name:p for p in text_params}

        for n, param_name in enumerate(self.dict_text_params):
            item = ComboBoxItem()
            item.Content    = param_name
            item.IsSelected = True if n==0 else False
            self.UI_parameters.Items.Add(item)

    def get_selected_parameter(self):
        """Function to get selected parameter from self.UI_parameters ComboBox."""
        for item in self.UI_parameters.Items:
            if item.IsSelected:
                return self.dict_text_params[item.Content]


    def renumber_parking_in_view(self):
        """Function to renumber parking spaces with order based on points along selected line."""
        with ef_Transaction(doc,__title__, debug=True):
            all_parkings_in_view = list(FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(BuiltInCategory.OST_Parking).WhereElementIsNotElementType().ToElements())
            if not all_parkings_in_view:
                forms.alert('Could not find any Parking in the current view. \nPlease Try Again',title=__title__,exitscript=True)

            points = get_points_along_a_curve(selected_curve, step=self.step)

            sel_param_id = self.get_selected_parameter().Id

            for pt in points:
                for parking in all_parkings_in_view:
                    try:
                        BB = parking.get_BoundingBox(doc.ActiveView)
                        if is_point_in_BB_2D(BB,pt):

                            # RENUMBER
                            param = None
                            for par in parking.Parameters:
                                if par.Id == sel_param_id:
                                    param = par
                                    break

                            if param:
                                value = self.prefix + str(self.count) + self.suffix
                                param.Set(value)
                                self.count += 1
                                all_parkings_in_view.remove(parking)
                                break
                    except:
                        print("***Couldn't number Parking({})".format(parking.Id))
                        print(traceback.format_exc() + "***")
    # ╦═╗╦ ╦╔╗╔
    # ╠╦╝║ ║║║║
    # ╩╚═╚═╝╝╚╝ RUN
    # ==================================================
    def button_run(self, sender, e):
        self.Close()
        self.count              = int(self.UI_count.Text)
        self.prefix             = self.UI_prefix.Text
        self.suffix             = self.UI_suffix.Text
        self.renumber_parking_in_view()

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
#==================================================
if __name__ == '__main__':
    ParkingRenumbering()
