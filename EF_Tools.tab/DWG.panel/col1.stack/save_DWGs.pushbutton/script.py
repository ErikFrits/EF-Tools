# -*- coding: utf-8 -*-
__title__   = "DWG: Save/Relink"
__author__  = "Erik Frits"
__doc__ = """Version = 1.1
Date    = 31.07.2021
_____________________________________________________________________
Description:

Save all linked CAD files in the project to a specified location. 
Optionally you can choose to relink them all as well.

It will click yes on DialogBoxes during relinking for
msg: 'Import detected no valid elements in the file's Paper space...'
_____________________________________________________________________
How-to:

-> Run the script.
-> Choose directory for saving CAD files.
-> optional: Relink newly saved DWG in the current model.
_____________________________________________________________________
Last update:

- [22.09.2021] - V1.1 RELEASE
- [22.09.2021] - EventHandler added for TaskDialogBox
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
from pyrevit.forms import alert
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
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> CLASS
class SaveDWGs:
    def __init__(self):
        #>>>>>>>>>> SAVE LOCATION
        dir_backup = self.Dialog_dir_backup()
        SavedDWGs = None
        #>>>>>>>>>> SAVE DWGs
        if dir_backup:
            SavedDWGs = self.SaveLinkedDWGs(dir_backup + "\\DWGs\\")
        # >>>>>>>>>> RELINK DWGs (optional)
        if SavedDWGs:
            self.RelinkCAD(SavedDWGs)

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> FUNCTIONS
    def Dialog_dir_backup(self):
        """ Ask user to use same directory as Revit file or
            Open a DialogBox to select destination folder manually."""
        try:
            #>>>>>>>>>> Check if Revit file exists.
            file_exist = os.path.exists(doc.PathName)
            if file_exist:
                dialogResult = MessageBox.Show(
                    "Would you like to save CAD files in the same folder as current Revit file?\n\n" + "Current file's path: " + str(doc.PathName),
                    __title__,
                    MessageBoxButtons.YesNo)
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
                alert("Backup path was not selected!\n Please try again.",title=__title__, exitscript = True)
            return dir_backup

        except:
            return None

    def SaveLinkedDWGs(self, path):
        """Save all linked DWGs in the Project to a chosen folder.
           Function returns a dictionary of CAD filename and their new filepath.
           {Filename : Filepath} - Is will be used further for relinking DWGs."""

        CADfiles_dict = {}
        if not os.path.exists(path):
            os.makedirs(path)

        DWGs = FilteredElementCollector(doc).OfClass(CADLinkType).WhereElementIsElementType()
        if DWGs:
            print("----------Saved CAD files:--------")
            for cad_Link in DWGs:
                try:
                    efr = cad_Link.GetExternalFileReference()
                    dwg_path = ModelPathUtils.ConvertModelPathToUserVisiblePath(efr.GetAbsolutePath())
                    dwg_name = dwg_path.split("\\")[-1]
                    dwg_new_path = os.path.join(path, dwg_name).replace('\\\\', '\\')
                    if dwg_path == dwg_new_path:
                        print('New path is the same as old one. ({})'.format(str(dwg_new_path)))
                    else:
                        shutil.copyfile(dwg_path, dwg_new_path)
                        print("- CAD file saved:" + str(dwg_new_path))
                        CADfiles_dict[dwg_name] = dwg_new_path
                except:
                    print("***Exception occured while saving DWG***")
                    import traceback
                    print(traceback.format_exc())
                    continue
            return CADfiles_dict
        else:
            print("- No CAD links found.")
            return

    def RelinkCAD(self, dict_dwg):
        """Relink all CAD files with newly exported ones.
           arg: dictionary of CAD files produced by SaveLinkedDWGs function.
           {filename : new_filepath}"""
        dialogResult = MessageBox.Show("Would you like to Relink saved CAD files in the currently open model?",
                                       "Relink CAD files?",
                                       MessageBoxButtons.YesNo)

        if (dialogResult == DialogResult.Yes):
            DWGs = FilteredElementCollector(doc).OfClass(CADLinkType).WhereElementIsElementType()
            if not DWGs:
                print("***No linked CAD files were found***")
                return

            print("---------------------------------------")
            print("----------Relinked CAD files:----------")
            for cad_Link in DWGs:
                try:
                    efr = cad_Link.GetExternalFileReference()
                    dwg_path = ModelPathUtils.ConvertModelPathToUserVisiblePath(efr.GetPath())
                    dwg_name = dwg_path.split("\\")[-1]
                    if dwg_name in dict_dwg:
                        try:
                            cad_Link.LoadFrom(dict_dwg[dwg_name])
                            print("- CAD file relinked - {}".format(dwg_name))
                        except:
                            print("*** Could not relink CAD file - {}***".format(dwg_name))
                except:
                    print("***Exception occured while Relinking DWG***")
                    continue
        else:
            print("*** CAD files were not relinked.***")

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> EVENT HANDLER
from System import EventHandler, Uri
from Autodesk.Revit.UI.Events import DialogBoxShowingEventArgs
from Autodesk.Revit.UI import TaskDialogResult

def event_handler_accept_msgBox(sender, args):
    """This function is subscribed to DialogBoxShowing Event and
    it is used to suppress TaskDialogBox when CAD files are being reloaded."""
    if  "Import detected no valid elements in the file's Paper space." in args.Message:
        args.OverrideResult(6) # Yes = 6
    elif  "has extents greater than 1E9. Data exceeding that range will be truncated." in args.Message:
        args.OverrideResult(1) # OK = 1
    elif  "Some numerical data within the imported file was out of range." in args.Message:
        args.OverrideResult(8) # Close = 8
    elif  "Some entities were lost during import." in args.Message:
        args.OverrideResult(8) # Close = 8
    else:
        print('         - MessageBox not handled. msg: ' + args.Message)
        return None
    print('         - MessageBox handled. msg: ' + args.Message)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> MAIN
if __name__ == '__main__':
    __revit__.DialogBoxShowing += EventHandler[DialogBoxShowingEventArgs](event_handler_accept_msgBox) #>>> Subscribe to Event[DialogBoxShowingEventArgs]
    t = Transaction(doc, __title__)
    t.Start()
    SaveDWGs()
    t.Commit()
    __revit__.DialogBoxShowing -= EventHandler[DialogBoxShowingEventArgs](event_handler_accept_msgBox) #>>>Unubscribe to Event[DialogBoxShowingEventArgs]

