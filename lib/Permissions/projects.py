# -*- coding: utf-8 -*-
__title__ = "Projects"
__author__ = "Erik Frits"
__doc__ = """Version = 1.0
Date    = 09.06.2021
_____________________________________________________________________
Description:
These additional function will limit the access to certain tools.
It is useful to restrict access to the custom tools that are 
made for specific projects.
_____________________________________________________________________
How-to:
- Add names of projects to Projects lists
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
uidoc   = __revit__.ActiveUIDocument
app     = __revit__.Application
doc     = __revit__.ActiveUIDocument.Document


def check_project_name(project_name_keyword):
    if project_name_keyword not in doc.Title :
        print("This script is intended only for a project with '{}' in its name".format(project_name_keyword))
        sys.exit()


