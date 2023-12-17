# -*- coding: utf-8 -*-
__title__   = "FilledRegion to Floors"
__version__ = 'Version = 1.0'
__doc__     = """Version = 1.0
Date    = 17.12.2023
_____________________________________________________________________
Description:
Convert selected FilledRegions to Floors.
_____________________________________________________________________
How-to:

-> Click on the button
-> Select Filled Regions to convert to Floors
-> Select Level
-> Select FloorType
-> New Floors will be selected
_____________________________________________________________________
Last update:
- [17.12.2023] - 1.0 RELEASE
_____________________________________________________________________
Author: Erik Frits"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
from Autodesk.Revit.DB           import *
from Autodesk.Revit.UI.Selection import *
from pyrevit                     import forms

# Custom
from Snippets._selection         import select_from_dict
from Snippets._context_manager   import try_except

# .NET Imports
import clr
clr.AddReference("System")
from System.Collections.Generic import List

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
uidoc     = __revit__.ActiveUIDocument
doc       = __revit__.ActiveUIDocument.Document #type: Document
app       = __revit__.Application
rvt_year  = int(app.VersionNumber)
selection = uidoc.Selection #type: Selection


# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝
def create_floor_from_region(region):
    """Function to create Floors form Regions.
    Works for different methods before and after RVT 22"""
    new_floor = None

    # Get Region Boundaries
    region_boundaries = region.GetBoundaries()

    # ✅ Create Floors in Revit 22+
    if rvt_year >= 2022:
        with Transaction(doc, 'Create Floors (RVT 22+)') as t:
            t.Start()

            new_floor = Floor.Create(doc, region_boundaries, floor_type.Id, level.Id)
            if new_floor:
                # SET OFFSET
                param = new_floor.get_Parameter(BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM)
                param.Set(offset)

            # Ignore any Warnings!
            failOpt = t.GetFailureHandlingOptions()
            failOpt.SetFailuresPreprocessor(FloorsCreationWarningSwallower())
            t.SetFailureHandlingOptions(failOpt)

            t.Commit()

    #✅ Create Floors before Revit 22-
    if rvt_year < 2022:
        with Transaction(doc, 'Create Floors (RVT 22+)') as t:
            t.Start()

            # Ignore Warnings
            failOpt     = t.GetFailureHandlingOptions()
            failOpt.SetFailuresPreprocessor(FloorsCreationWarningSwallower())
            t.SetFailureHandlingOptions(failOpt)

            # Get Floor and Opening Shapes
            floor_shape = region_boundaries[0]
            openings    = list(region_boundaries)[1:] if len(region_boundaries) > 1 else []

            # Convert Boundary to CurveArray
            curve_array = CurveArray()
            for seg in floor_shape:
                curve_array.Append(seg)

            # Create Floor
            new_floor = doc.Create.NewFloor(curve_array, floor_type, level, False)

            # SET OFFSET
            if new_floor:
                param = new_floor.get_Parameter(BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM)
                param.Set(offset)

            t.Commit()


        # Create Openings separately (Before RVT 2022!)
        if openings:
            with Transaction(doc, 'Create FloorOpening') as t2:
                t2.Start()
                for opening in openings:
                    with try_except():

                        # Convert Boundary to Curve Array
                        opening_curve = CurveArray()
                        for seg in opening:
                            opening_curve.Append(seg)

                        # Add Openings
                        floor_opening = doc.Create.NewOpening(new_floor, opening_curve, True)
                t2.Commit()
    return new_floor
# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝
#==================================================
class ISelectionFilter_Regions(ISelectionFilter):
    def AllowElement(self, element):
        if type(element) == FilledRegion:
            return True

class FloorsCreationWarningSwallower(IFailuresPreprocessor):
    def PreprocessFailures(self, failuresAccessor):
        failList = failuresAccessor.GetFailureMessages()
        for failure in failList: #type: FailureMessage
            failuresAccessor.DeleteWarning(failure)
        return FailureProcessingResult.Continue

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#==================================================
#1️⃣ Get FilledRegions
with forms.WarningBar(title='Pick Filled Region:'):
    try:
        ref_picked = selection.PickObjects(ObjectType.Element, ISelectionFilter_Regions())
        regions     = [doc.GetElement(ref) for ref in ref_picked]

        if not regions:
            forms.alert("Multie-Boundary FileldRegion wasn't selected. Please Try Again.",exitscript=True)
    except:
        pass


#🎯 Modify Shape
# UI: Select Level
all_levels  = FilteredElementCollector(doc).OfClass(Level).ToElements()
dict_levels = {l.Name:l for l in all_levels}
level = select_from_dict(dict_levels, title=__title__,label='Select Level', version=__version__, SelectMultiple=False)
level = level[0] # select_from_dict returns list!

# Offset
offset = 0

# UI: Select Floor Type
all_floor_types = FilteredElementCollector(doc).OfClass(FloorType).ToElements()
dict_floor_types = {Element.Name.GetValue(ft):ft for ft in all_floor_types}
floor_type = select_from_dict(dict_floor_types, title=__title__,label='Select FloorType', version=__version__, SelectMultiple=False)
floor_type = floor_type[0] # select_from_dict returns list!



# Create Floors from Regions
with TransactionGroup(doc, __title__) as tg:
    tg.Start()

    new_floors = []
    for region in regions:
        floor = create_floor_from_region(region)
        new_floors.append(floor)
    tg.Assimilate()




#4️ Select New Ceilings
try:
    uidoc.Selection.SetElementIds(List[ElementId]([c.Id for c in new_floors if c.IsValidObject]))
except:
    pass