# -*- coding: utf-8 -*-
__title__ = "User Groups"
__author__ = "Erik Frits"
__doc__ = """Version = 1.0
Date    = 09.06.2021
_____________________________________________________________________
Description:
These additional function will limit the access to certain tools.
It is useful to restrict access to the most sensetive tools from the
beginner users to avoid massive errors.
_____________________________________________________________________
How-to:
- Add names of users to Dev. and admin lists
- Import function script_for_dev_only() or script_for_admins_only() 
into your tool and place it in the beginning to prevent running the 
script any further for users not in the list.
_____________________________________________________________________
Prerequisite:
- Add user names to Dev and Admin lists
_____________________________________________________________________
Last update:
09.06.2021 - Description added
_____________________________________________________________________
To-do:
-
_____________________________________________________________________
"""

# IMPORTS
import sys, os
app = __revit__.Application

# LIST OF ADMINS
#todo external config file? so other users can create their own lists
admins = [
    "RLP_Jakob Steiner",
    "ErikFrits",
]

# LIST OF DEVELOPERS
#todo external config file? so other users can create their own lists
devs = ["ErikFrits", ]

def dev_only():
    """This will stop an execution of the script if username is not in the list of developers."""
    if app.Username not in devs:
        print("USER: {}".format(app.Username))
        print("This script can only be executed by assigned developers. \nPlease contact your developer or update the list of developers in lib/Permissions/user_group.py file.")
        sys.exit()

def admins_only():
    """This will stop an execution of the script if username is not in the list of admins."""
    if app.Username not in admins:
        print("USER: {}".format(app.Username))
        print("This script can only be executed by assigned admins. \nPlease contact your developer or update the list of developers in lib/Permissions/user_group.py file.")
        sys.exit()
