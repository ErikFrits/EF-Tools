# -*- coding: utf-8 -*-
doc = """This file will be executed everytime Revit starts."""
import os

# UPDATE EF-TOOLS
cmd_command = 'cmd /c "pyrevit extensions update EF-Tools"'
os.system(cmd_command)