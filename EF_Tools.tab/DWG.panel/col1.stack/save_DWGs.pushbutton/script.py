# -*- coding: utf-8 -*-
__title__   = "Save DWGs"
__author__  = "Erik Frits"
__doc__ = """Version = 1.0
Date    = 31.07.2021
_____________________________________________________________________
Description:

Save all linked DWGs in the project to a specified location. 
Optionally you can choose to relink them all as well.
_____________________________________________________________________
How-to:

-> Run the script.
-> Choose directory for saving DWG.
-> optional: Relink newly saved DWG in the current model.
_____________________________________________________________________
Last update:

- [10.06.2021] - 1.2 RELEASE
_____________________________________________________________________
To-do:

- 
_____________________________________________________________________
Author: Erik Frits
"""

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> IMPORTS
import os, sys, clr, shutil
from Autodesk.Revit.DB import (FilteredElementCollector,
                               CADLinkType,
                               ModelPathUtils,
                               Transaction)
#>>>>>>>>>> .NET IMPORTS
clr.AddReference("System")
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import (DialogResult,
                                  MessageBox,
                                  MessageBoxButtons ,
                                  OpenFileDialog,
                                  FolderBrowserDialog)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VARIABLES
doc = __revit__.ActiveUIDocument.Document

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> CLASS
class SaveDWGs:
    def __init__(self):
        #>>>>>>>>>> SAVE LOCATION
        dir_backup = self.Dialog_dir_backup()
        #>>>>>>>>>> SAVE DWGs
        SavedDWGs = self.SaveLinkedDWGs(dir_backup + "\\DWGs\\")

        # >>>>>>>>>> RELINK DWGs (optional)
        if SavedDWGs:
            self.RelinkCAD(SavedDWGs)

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> FUNCTIONS
    def Dialog_dir_backup(self):
        """ Ask user to use same directory as Revit file or
            Open a DialogBox to select destination folder manually."""
        file_exist = os.path.exists(doc.PathName)
        if file_exist:
            dialogResult = MessageBox.Show(
                "Save DWGs in the same folder as current Revit file?\n\n" + "Current file: " + str(doc.PathName),
                "Save DWGs", MessageBoxButtons.YesNo)
            if (dialogResult == DialogResult.Yes):
                #>>>>>>>>>> Saving folder is the same as Revit location
                doc_path = doc.PathName
                rvt_name = doc_path.split("\\")[-1]
                temp = len(doc_path) - len(rvt_name)
                doc_dir = doc_path[:temp]
                return doc_dir

        #>>>>>>>>>> CHOOSE SAVING DIR
        fileDialog              = FolderBrowserDialog()
        fileDialog.Description  = "Select folder for saving dwg files."
        fileDialog.ShowDialog()

        #>>>>>>>>>> SELECTED PATH
        dir_backup = fileDialog.SelectedPath

        if not dir_backup:
            sys.exit("Backup destination directory was not selected!")
        return dir_backup

    def SaveLinkedDWGs(self, path):
        """Save all linked DWGs in Project to chosen folder.
           Function returns a dictionary of CAD filename and its new filepath.
           {Filename : Filepath} - Is used for relinking DWGs."""

        CADfiles_dict = {}
        if not os.path.exists(path):
            os.makedirs(path)

        DWGs = FilteredElementCollector(doc).OfClass(CADLinkType).WhereElementIsElementType()
        if DWGs:
            print("----------Saved CAD files:--------")
            for cad_Link in DWGs:
                try:
                    efr = cad_Link.GetExternalFileReference()
                    dwg_path = ModelPathUtils.ConvertModelPathToUserVisiblePath(efr.GetPath())
                    dwg_name = dwg_path.split("\\")[-1]
                    dwg_new_path = path + dwg_name
                    shutil.copyfile(dwg_path, dwg_new_path)
                    print("CAD saved:" + str(dwg_new_path))
                    CADfiles_dict[dwg_name] = dwg_new_path
                except:
                    print("***Exception occured while saving DWG***")
                    continue
            return CADfiles_dict
        else:
            print("- No CAD links found.")
            return

    def RelinkCAD(self, dict_dwg):
        """Relink all CAD files with exported ones.
           arg: dictionary of CAD files produced by SaveLinkedDWGs function.
           {filename : new_filepath}"""
        dialogResult = MessageBox.Show("Relink dwgs in currently open model?",
                                       "Relink DWGs",
                                       MessageBoxButtons.YesNo)

        if (dialogResult == DialogResult.Yes):
            DWGs = FilteredElementCollector(doc).OfClass(CADLinkType).WhereElementIsElementType()
            if not DWGs:
                print("***No DWGs***")
                return

            print("----------Relinked CAD:----------")
            for cad_Link in DWGs:
                try:
                    efr = cad_Link.GetExternalFileReference()
                    dwg_path = ModelPathUtils.ConvertModelPathToUserVisiblePath(efr.GetPath())
                    dwg_name = dwg_path.split("\\")[-1]
                    if dwg_name in dict_dwg:
                        try:
                            cad_Link.LoadFrom(dict_dwg[dwg_name])
                            print("- DWG relinked - {}".format(dwg_name))
                        except:
                            print("*** Could not relink DWG - {}".format(dwg_name))
                except:
                    print("***Exception occured while Relinking DWG***")
                    continue
        else:
            print("- CAD files were not relinked.")

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> MAIN
if __name__ == '__main__':
    t = Transaction(doc, __title__)
    t.Start()
    SaveDWGs()
    t.Commit()