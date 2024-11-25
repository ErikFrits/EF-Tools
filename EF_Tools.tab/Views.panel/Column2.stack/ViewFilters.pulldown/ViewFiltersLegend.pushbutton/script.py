# -*- coding: utf-8 -*-
__title__   = "ViewFilters: Create Legend"
__author__  = "Erik Frits"
__version__ = "Version: 1.1"
__doc__ = """Version = 1.1
Date    = 25.01.2022
_____________________________________________________________________
Description:

Generate legend for filters applied to the selected views: 

The legend contains multiple columns of information:
- Lines Cut
- Lines Surface
- FilledRegion Cut
- FilledRegion Surface
- FilterName
- FilterCategories
- RuleParameter
- RuleEvaluator
- Rule Value

Delete what you don't want to have in your legend or use these
views for overviews of your filter applied to selected view.
_____________________________________________________________________
How-to:

-> Click on the button
-> Change Settings(optional)
-> Click on Generate Legends
_____________________________________________________________________
Last update:
- [11.02.2022] - 1.1 added Revit 2022 Support.
- [31.01.2022] - 1.0 RELEASE
_____________________________________________________________________
To-Do:
- Test Legend ViewTemplate(Might cause errors)
- Open latest Legend
- Report new Legends with linkify?
_____________________________________________________________________
Author: Erik Frits"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#====================================================================================================
import  os
from pyrevit import forms
from Autodesk.Revit.DB import *

#>>>>>>>>>> CUSTOM IMPORTS
from Snippets._context_manager  import ef_Transaction, try_except
from GUI.forms                  import my_WPF, ListItem
from Snippets._annotations      import create_region, create_horizontal_line, create_text_note
from Snippets._convert          import convert_cm_to_feet
from Snippets._overrides        import override_graphics_region, override_graphics_line

#>>>>>>>>>> .NET IMPORTS
import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System")
from System.Collections.Generic import List
from System.Windows.Controls import ComboBoxItem
import wpf



# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#====================================================================================================
PATH_SCRIPT = os.path.dirname(__file__)

uidoc   = __revit__.ActiveUIDocument
app     = __revit__.Application
doc     = __revit__.ActiveUIDocument.Document

# TEXT
all_text_types      = FilteredElementCollector(doc).OfClass(TextNoteType).WhereElementIsElementType().ToElements()
dict_all_text_types = {i.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString(): i for i in all_text_types}

#VIEWS
all_views                       = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).ToElements()
all_views_with_filters          = [v for v in all_views if v.GetFilters() and not v.IsTemplate]
all_templates_with_filters      = [v for v in all_views if v.GetFilters() and v.IsTemplate]
all_with_filters                = all_views_with_filters + all_templates_with_filters
if not all_with_filters:
    forms.alert("There are no Views or ViewTemplates with Filters assigned to them! "
                "\nPlease add one and try again.", exitscript=True)



dict_all_views_and_templates    = {v.Name: v for v in all_with_filters}
dict_all_views                  = {v.Name:v for v in all_views_with_filters}
dict_all_templates              = {v.Name:v for v in all_templates_with_filters}

# GET ALL LEGEND VIEWS
all_views = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).ToElements()
all_legends = [view for view in all_views if view.ViewType == ViewType.Legend]
all_legends = [view for view in all_legends if not view.IsTemplate]

if not all_legends:
    forms.alert("There has to be at least 1 Legend View in the project! "
                "Please create one and try again.", exitscript=True)

# WORKSETS
all_worksets  = FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset).ToWorksets()
workset_names = {int(str(w.Id)): w.Name for w in all_worksets}


def create_List(dict_elements):
    """Function to create a List<ListItem> to parse it in GUI ComboBox.
    :param dict_elements:   dict of views ({name:view})
    :return:                List<ListItem>"""
    list_of_views = List[type(ListItem())]()
    for name, view in sorted(dict_elements.items()):
        list_of_views.Add(ListItem(name, view))
    return list_of_views

List_all_views_and_templates = create_List(dict_all_views_and_templates)
List_all_views               = create_List(dict_all_views)
List_all_templates           = create_List(dict_all_templates)

# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝ CLASSES
# ==================================================

class ef_Rule:
    dict_BIPs =  {str(i.value__) : i for i in BuiltInParameter.GetValues(BuiltInParameter)}

    def __init__(self, rule):
        """Function to parse FilterRule.
        :param rule: ParameterFilterElement """

        self.rule = rule
        self.get_rule_value()

    @property
    def rule_param_name(self):
        """Method to get rule Parameter"""
        # PARAM ID
        rule_param_id = self.rule.GetRuleParameter()

        # SHARED PARAMETER
        rule_shared_param = doc.GetElement(rule_param_id)
        if rule_shared_param:
            return rule_shared_param.Name

        # BUILT-IN PARAMETER
        bip_rule_param = self.dict_BIPs[str(rule_param_id)]
        readable_bip = LabelUtils.GetLabelFor(bip_rule_param)
        return readable_bip

    def get_rule_value(self):
        # VARIABLES
        #==============================
        rule_evaluator  = ''
        rule_value      = ''
        inverse         = False

        # INVERSE
        #==============================
        if type(self.rule) == FilterInverseRule:
            inverse = True
            inner_rule = self.rule.GetInnerRule()
            rule = inner_rule
        else:
            rule = self.rule


        # GET EVALUATOR
        #==============================
        try:
            rule_evaluator = rule.GetEvaluator().ToString().split('Filter')[1].replace("String","").replace("Numeric","")
            rule_evaluator = 'not {}'.format(rule_evaluator) if inverse else rule_evaluator
        except:
            if type(rule) == HasValueFilterRule:
                rule_evaluator = 'HasValue'
            elif type(rule) == HasNoValueFilterRule:
                rule_evaluator = 'HasNoValue'
            elif type(rule) == SharedParameterApplicableRule:
                rule_evaluator = 'Exists'
            else:
                print("Could not get RuleValue. Please submit screenshot with description to: https://github.com/ErikFrits/EF-Tools/issues")
                print('Rule: {}'.format(rule))
                print('type(Rule): {}'.format(type(rule)))

        # VALUES
        #==============================
        # STRING
        if type(rule) == FilterStringRule:
            rule_value = rule.RuleString

        # INTEGER
        elif type(rule) == FilterIntegerRule:
            if self.rule_param_name == 'Workset':
                rule_value = workset_names[rule.RuleValue]
            else:
                rule_value = rule.RuleValue

        # DOUBLE
        elif type(rule) == FilterDoubleRule:
            rule_value = rule.RuleValue

        # ELEMENTID
        elif type(rule) == FilterElementIdRule:
            element_id = rule.RuleValue
            element = doc.GetElement(element_id)
            try:
                rule_value = element.Name
            except:
                try:
                    rule_value = element.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()
                except:
                    rule_value = element

        # HasNoValue
        elif type(rule) == HasNoValueFilterRule:
            rule_value = '-'

        # HasValue
        elif type(rule) == HasValueFilterRule:
            rule_value = '-'

        elif type(rule) == SharedParameterApplicableRule:
            rule_value = '-'

        else:
            print("Could not get RuleValue. Please submit screenshot with description to: https://github.com/ErikFrits/EF-Tools/issues")
            print('Rule: {}'.format(rule))
            print('type(Rule): {}'.format(type(rule)))

        # RESULTS
        #==============================
        self.rule_value = rule_value
        self.rule_eval = rule_evaluator


class ef_Filter:

    def __init__(self, pfe):
        self.pfe = pfe
        self.cats           = self.get_categories()
        self.cat_names      = [cat.Name for cat in self.cats]
        self.rules          = self.get_rules()

    def get_categories(self):
        """Function to get filter's categories."""
        cats = []
        for catid in self.pfe.GetCategories():
            cat = Category.GetCategory(doc, catid)
            cats.append(cat)
        return cats

    def get_rules(self):
        filter_filters = self.pfe.GetElementFilter()
        if not filter_filters:
            # print("There are no rules for filter [{}]. Please verify.".format(self.pfe.Name))
            return []

        filter_rules = filter_filters.GetFilters()
        parsed_rules = []
        for rule_set in filter_rules:
            rules = rule_set.GetRules()
            for rule in rules:
                parsed_rule = ef_Rule(rule)
                parsed_rules.append(parsed_rule)
        return parsed_rules

