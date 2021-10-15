from Autodesk.Revit.DB import (ViewPlan, ViewSection, View3D, ViewSchedule, View, ViewType, ViewDrafting,
                               DetailLine, DetailCurve, DetailArc, DetailEllipse, DetailNurbSpline,
                               ModelLine, ModelCurve, ModelArc, ModelEllipse, ModelNurbSpline
                               )


ALL_VIEW_TYPES = [ViewPlan, ViewSection, View3D , ViewSchedule, View, ViewDrafting]
LINE_TYPES = [DetailLine, DetailCurve, DetailArc, DetailEllipse, DetailNurbSpline,
              ModelLine, ModelCurve, ModelArc, ModelEllipse, ModelNurbSpline]