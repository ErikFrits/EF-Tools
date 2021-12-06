# -*- coding: utf-8 -*-
from sys import exit
app   = __revit__.Application

def check_revit_version(min_version ,exit_script = True):
    #type(int,bool) -> None
    """Verify Revit version, Stop execution if exit_script.
    :param   min_version: int
    :param   exit_script:
    :return: None"""

    if int(app.VersionNumber) < min_version:
        print("AttachedGroups tools are only available for Revit version {}+ because of RevitAPI abilities.".format(min_version))
        if exit_script: exit()
        return False
    return True