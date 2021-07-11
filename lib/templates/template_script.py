# -*- coding: utf-8 -*-
__title__ = "Template"
__author__ = "Erik Frits"
__helpurl__ = "www.erikfrits.com/blog"
# __highlight__ = 'updated'
# __context__ = ['Sheets', 'Views']

__doc__ = """Version = 1.0
Date    = 10.06.2021
_____________________________________________________________________
Description:

Here will be a description of the add-in.
_____________________________________________________________________
How-to:

Here will be a guide on how to use the tool.
_____________________________________________________________________
Prerequisite:

All requirements and things to be changed in the script should be described here.
_____________________________________________________________________
Last update:
- [13.04.2021] - v1.0 
_____________________________________________________________________
To-do:
- [BUG]     - Resolve a bug.
- [TO-DO]   - Make something
- [FEATURE] - Add a new Feature 
_____________________________________________________________________"""


# IMPORTS
from Autodesk.Revit.DB import *

# SYSTEM IMPORTS
import clr
clr.AddReference("System")
from System.Collections.Generic import List


# USER GROUP (optional)
# from Permissions import usergroup
# usergroup.dev_only()
# usergroup.admins_only()


# GLOBAL VARIABLES
uidoc   = __revit__.ActiveUIDocument
app     = __revit__.Application
doc     = __revit__.ActiveUIDocument.Document


# MAIN
if __name__ == '__main__':
    t = Transaction(doc,__title__)
    t.Start()
    # CODE HERE
    t.Commit()