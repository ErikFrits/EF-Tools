# -*- coding: utf-8 -*-
__title__   = "Shorten Ribbon names"
__author__  = "Erik Frits"
__doc__ = """Version = 1.0
Date    = 19.11.2021
_____________________________________________________________________
Description:

This tool will Shorten names of your Ribbon Tabs to the ones
defined in translaction dictionary. 
_____________________________________________________________________
How-to:

-> Click on the button to toggle ON/OFF effect.
_____________________________________________________________________
Modify translation:

Hold <ALT> key and click on the button. The folder with the script
will open. Open \translation folder.
Open a file with any text editor to modify to your own new names.

*All except for the last entry should be separated with a comma*

You can submit me translations for other languages so I can include 
it by default.
_____________________________________________________________________
Please do not rename EF-Tools because 
it won't be able to change icon colour otherwise.
_____________________________________________________________________
Last update:
- [19.11.20211] - V1.0 RELEASE
_____________________________________________________________________
Idea by: Thomas Vogt
Author : Erik Frits
"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
import json, os, codecs
from Autodesk.Revit.ApplicationServices import LanguageType
from pyrevit.coreutils.ribbon import ICON_MEDIUM
from pyrevit.script import toggle_icon
from pyrevit import script, forms
from pyrevit.api import AdWindows

#CUSTOM IMPORTS
from Snippets._context_manager import try_except

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
app = __revit__.Application
doc = __revit__.ActiveUIDocument.Document
PATH_SCRIPT = os.path.dirname(__file__)

# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝FUNCTIONS
#==================================================
def read_toggle_config():
    """Function to read toggle_state.json config located in the script's folder.
    If file is not found it will be created with False value."""
    json_toggle_state = os.path.join(PATH_SCRIPT, 'toggle_state.json')

    # READ/CREATE file
    if os.path.exists(json_toggle_state):
        with open(json_toggle_state) as f:
            json_data = json.load(f)
            TOGGLE = json_data['toggle_state']
    else:
        TOGGLE = False
    # REVERSE VALUE
    with open(json_toggle_state, "w") as f:
        x = not TOGGLE
        new_data = {"toggle_state": x}
        json.dump(new_data, f)
    return TOGGLE

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#==================================================
if __name__ == '__main__':
    # GET TOGGLE
    TOGGLE = read_toggle_config()

    # ACTIVATE/DEACTIVATE ICON
    icon_on  = os.path.join(PATH_SCRIPT, 'on.png')
    icon_off = os.path.join(PATH_SCRIPT, 'off.png')
    toggle_icon(TOGGLE, icon_on, icon_off) #Change icon

    #CHECK LANGUAGE and GET TRANSLATIONS
    lang = str(app.Language)
    path_translation = None
    if   "English" in lang :  path_translation = os.path.join(PATH_SCRIPT,'translation/ENG.json')
    elif "German"  in lang :  path_translation = os.path.join(PATH_SCRIPT,'translation/DEU.json')
    else:
        print("{} - Unfortunately your language is not supported. "
              "You can submit your short names to me "
              "and it will be added to the list.".format(lang))

    # READ TRANSLATION DICTIONARY
    with codecs.open(path_translation, 'r', 'utf-8') as f:
        translation = json.load(f)

    # REVERSE TRANSLATION IF NOT TOGGLE
    if not TOGGLE:
        translation = {v:k for k,v in translation.items()}

    # CHANGE NAMES
    for tab in AdWindows.ComponentManager.Ribbon.Tabs:
        with try_except():
            new_name = translation[tab.Title]
            if new_name != tab.Title:
                tab.Title = new_name
