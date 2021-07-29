# -*- coding: utf-8 -*-
__title__ = "Regions: Change Linestyle"   # Name of the button displayed in Revit
__author__ = "Erik Frits"
__doc__ = """Version = 1.0
Date    = 18.07.2021
_____________________________________________________________________
Description:

Apply LineStyle from the list to borders 
of the selected FilledRegions.
_____________________________________________________________________
How-to:

-> Select FilledRegions
-> Run the script
-> Select LineStyle to apply
_____________________________________________________________________
Last update:

- [18.07.2021] - 1.0 RELEASE
_____________________________________________________________________
"""

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> IMPORTS
from pyrevit import forms, revit
from Autodesk.Revit.DB import  FilledRegion

#>>>>>>>>>> CUSTOM IMPORTS
from Snippets._selection import get_selected_elements

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VARIABLES
doc   = __revit__.ActiveUIDocument.Document

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> MAIN
if __name__ == '__main__':

    #>>>>>>>>>> GET SELECTED FILLED REGIONS
    selected_filled_regions = [element for element in get_selected_elements() if type(element) == FilledRegion]
    if not selected_filled_regions:
        forms.alert('No FilledRegion selected. Please try again', title=__title__, exitscript=True)

    #>>>>>>>>>> GET VALID LINESTYLES
    region                  = selected_filled_regions[0]
    valid_line_styles_ids   = region.GetValidLineStyleIdsForFilledRegion(doc)
    valid_line_styles       = [doc.GetElement(i) for i in valid_line_styles_ids]
    dict_valid_line_styles  = {i.Name:i for i in valid_line_styles}

    #>>>>>>>>>> PROMT USER TO SELECT ONE
    selection           = forms.SelectFromList.show(dict_valid_line_styles.keys(),title="Select LineStyle", button_name='Select')
    if not selection:   forms.alert("LineStyle was not chosen. Please try again.", title=__title__, exitscript=True)
    selected_line_style = dict_valid_line_styles[selection]

    #>>>>>>>>>> APPLY SELECTED LINESTYLE
    with revit.Transaction(__title__):
        for region in selected_filled_regions:
            region.SetLineStyleId(selected_line_style.Id)
