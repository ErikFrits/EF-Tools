# -*- coding: utf-8 -*-

import clr
import System
from Autodesk.Revit.DB import *
doc = __revit__.ActiveUIDocument.Document
import os
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import (DialogResult, MessageBox,MessageBoxButtons, MessageBoxIcon,OpenFileDialog,FolderBrowserDialog)
import shutil #Copy file
import sys

def Dialog_dir_backup():
    """Open Dialogbox to select destination folder."""
    dialogResult = MessageBox.Show("Save DWGs in the same folder as current Revit file?\n\n" +  "Current file: " + str(doc.PathName) , "Save DWGs",MessageBoxButtons.YesNo)

    if (dialogResult == DialogResult.Yes):
        # Saving folder is the same as Revit location
        doc_path = doc.PathName
        rvt_name = doc_path.split("\\")[-1]
        temp = len(doc_path) - len(rvt_name)
        doc_dir = doc_path[:temp]
        return doc_dir

    else :
        #Choose saving folder
        fileDialog = FolderBrowserDialog()
        fileDialog.Description  = "Select folder for saving dwg files."
        fileDialog.ShowDialog()
        dir_backup = fileDialog.SelectedPath
        if dir_backup:
            return dir_backup
        else:
            sys.exit("Backup destination directory was not selected!")


def SaveLinkedDWGs(path):
    """
    Save all linked DWGs in Project to chosen folder.
    Function returns a dictionary of CAD filename and its new filepath.
    {Filename : Filepath} - Is used for relinking DWGs."""
    CADfiles_dict = {}
    if not os.path.exists(path):
        os.makedirs(path)
    DWGs = FilteredElementCollector(doc).OfClass(CADLinkType).WhereElementIsElementType()
    if DWGs:
        print("Saved CAD files:")
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
                # TODO PRINT IF LINK HAD AN ISSUE. MGC WAS GIVING AN ERROR WHEN USING THIS WITHOUT TRY, EXCEPT
                print("Exception occured in saving DWG.")
                continue
        print("Linked CAD files are saved.\n----------------------------------------------\n")
        return CADfiles_dict
    else:
        print("No CAD links.")
        return None

def RelinkCAD(dict_dwg):
    """
    Relink all CAD files with exported ones.
    arg: dictionary of CAD files produced by SaveLinkedDWGs function.
    {filename : new_filepath}"""
    dialogResult = MessageBox.Show("Relink dwgs in currently open model?", "Relink DWGs",MessageBoxButtons.YesNo)
    if (dialogResult == DialogResult.Yes):
        DWGs = FilteredElementCollector(doc).OfClass(CADLinkType).WhereElementIsElementType()
        if DWGs:
            print("Relinked CAD:")
            for cad_Link in DWGs:
                try:

                    efr = cad_Link.GetExternalFileReference()
                    dwg_path = ModelPathUtils.ConvertModelPathToUserVisiblePath(efr.GetPath())
                    dwg_name = dwg_path.split("\\")[-1]
                    if dwg_name in dict_dwg:
                        try:
                            t = Transaction(doc,"Relinking")
                            t.Start()
                            cad_Link.LoadFrom(dict_dwg[dwg_name])
                            t.Commit()
                            print(dwg_name + "   - Was relinked.")
                        except:
                            print("didnt work")
                except:
                    # TODO PRINT IF LINK HAD AN ISSUE. MGC WAS GIVING AN ERROR WHEN USING THIS WITHOUT TRY, EXCEPT
                    print("Exception occured in Relinking DWG.")
                    continue
            print("----------------------------------------------\n")
        else:
            print("No DWGs")
    else:
        print("CAD files were not relinked in current model.")

