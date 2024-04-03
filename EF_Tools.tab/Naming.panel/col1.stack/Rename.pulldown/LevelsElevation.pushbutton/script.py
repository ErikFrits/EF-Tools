# -*- coding: utf-8 -*-
__title__ = "Level Elevation: Add/Remove "
__author__ = "Erik Frits"
__version__ = "Version = 1.0"
__doc__ = """Version = 1.0
Date    = 20.04.2022
_____________________________________________________________________
Description:
Function to add Elevation in meters to all Level names
as a prefix/suffix.

There is an option to Add/Update or Remove them.
_____________________________________________________________________
How-to:

-> Run the script
-> Change Settings (Prefix/Suffix, Add/Remove)
-> Rename

_____________________________________________________________________
Last update:
- [23.04.2022] - 1.0 RELEASE
_____________________________________________________________________
Author: Erik Frits"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
#==================================================
import os
from Autodesk.Revit.DB import  Level, FilteredElementCollector, BuiltInCategory

# pyRevit
from pyrevit import forms

# Custom
from GUI.forms                  import my_WPF
from Snippets._convert          import convert_internal_to_m
from Snippets._context_manager  import ef_Transaction, try_except




#>>>>>>>>>> .NET IMPORTS
import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System")
import wpf

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
#==================================================
doc   = __revit__.ActiveUIDocument.Document
PATH_SCRIPT = os.path.dirname(__file__)

def get_text_in_brackets(text, symbol_start, symbol_end):
    """Function to get contents between 2 symbols.
    :param text:            Given Text
    :param symbol_start:
    :param symbol_end:
    :return:
    e.g.
    get_text_in_brackets('This is [not] important message', '[', ']')
    => 'not'"""
    start = text.find(symbol_start) + len(symbol_start) if symbol_start in text else None
    stop = text.find(symbol_end) if symbol_end in text else None
    return str(text[start:stop])

# ╔═╗╦  ╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝
#==================================================
class LevelElevations(my_WPF):
    """Class for GUI of LevelElevations tools."""
    def __init__(self):
        self.add_wpf_resource()
        path_xaml_file = os.path.join(PATH_SCRIPT, 'LevelElevation.xaml')
        wpf.LoadComponent(self, path_xaml_file)

        self.main_title.Text     = __title__
        self.footer_version.Text = __version__
        self.ShowDialog()

    # >>>>>>>>>> INHERIT WPF RESOURCES
    def add_wpf_resource(self):
        """Function to get resources from super()"""
        super(LevelElevations, self).add_wpf_resource()

    def elevation_to_level(self, lvl, mode, position):
        # type:(Level,str,str)
        """Function to update Levels names according to given mode and position.
        :param lvl:      Level that is being updated
        :param mode:     'add/remove'    - add will also update if value exists.
        :param position: 'prefix/suffix' - Position of elevation value.
        :return: """

        symbol_start = self.UI_symbol_start.Text
        symbol_end   = self.UI_symbol_end.Text

        if not symbol_start or not symbol_end:
            forms.alert("Please provide both Start/End Symbol to use this tool. Try Again.",title=__title__,exitscript=True)

        lvl_elevation_m = str(round(convert_internal_to_m(lvl.Elevation), 2))  # cut at 2 digits
        lvl_elevation_m = "+" + lvl_elevation_m if lvl.Elevation > 0 else lvl_elevation_m

        # ELEVATION EXISTS
        if symbol_start in lvl.Name and symbol_end in lvl.Name:
            brackets_value = get_text_in_brackets(lvl.Name, symbol_start, symbol_end)
            if mode == 'Add/Update':
                new_name = lvl.Name.replace(brackets_value, lvl_elevation_m)
            elif mode == 'Remove':
                new_name = lvl.Name.replace(symbol_start + brackets_value + symbol_end, "")

        # ELEVATION DOES NOT EXISTS
        else:
            elevation_value = symbol_start + lvl_elevation_m + symbol_end
            new_name = lvl.Name + elevation_value if position == "Suffix" else elevation_value + lvl.Name

        # UPDATE LEVEL NAME
        if lvl.Name != new_name:
            lvl_name = lvl.Name  # Current name (for reporting)
            try:
                lvl.Name = new_name  # Change Name
                print('Renamed: {} -> {}'.format(lvl_name, new_name))
            except:
                print('Could not rename - {}. \nPlease make sure there is no Level with the same intended name.'.format(lvl_name))

    # ╔═╗╦  ╦╔═╗╔╗╔╔╦╗╔═╗
    # ║╣ ╚╗╔╝║╣ ║║║ ║ ╚═╗
    # ╚═╝ ╚╝ ╚═╝╝╚╝ ╩ ╚═╝
    # ==================================================
    def UI_mode_changed(self, sender, e):
        self.mode = sender.Content.ToString()

    def UI_position_changed(self, sender, e):
        self.position = sender.Content.ToString()

    # ╦═╗╦ ╦╔╗╔
    # ╠╦╝║ ║║║║
    # ╩╚═╚═╝╝╚╝ RUN
    # ==================================================
    def UI_Run(self, sender, e):
        self.Close()



        all_levels = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
        with ef_Transaction(doc, __title__, debug=True):
            for lvl in all_levels:
                self.elevation_to_level(lvl, self.mode, self.position)
        print("-" * 50)
        print("Script is finished.")



# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
# ==================================================
if __name__ == '__main__':
    LevelElevations()