# MAIN FUNCTION
class CreateFilters(my_WPF):
    views = List_all_views_and_templates
    legend_view = None #Used to open view of last generated legend.

    def __init__(self):
        # GUI
        self.add_wpf_resource()
        path_xaml_file = os.path.join(PATH_SCRIPT, 'CreateFilters.xaml')
        wpf.LoadComponent(self, path_xaml_file)
        self.combobox_add_text_types()
        self.UI_ListBox_Views.ItemsSource = self.views

        self.main_title.Text     = __title__
        self.footer_version.Text = __version__

        # REVIT
        # self.drafting_view_type = self.get_drafting_view_type()
        self.ShowDialog()


    #>>>>>>>>>> INHERIT WPF RESOURCES
    def add_wpf_resource(self):
        """Function to get resources from super()"""
        super(CreateFilters, self).add_wpf_resource()

    def combobox_add_text_types(self):
        """Function to add all TextNoteTypes to ComboBox(self.UI_text_type)."""
        for n, type in enumerate(all_text_types):
            item = ComboBoxItem()
            item.Content    = type.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()
            item.IsSelected = True if n==0 else False
            self.UI_text_type.Items.Add(item)

    # ╔═╗╦═╗╔═╗╔═╗╔╦╗╔═╗
    # ║  ╠╦╝║╣ ╠═╣ ║ ║╣
    # ╚═╝╩╚═╚═╝╩ ╩ ╩ ╚═╝ CREATE
    #==================================================

    def create_legend_view(self, name=""):
        """Function to create LegendView by duplicating one of existing ones."""
        random_legend = all_legends[0]

        # CREATE NEW LEGEND VIEW
        new_legend_view_id = random_legend.Duplicate(ViewDuplicateOption.Duplicate)
        new_legend_view = doc.GetElement(new_legend_view_id)
        new_legend_view.Scale = 100

        # RENAME
        if name:
            for i in range(50):
                try:    new_legend_view.Name = name
                except: name += "*"

        self.legend_view = new_legend_view
        return new_legend_view


    # ╔═╗╔═╗╔╦╗╔╦╗╔═╗╦═╗╔═╗
    # ║ ╦║╣  ║  ║ ║╣ ╠╦╝╚═╗
    # ╚═╝╚═╝ ╩  ╩ ╚═╝╩╚═╚═╝ GETTERS
    #==================================================

    def get_selected_text_type(self):
        """Function to get selected item from self.UI_text_type."""
        for item in self.UI_text_type.Items:
            if item.IsSelected:
                text_type = dict_all_text_types[item.Content]
                return text_type


    def get_selected_views(self):
        """Get a list of selected views from ListBox."""
        selected_views = []
        for item in self.views:
            if item.IsChecked:
                selected_views.append(item.element)
        return selected_views

    # ╔═╗╦ ╦╦  ╔═╗╦  ╦╔═╗╔╗╔╔╦╗╔═╗
    # ║ ╦║ ║║  ║╣ ╚╗╔╝║╣ ║║║ ║ ╚═╗
    # ╚═╝╚═╝╩  ╚═╝ ╚╝ ╚═╝╝╚╝ ╩ ╚═╝
    #==================================================
    def UI_event_checked_views(self, sender, e):
        """EventHandler to filter Views and ViewTemplate in the ListBox when checkboxes clicked."""
        #VIEWS + TEMPLATE
        if self.UI_checkboax_views.IsChecked and self.UI_checkboax_view_templates.IsChecked:
            self.views = List_all_views_and_templates
        #VIEWS
        elif self.UI_checkboax_views.IsChecked:
            self.views = List_all_views
        #TEMPLATES
        elif self.UI_checkboax_view_templates.IsChecked:
            self.views = List_all_templates
        #NONE
        else:
            self.views = {}

        #UPDATE LISTBOX
        self.UI_ListBox_Views.ItemsSource = self.views
        self.UI_text_filter_updated(0,0)

    def UI_text_filter_updated(self, sender, e):
        """Function to filter items in the UI_ListBox_Views."""
        filtered_list_of_items = List[type(ListItem())]()
        filter_keyword = self.textbox_filter.Text

        #RESTORE ORIGINAL LIST
        if not filter_keyword:
            self.UI_ListBox_Views.ItemsSource = self.views
            return

        # FILTER ITEMS
        for item in self.views:
            if filter_keyword.lower() in item.Name.lower():
                filtered_list_of_items.Add(item)

        # UPDATE LIST OF ITEMS
        self.UI_ListBox_Views.ItemsSource = filtered_list_of_items


    # ╦═╗╦ ╦╔╗╔
    # ╠╦╝║ ║║║║
    # ╩╚═╚═╝╝╚╝ RUN
    #==================================================

    def button_run(self, sender, e):
        self.Close()
        self.selected_text_type = self.get_selected_text_type()
        self.selected_views = self.get_selected_views()

        # LOOP THROUGH SELECTED VIEWS
        for view in self.selected_views:
            X = 0.0
            Y = 0.0

            # Create Legend
            legend_name = 'Legend_{}'.format(view.Name)
            legend_view = self.create_legend_view(legend_name)

            # Region Parameters
            region_width        = convert_cm_to_feet(float(self.UI_region_width.Text))
            region_height       = convert_cm_to_feet(float(self.UI_region_height.Text))
            region_spacing      = convert_cm_to_feet(float(self.UI_region_spacing.Text))
            line_width          = convert_cm_to_feet((float(self.UI_line_width.Text)))

            text_offset         = region_width + region_spacing

            # ╦ ╦╔═╗╔═╗╔╦╗╔═╗╦═╗╔═╗
            # ╠═╣║╣ ╠═╣ ║║║╣ ╠╦╝╚═╗
            # ╩ ╩╚═╝╩ ╩═╩╝╚═╝╩╚═╚═╝ HEADERS
            # ==================================================
            header_line_surface    = create_text_note(doc, legend_view, X               , Y+text_offset, 'Surface:'     , self.selected_text_type, bold=True)
            header_line_cut        = create_text_note(doc, legend_view, X+text_offset   , Y+text_offset, 'Cut:'         , self.selected_text_type, bold=True)
            header_region_surface  = create_text_note(doc, legend_view, X+text_offset*2 , Y+text_offset, 'Surface:'     , self.selected_text_type, bold=True)
            header_region_cut      = create_text_note(doc, legend_view, X+text_offset*3 , Y+text_offset, 'Cut:'         , self.selected_text_type, bold=True)
            header_Name            = create_text_note(doc, legend_view, X+text_offset*4 , Y+text_offset, 'FilterName:'  , self.selected_text_type, bold=True)
            header_categories      = create_text_note(doc, legend_view, X+text_offset*6 , Y+text_offset, 'FilterCategories', self.selected_text_type, bold=True)
            header_rule_param      = create_text_note(doc, legend_view, X+text_offset*8 , Y+text_offset, 'RuleParameter:'  , self.selected_text_type, bold=True)
            header_rule_eval       = create_text_note(doc, legend_view, X+text_offset*11 , Y+text_offset, 'RuleEvaluator:' , self.selected_text_type, bold=True)
            header_rule_value      = create_text_note(doc, legend_view, X+text_offset*13 , Y+text_offset, 'RuleValue:'     , self.selected_text_type, bold=True)


            # GET AND SORT FILTERS
            view_filters_ids = view.GetFilters()
            view_filters = [doc.GetElement(id) for id in view_filters_ids]
            view_filters.sort(key=lambda x: x.Name, reverse=False)

            #Loop through Filters
            try:
                for filter in view_filters:
                    X = 0.0

                    # ╦  ╦╔╗╔╔═╗╔═╗
                    # ║  ║║║║║╣ ╚═╗
                    # ╩═╝╩╝╚╝╚═╝╚═╝ LINES
                    # ==================================================
                    line_surf = create_horizontal_line(doc, legend_view, X, Y - region_height/2, line_width)
                    X += text_offset

                    line_cut  = create_horizontal_line(doc, legend_view, X, Y - region_height/2, line_width)
                    X += text_offset


                    # ╔═╗╦═╗╔═╗╔═╗╔╦╗╔═╗  ╦═╗╔═╗╔═╗╦╔═╗╔╗╔╔═╗
                    # ║  ╠╦╝║╣ ╠═╣ ║ ║╣   ╠╦╝║╣ ║ ╦║║ ║║║║╚═╗
                    # ╚═╝╩╚═╚═╝╩ ╩ ╩ ╚═╝  ╩╚═╚═╝╚═╝╩╚═╝╝╚╝╚═╝ CREATE REGIONS
                    # ==================================================


                    # GET OVERRIDE GRAPHICS
                    filter_overrides = view.GetFilterOverrides(filter.Id)

                    # SURFACE
                    region_surface  = create_region(doc, legend_view, X, Y, region_width, region_height)

                    surf_foreground_color       = filter_overrides.SurfaceForegroundPatternColor
                    surf_foreground_pattern_id  = filter_overrides.SurfaceForegroundPatternId
                    surf_background_color       = filter_overrides.SurfaceBackgroundPatternColor
                    surf_background_pattern_id  = filter_overrides.SurfaceBackgroundPatternId

                    surf_line_color             = filter_overrides.ProjectionLineColor
                    surf_line_pattern_id        = filter_overrides.ProjectionLinePatternId
                    surf_lineweight             = filter_overrides.ProjectionLineWeight

                    override_graphics_region(doc, legend_view, region_surface,
                                            fg_pattern_id    = surf_foreground_pattern_id,
                                            fg_color         = surf_foreground_color,
                                            bg_pattern_id    = surf_background_pattern_id,
                                            bg_color         = surf_background_color,
                                            line_color       = surf_line_color,
                                            line_pattern_id  = surf_line_pattern_id,
                                            lineweight       = surf_lineweight)

                    override_graphics_line(doc, legend_view, line_surf,
                                           line_color      = surf_line_color,
                                           line_pattern_id = surf_line_pattern_id,
                                           lineweight      = surf_lineweight)
                    X += text_offset

                    # CUT
                    region_cut      = create_region(doc, legend_view, X, Y, region_width, region_height)

                    cut_foreground_color        = filter_overrides.CutForegroundPatternColor
                    cut_foreground_pattern_id   = filter_overrides.CutForegroundPatternId
                    cut_background_color        = filter_overrides.CutBackgroundPatternColor
                    cut_background_pattern_id   = filter_overrides.CutBackgroundPatternId

                    cut_line_color              = filter_overrides.CutLineColor
                    cut_line_pattern_id         = filter_overrides.CutLinePatternId
                    cut_lineweight              = filter_overrides.CutLineWeight

                    override_graphics_region(doc, legend_view, region_cut,
                                             fg_pattern_id   = cut_foreground_pattern_id,
                                             fg_color        = cut_foreground_color,
                                             bg_pattern_id   = cut_background_pattern_id,
                                             bg_color        = cut_background_color,
                                             line_color      = cut_line_color,
                                             line_pattern_id = cut_line_pattern_id,
                                             lineweight      = cut_lineweight)

                    override_graphics_line(doc, legend_view, line_cut,
                                           line_color       = cut_line_color,
                                           line_pattern_id  = cut_line_pattern_id,
                                           lineweight       = cut_lineweight)
                    X += text_offset

                    # FILTER NAME
                    text_filter_name = create_text_note(doc, legend_view, X, Y, filter.Name, self.selected_text_type)
                    X += text_offset*2

                    try:
                        my_filter = ef_Filter(filter)

                        # CATEGORIES
                        categories = ', '.join(my_filter.cat_names)
                        text_category = create_text_note(doc, legend_view, X, Y, categories, self.selected_text_type)
                        X += text_offset * 2

                        # RULES
                        rules = my_filter.rules

                        if len(rules) == 1:
                            rule = rules[0]
                            rule_param_name = rule.rule_param_name
                            rule_eval       = rule.rule_eval
                            rule_value      = str(rule.rule_value)

                        elif len(rules) == 0:
                            no_rules        = '[No-Rules]'
                            rule_param_name = no_rules
                            rule_eval       = no_rules
                            rule_value      = no_rules

                        else:
                            multi_rules     = '[Multi-Rules]'
                            rule_param_name = multi_rules
                            rule_eval       = multi_rules
                            rule_value      = multi_rules


                        # WRITE RULE PARAMETER NAME
                        text_category = create_text_note(doc, legend_view, X, Y, rule_param_name, self.selected_text_type)
                        X += text_offset * 3
                        # WRITE RULE EVALUATOR
                        text_category = create_text_note(doc, legend_view, X, Y, rule_eval      , self.selected_text_type)
                        X += text_offset * 2
                        # WRITE RULE VALUE
                        text_category = create_text_note(doc, legend_view, X, Y, rule_value     , self.selected_text_type)
                        X += text_offset * 2

                    except:
                        import traceback
                        print(traceback.format_exc())

                    Y -= region_spacing + region_height

            except:
                print("Failed to parse the rule. Please submit screenshot with description to: https://github.com/ErikFrits/EF-Tools/issues")
                import traceback
                print(traceback.format_exc())

if __name__ == '__main__':
    with ef_Transaction(doc, __title__, debug=True):
        x = CreateFilters()
    if x.legend_view:
        uidoc.ActiveView = x.legend_view


# TESTING
# if __name__ == '__main__':
#     my_filter = None
#     all_pfe = FilteredElementCollector(doc).OfClass(ParameterFilterElement)
#     for pfe in all_pfe:
#         if pfe.Name == "MY FILTER":
#             my_filter = pfe
#             break
#
#     parsed_filter = ef_Filter(my_filter)

