# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import ElementId, OverrideGraphicSettings, Color
def override_graphics_region(doc, view, region,
                             fg_pattern_id, fg_color,
                             bg_pattern_id, bg_color,
                             line_color = None, line_pattern_id=None, lineweight= None):
    """Function to ovverride given region with the override settings.
    :param doc:             Revit Document
    :param region:          FilledRegion to apply OverrideGraphicsSettings
    :param fg_pattern_id:   Foreground - Pattern id
    :param fg_color:        Foreground - Colour
    :param bg_pattern_id:   Background - Pattern id
    :param bg_color:        Background - Colour
    :return:                None """
    try:
        override_settings = OverrideGraphicSettings()
        if fg_pattern_id != ElementId(-1):
            override_settings.SetSurfaceForegroundPatternId(fg_pattern_id)
            override_settings.SetSurfaceForegroundPatternColor(fg_color)
        else:
            override_settings.SetSurfaceForegroundPatternColor(Color(255, 255, 255))

        if bg_pattern_id != ElementId(-1):
            override_settings.SetSurfaceBackgroundPatternId(bg_pattern_id)
            override_settings.SetSurfaceBackgroundPatternColor(bg_color)
        else:
            override_settings.SetSurfaceBackgroundPatternColor(Color(255, 255, 255))

        # LINE
        if line_color:      override_settings.SetProjectionLineColor(line_color)
        if line_pattern_id: override_settings.SetProjectionLinePatternId(line_pattern_id)
        if lineweight:      override_settings.SetProjectionLineWeight(lineweight)

        view.SetElementOverrides(region.Id, override_settings)

    except:
        # DELETE REGIONS IF MODEL PATTERN IS USED ?
        doc.Delete(region.Id)




def override_graphics_line(doc, view, line,
                             line_color = None, line_pattern_id=None, lineweight= None):
    """Function to ovverride given region with the override settings.
    :param doc:             Revit Document
    :param line:            DetailCurve to apply OverrideGraphicsSettings
    :param fg_pattern_id:   Foreground - Pattern id
    :param fg_color:        Foreground - Colour
    :param bg_pattern_id:   Background - Pattern id
    :param bg_color:        Background - Colour
    :return:                None """

    try:
        override_settings = OverrideGraphicSettings()
        # LINE
        if line_color:      override_settings.SetProjectionLineColor(line_color)
        if line_pattern_id: override_settings.SetProjectionLinePatternId(line_pattern_id)
        if lineweight:      override_settings.SetProjectionLineWeight(lineweight)

        view.SetElementOverrides(line.Id, override_settings)

    except:
        import traceback
        print(traceback.format_exc())




