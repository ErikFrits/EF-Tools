# -*- coding: utf-8 -*-
__title__ = "EF Sheet Generator"
__helpurl__ = "https://www.youtube.com/watch?v=SxcxeErbLgc"
__doc__ = """Version = 1.0
Date: 24.11.2024
Author: Erik Frits
_____________________________________________________________________
Description:
Use EF-Sheet Generator to create New Sheets with views in no time.
_____________________________________________________________________
How-to:

SheetGenerator Form:
-> Drag Views from List to any SheetCard
-> You Can Drag Views between SheetCards as well.
-> Click on + Symbol to create a new SheetCard
-> Right-Click to remove views from SheetCards
-> Right-Click Views in list to duplicate them

Report Form:
-> Click on Cards in Report to open Sheets/Views 
_____________________________________________________________________
Ready to become pyRevit Hacker yourself? 
Check LearnRevitAPI.com"""


#👋 Hey pyRevit Hacker,
# That's not the simplest script, but it's really powerful tool.
# So, buckle up if you are trying to reverse engineer it and adjust to your own needs.
# I'm proud of you for taking this step!
# ⌨️ Happy Coding!



# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
#==================================================
from Autodesk.Revit.DB import *
from pyrevit import forms
import wpf, os, clr

# WPF Imports
clr.AddReference("System")
from System.Windows import Window, DragDropEffects, DataObject, DragDrop, Visibility, HorizontalAlignment, VerticalAlignment, CornerRadius, Thickness
from System.Windows.Window import DragMove
from System.Windows.Controls import Orientation, CheckBox, DockPanel, Button,ComboBoxItem, TextBox, ListBoxItem, StackPanel, TextBlock, WrapPanel, Border, ScrollViewer
from System.Windows.Input import MouseButtonState, Cursors
from System.Windows.Media import VisualTreeHelper, SolidColorBrush, Colors, SolidColorBrush, ColorConverter, Brushes
from System.Diagnostics.Process import Start
from System import Uri

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
#==================================================
PATH_SCRIPT = os.path.dirname(__file__)
uidoc       = __revit__.ActiveUIDocument
app         = __revit__.Application
doc         = __revit__.ActiveUIDocument.Document
exit = False


# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝
#==================================================

def exitscript():
    output.print_md('**Error has occurred**')
    output.print_md(
        '**Please share the error message with me on [GitHub/EF-Tools:Issues](https://github.com/ErikFrits/EF-Tools/issues)**')
    print('\n Error Message:')
    import traceback, sys
    print(traceback.format_exc())
    sys.exit()

def rename_sheet(sheet, sheet_name, sheet_number):
    """Renames a ViewSheet with the specified SheetName and SheetNumber avoiding duplicates."""
    # Clear forbidden symbols
    forbidden_symbols = "\:{}[]|;<>?`~"
    sheet_name   = ''.join(c for c in sheet_name if c not in forbidden_symbols)
    sheet_number = ''.join(c for c in sheet_number if c not in forbidden_symbols)

    # Change SheetName
    sheet.Name = sheet_name

    # Change SheetNumber
    for i in range(1, 50):
        try:
            sheet.SheetNumber = sheet_number
            break
        except:
            sheet_number += '*'

# ╦ ╦╔═╗╦  ╔═╗╔═╗╦═╗  ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ╠═╣║╣ ║  ╠═╝║╣ ╠╦╝  ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╩ ╩╚═╝╩═╝╩  ╚═╝╩╚═  ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝
#==================================================

class BorderSheetCardReader:
    sheet_number = ''
    sheet_name   = ''

    def __init__(self, border_element):
        self.views = []

        # Ensure Border
        self.border       = border_element
        if not isinstance(self.border, Border):
            raise TypeError("Input must be a Border element.")

        # Parse data
        self._parse_border()

    def _parse_border(self):
        """Parse the Border element to extract its content."""

        # Get Main StackPanel
        main_stack = self.border.Child

        # Get Containers
        dock_panel         = main_stack.Children[0]
        border             = main_stack.Children[1]
        nested_stack_panel = border.Child

        # Get Text Values
        self.sheet_number = dock_panel.Children[0].Text
        self.sheet_name   = dock_panel.Children[1].Text

        # Get View
        for text_block in nested_stack_panel.Children:
            view = text_block.Tag
            self.views.append(view)

# ╔╦╗╔═╗╦╔╗╔  ╔═╗╔═╗╦═╗╔╦╗
# ║║║╠═╣║║║║  ╠╣ ║ ║╠╦╝║║║
# ╩ ╩╩ ╩╩╝╚╝  ╚  ╚═╝╩╚═╩ ╩
#==================================================

class EF_SheetGenerator(Window):
    def __init__(self):
        # 🎨 Load XAML
        path_xaml_file = os.path.join(PATH_SCRIPT, 'PlaceViewsUI.xaml')
        wpf.LoadComponent(self, path_xaml_file)
        self.load_logo()

        #⬇️ Populate the ListBox with views
        self.populate_views_listbox()
        self.populate_title_blocks_combo()

        #👀 Show Form
        self.ShowDialog()

    # ╦ ╦╔═╗╦  ╔═╗╔═╗╦═╗  ╔╦╗╔═╗╔╦╗╦ ╦╔═╗╔╦╗╔═╗
    # ╠═╣║╣ ║  ╠═╝║╣ ╠╦╝  ║║║║╣  ║ ╠═╣║ ║ ║║╚═╗
    # ╩ ╩╚═╝╩═╝╩  ╚═╝╩╚═  ╩ ╩╚═╝ ╩ ╩ ╩╚═╝═╩╝╚═╝
    # ==================================================

    def load_logo(self):
        logo_path = os.path.join(PATH_SCRIPT, 'ef_logo.png')

        from System.Windows.Media.Imaging import BitmapImage
        self.UI_ef_logo.Source = BitmapImage(Uri(logo_path))

    def create_border(self):
        """Create a new Border element with Behind-Code.
        <Border Tag="border_card" CornerRadius="10"  Background="#444444" Margin="0,0,10,10">
            <StackPanel>

                <DockPanel Margin="5">

                    <TextBox Text="SheetNumber"  Width="135" Margin="0,0,5,0"/>
                    <TextBox Text="SheetName"    Width="135"/>
                </DockPanel>

                <Border CornerRadius="10" Background="#555555"  Margin="10" >
                    <StackPanel Height="185" Margin="10" Background="#555555"
                                 AllowDrop="True" Drop="UIe_stackPanel_Drop"
                                 PreviewMouseLeftButtonDown="UIe_stackPanel_PreviewMouseLeftButtonDown"/>
                </Border>

            </StackPanel>
        </Border >
        """

        # Create the outer Border
        border              = Border()
        border.Tag          = "border_card"
        border.CornerRadius = CornerRadius(10)
        border.Background   = SolidColorBrush(ColorConverter.ConvertFromString("#444444"))
        border.Margin       = Thickness(0, 0, 10, 10)

        # Create the main StackPanel
        stack_panel_main = StackPanel()

        # Create the DockPanel
        dock_panel        = DockPanel()
        dock_panel.Margin = Thickness(5)

        # Create TextBoxes inside DockPanel
        text_box_1        = TextBox()
        text_box_1.Text   = "SheetNumber"
        text_box_1.Width  = 135
        text_box_1.Margin = Thickness(0, 0, 5, 0)

        text_box_2        = TextBox()
        text_box_2.Text   = "SheetName"
        text_box_2.Width  = 135

        # Add TextBoxes to DockPanel
        dock_panel.Children.Add(text_box_1)
        dock_panel.Children.Add(text_box_2)

        # Add DockPanel to the main StackPanel
        stack_panel_main.Children.Add(dock_panel)

        # Create the inner Border
        inner_border              = Border()
        inner_border.CornerRadius = CornerRadius(10)
        inner_border.Background   = SolidColorBrush(ColorConverter.ConvertFromString("#2b2b2b"))
        inner_border.Margin       = Thickness(10)

        # Create the nested StackPanel
        stack_panel_nested            = StackPanel()
        stack_panel_nested.Height     = 185
        stack_panel_nested.Margin     = Thickness(10)
        stack_panel_nested.Background = SolidColorBrush(ColorConverter.ConvertFromString("#2b2b2b"))
        stack_panel_nested.AllowDrop  = True

        # Attach EventHandlers
        stack_panel_nested.Drop                       += self.UIe_stackPanel_Drop
        stack_panel_nested.PreviewMouseLeftButtonDown += self.UIe_stackPanel_PreviewMouseLeftButtonDown

        # Nest Elements inside (Border -> Inned Border -> StackPanel)
        inner_border.Child = stack_panel_nested
        stack_panel_main.Children.Add(inner_border)
        border.Child = stack_panel_main

        return border

    def duplicate_view(self, listBoxItem, view, duplicate_option):
        """Duplicate a selected view inside SheetGenerator Form."""

        t = Transaction(doc, "Duplicate View")
        t.Start()

        try:
            # Duplicate View
            new_view_id = view.Duplicate(duplicate_option)
            new_view    = doc.GetElement(new_view_id)

            # Create a new ListBoxItem for the duplicated view
            view_name = '[{}] {}'.format(new_view.ViewType, new_view.Name)
            new_item = ListBoxItem(Content=view_name, Tag=new_view)

            # Insert Duplicated View after original
            index = self.UI_viewsListBox.Items.IndexOf(listBoxItem)
            self.UI_viewsListBox.Items.Insert(index + 1, new_item)

            # Refresh the search filter
            self.UIe_search_changed(None, None)

        except Exception as ex:
            print("Error duplicating view: {}".format(ex))

        finally:
            t.Commit()

    def FindAncestor(self, ancestorType, element):
        """Helper method to find ancestor of a specific type."""
        while element is not None and not isinstance(element, ancestorType):
            element = VisualTreeHelper.GetParent(element)
        return element

    def populate_views_listbox(self):
        """Populate the ListBox with all views in the project."""
        # Get Views
        views = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).WhereElementIsNotElementType().ToElements()
        views = [view for view in views if not view.IsTemplate] # Remove Templates
        views = [view for view in views if not view.get_Parameter(BuiltInParameter.VIEWPORT_SHEET_NUMBER).AsString()] #Unplaced

        # Create Dict Views {ViewType_ViewName : View}}
        dict_views = { '[{}] {}'.format(view.ViewType, view.Name):view for view in views}

        for view_name, view in sorted(dict_views.items()):
            # Add views to ListBox
            item = ListBoxItem(Content=view_name, Tag=view)
            self.UI_viewsListBox.Items.Add(item)

    def populate_title_blocks_combo(self):
        # Clear ComboBox
        self.UI_combo_title_blocks.Items.Clear()

        #⬇ Add Title Blocks to ComboBox
        tb_types = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_TitleBlocks).WhereElementIsElementType().ToElements()
        for tb_type in tb_types:
            # Create TB Name
            key = '[{}] {}'.format(tb_type.FamilyName, Element.Name.GetValue(tb_type))

            # Create TextBlock
            text_block      = TextBlock()
            text_block.Text = key

            # Create ComboBoxItem
            combo_item         = ComboBoxItem()
            combo_item.Content = text_block
            combo_item.Tag     = tb_type

            # Add ComboBoxItem to ComboBox
            self.UI_combo_title_blocks.Items.Add(combo_item)

        combo_item.IsSelected = True

    # ╔═╗╦═╗╔═╗╔═╗╔═╗╦═╗╔╦╗╦╔═╗╔═╗
    # ╠═╝╠╦╝║ ║╠═╝║╣ ╠╦╝ ║ ║║╣ ╚═╗
    # ╩  ╩╚═╚═╝╩  ╚═╝╩╚═ ╩ ╩╚═╝╚═╝
    # ==================================================

    @property
    def BorderSheetCards(self):
        """Retrieve all Border elements representing sheet cards from the grid."""
        sheet_cards = []
        for child in self.UI_sheet_grid.Children:
            if isinstance(child, Border) and child.Tag == "border_card":
                sheet_cards.append(child)
        return sheet_cards

    @property
    def selected_title_block_type(self):
        combo_item = self.UI_combo_title_blocks.SelectedItem
        tb_type    = combo_item.Tag
        return tb_type

    @property
    def used_views(self):
        all_used_views = []

        for border_card in self.BorderSheetCards:
            card_reader = BorderSheetCardReader(border_card)
            views       = card_reader.views
            views       = [v for v in views if v.ViewType != ViewType.Legend ]
            all_used_views += views

        return all_used_views


    # ╔═╗╦  ╦╔═╗╔╗╔╔╦╗╔═╗
    # ║╣ ╚╗╔╝║╣ ║║║ ║ ╚═╗
    # ╚═╝ ╚╝ ╚═╝╝╚╝ ╩ ╚═╝
    # ==================================================

    def UIe_header_btn_close(self, sender, e):
        """Stop application by clicking on a <Close> button in the top right corner."""
        self.Close()
        import sys
        sys.exit()


    def UIe_header_drag(self, sender, e):
        """Drag window by holding LeftButton on the header."""
        if e.LeftButton == MouseButtonState.Pressed:
            DragMove(self)

    def UIe_RequestNavigate(self, sender, e):
        """Forwarding for a Hyperlinks."""
        Start(e.Uri.AbsoluteUri)

    def UIe_add_sheet_card(self, sender, e):
        """Add a new SheetCard inside the Grid when clicked on + sign."""
        # Create New Card
        new_card = self.create_border()

        # Add New SheetCard to Grid
        grid         = self.UI_sheet_grid
        insert_index = max(0, grid.Children.Count - 1)  # Insert one before the last
        grid.Children.Insert(insert_index, new_card)

    def UIe_search_changed(self, sender, e):
        """Filter items in the viewsListBox based on search input.
        Use Visibility to Hide and Show items instead of recreating the list."""
        used_view_ids = [v.Id for v in self.used_views]
        search_input  = self.UI_search.Text.strip().lower()
        search_words  = search_input.split() if search_input else []

        # Control Views Visibility
        for item in self.UI_viewsListBox.Items:
            view_name = item.Content.lower()
            view      = item.Tag
            view_id   = view.Id

            # Only display items that are not in used_view_ids and match search criteria
            if view_id not in used_view_ids:
                if all(word in view_name for word in search_words) or not search_words:
                    item.Visibility = Visibility.Visible
                else:
                    item.Visibility = Visibility.Collapsed
            else:
                item.Visibility = Visibility.Collapsed

    def UIe_viewsListBox_PreviewMouseLeftButtonDown(self, sender, e):
        """Initiate drag-and-drop from the ListBox."""
        listBoxItem = self.FindAncestor(ListBoxItem, e.OriginalSource)
        if listBoxItem is not None:
            dataObject = DataObject(listBoxItem)
            DragDrop.DoDragDrop(listBoxItem, dataObject, DragDropEffects.Move)

    def UIe_stackPanel_PreviewMouseLeftButtonDown(self, sender, e):
        """Initiate drag-and-drop from a StackPanel."""
        textBlock = self.FindAncestor(TextBlock, e.OriginalSource)
        if textBlock is not None:
            dataObject = DataObject(textBlock)
            DragDrop.DoDragDrop(textBlock, dataObject, DragDropEffects.Move)

    def UIe_viewsListBox_Drop(self, sender, e):
        """Handle drop event on the ListBox."""
        if e.Data.GetDataPresent(TextBlock):
            # Get the dropped TextBlock
            text_block = e.Data.GetData(TextBlock)

            # Find the parent StackPanel
            stack_panel = self.FindAncestor(StackPanel, text_block)
            if stack_panel:
                # Remove the TextBlock from the StackPanel
                stack_panel.Children.Remove(text_block)

            # Restore visibility of the corresponding ListBoxItem
            for item in self.UI_viewsListBox.Items:
                if item.Tag == text_block.Tag:
                    item.Visibility = Visibility.Visible
                    break

    def UIe_stackPanel_Drop(self, sender, e):
        """Handle drop event on the StackPanels."""

        # 🅰️ ListBox -> StackPanel
        if e.Data.GetDataPresent(ListBoxItem):
            # Get the dropped ListBoxItem
            listBoxItem = e.Data.GetData(ListBoxItem)

            # Ensure the legend is not already in the StackPanel
            stackPanel = sender
            if '[Legend]' in listBoxItem.Content:
                # Check if the same legend already exists in the StackPanel
                existing_items = [child.Text for child in stackPanel.Children if isinstance(child, TextBlock)]
                if listBoxItem.Content in existing_items:
                    # Legend already exists; do nothing
                    return

            # Update visibility of the ListBoxItem (hide it if not a legend)
            if '[Legend]' not in listBoxItem.Content:
                listBoxItem.Visibility = Visibility.Collapsed

            # Create a new TextBlock for display in the StackPanel
            text_block      = TextBlock()
            text_block.Text = listBoxItem.Content
            text_block.Tag  = listBoxItem.Tag
            text_block.Margin  = Thickness(0,0,0,5)
            text_block.Cursor = Cursors.Hand


            # Attach event handler to the TextBlock
            text_block.MouseLeftButtonDown += self.UIe_stackPanel_PreviewMouseLeftButtonDown
            text_block.MouseRightButtonDown += self.UIe_remove_item_on_right_click

            stackPanel.Children.Add(text_block)

        # 🅱️ TextBlock -> StackPanel (Moving between StackPanels)
        elif e.Data.GetDataPresent(TextBlock):
            # Get the dropped TextBlock
            textBlock = e.Data.GetData(TextBlock)

            # Get the source StackPanel (parent of the TextBlock)
            sourceStackPanel = self.FindAncestor(StackPanel, textBlock)

            # Get the target StackPanel (sender)
            targetStackPanel = sender

            # If the source and target StackPanels are different
            if sourceStackPanel != targetStackPanel:
                # Ensure the legend is not already in the target StackPanel
                if '[Legend]' in textBlock.Text:
                    # Check if the same legend already exists in the target StackPanel
                    existing_items = [child.Text for child in targetStackPanel.Children if isinstance(child, TextBlock)]
                    if textBlock.Text in existing_items:
                        # Legend already exists in target; do not add
                        return

                # Remove the TextBlock from the source StackPanel
                sourceStackPanel.Children.Remove(textBlock)

                # Add the TextBlock to the target StackPanel
                targetStackPanel.Children.Add(textBlock)

            else:
                # If the source and target StackPanels are the same, do nothing
                pass

    def UIe_DuplicateView(self, sender, e):
        # Get the MenuItem
        menuItem = sender
        header = menuItem.Header

        # Get the ContextMenu
        contextMenu = menuItem.Parent
        # Get the PlacementTarget (ListBoxItem)
        listBoxItem = contextMenu.PlacementTarget
        # Get the view from the Tag
        view = listBoxItem.Tag

        # Determine the duplication option based on the MenuItem's Header
        if header == "Duplicate":                duplicate_option = ViewDuplicateOption.Duplicate
        elif header == "Duplicate As Detailed":  duplicate_option = ViewDuplicateOption.WithDetailing
        elif header == "Duplicate As Dependent": duplicate_option = ViewDuplicateOption.AsDependent
        else: return

        self.duplicate_view(listBoxItem, view, duplicate_option)

    def UIe_remove_item_on_right_click(self, sender, e):
        """Handle right-click to remove an item from the StackPanel and restore it in the ListBox."""
        # Get the clicked TextBlock
        text_block = sender

        # Find the parent StackPanel
        stack_panel = self.FindAncestor(StackPanel, text_block)
        if stack_panel:
            # Remove the TextBlock from the StackPanel
            stack_panel.Children.Remove(text_block)

        # Restore the corresponding ListBoxItem in the ListBox
        for item in self.UI_viewsListBox.Items:
            if item.Tag == text_block.Tag:  # Match by Tag
                item.Visibility = Visibility.Visible
                break

    def UIe_btn_run(self, sender, e):
        self.Close()


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
#==================================================

from pyrevit import script
output = script.get_output()

#👀 Show form to the user
try:
    UI           = EF_SheetGenerator()
    border_cards = UI.BorderSheetCards
    title_block = UI.selected_title_block_type
except SystemExit:
    exit = True
except:
    exitscript()

if exit:
    import sys
    sys.exit()

# Iterate through and create new sheets (if views were added)
t = Transaction(doc, "EF_Sheet Generator")
t.Start()

report_data = []

with forms.ProgressBar() as pb:
    for n, border_card in enumerate(border_cards):
        pb.update_progress(n, len(border_cards)) #Update Progress Bar

        card_reader = BorderSheetCardReader(border_card)
        views       = card_reader.views

        if views:
            # Create Sheet
            new_sheet = ViewSheet.Create(doc, title_block.Id)
            rename_sheet(new_sheet, card_reader.sheet_name, card_reader.sheet_number)

            # Create Viewports
            X,Y = 0,0

            link_views = []
            for view in views: #type: View
                if Viewport.CanAddViewToSheet(doc, new_sheet.Id, view.Id):
                    Y += 3
                    Viewport.Create(doc, new_sheet.Id, view.Id, XYZ(X, Y, 0))


            # Update Report
            report_data.append((new_sheet, views))

t.Commit()





# ╦═╗╔═╗╔═╗╔═╗╦═╗╔╦╗  ╔═╗╔═╗╦═╗╔╦╗
# ╠╦╝║╣ ╠═╝║ ║╠╦╝ ║   ║  ╠═╣╠╦╝ ║║
# ╩╚═╚═╝╩  ╚═╝╩╚═ ╩   ╚═╝╩ ╩╩╚══╩╝
#==================================================

class EF_ReportTable(Window):
    """Quick and Dirty form. Might make it better later... You know how it goes """
    def __init__(self, report_data):
        # Load the XAML file
        path_xaml_file = os.path.join(PATH_SCRIPT, 'ReportTable.xaml')
        wpf.LoadComponent(self, path_xaml_file)
        self.load_logo()

        # Populate data
        self.populate_data(report_data)

        # Show the window
        self.Show()         #<- This crashes revit If I add MouseDown event for dragging...
        # self.ShowDialog() #<- This Works

    def load_logo(self):
        import os
        PATH_SCRIPT = os.path.dirname(__file__)
        logo_path   = os.path.join(PATH_SCRIPT, 'ef_logo.png')

        from System.Windows.Media.Imaging import BitmapImage
        from System import Uri
        self.UI_ef_logo.Source = BitmapImage(Uri(logo_path))

    def populate_data(self, report_data):
        # Find the MainStackPanel in the XAML
        main_stack_panel = self.UI_main_stack

        if main_stack_panel is None:
            raise ValueError("MainStackPanel not found in XAML.")

        # Clear any existing items in the MainStackPanel
        main_stack_panel.Children.Clear()

        # Populate with new data
        for sheet, views in report_data:
            # Create a DockPanel for each sheet
            dock_panel = DockPanel()
            dock_panel.Margin = Thickness(0, 5, 0, 0)

            # Create a Border for the sheet
            sheet_border = Border()
            sheet_border.Padding = Thickness(10)
            sheet_border.Margin = Thickness(5)
            sheet_border.HorizontalAlignment = HorizontalAlignment.Left
            sheet_border.Background = SolidColorBrush(ColorConverter.ConvertFromString("#1c1c1c"))

            sheet_border.MouseDown += self.UIe_view_button_click
            sheet_border.Cursor = Cursors.Hand
            sheet_border.Tag = sheet

            # Create a StackPanel for the sheet's TextBlocks
            sheet_stack = StackPanel()
            sheet_stack.Orientation = Orientation.Vertical

            # Create TextBlock for SheetNumber
            sheet_number_text = TextBlock()
            sheet_number_text.Text = sheet.SheetNumber
            sheet_number_text.Foreground = SolidColorBrush(ColorConverter.ConvertFromString("#FF8C00"))  # Orange color
            sheet_number_text.FontSize = 10  # Smaller font size
            sheet_stack.Children.Add(sheet_number_text)

            # Create TextBlock for Sheet.Name
            sheet_name_text = TextBlock()
            sheet_name_text.Text = sheet.Name
            sheet_name_text.Foreground = SolidColorBrush(ColorConverter.ConvertFromString("#f2f2f2"))  # White color
            sheet_stack.Children.Add(sheet_name_text)

            # Set the StackPanel as the child of the sheet Border
            sheet_border.Child = sheet_stack

            # Add the sheet Border to the DockPanel
            dock_panel.Children.Add(sheet_border)

            # Create a WrapPanel for views
            wrap_panel = WrapPanel()
            wrap_panel.HorizontalAlignment = HorizontalAlignment.Right
            wrap_panel.Margin = Thickness(5)

            for view in views:
                # Create a Border for each view
                view_border = Border()
                view_border.Padding = Thickness(10)
                view_border.Margin = Thickness(5)
                view_border.Background = SolidColorBrush(ColorConverter.ConvertFromString("#1c1c1c"))

                view_border.MouseDown += self.UIe_view_button_click
                view_border.Cursor = Cursors.Hand
                view_border.Tag = view

                # Create a StackPanel for the view's TextBlocks
                view_stack = StackPanel()
                view_stack.Orientation = Orientation.Vertical

                # Create TextBlock for view.ViewType
                view_type_text = TextBlock()
                view_type_text.Text = str(view.ViewType)
                view_type_text.Foreground = SolidColorBrush(ColorConverter.ConvertFromString("#FF8C00"))  # Orange color
                view_type_text.FontSize = 10  # Smaller font size
                view_stack.Children.Add(view_type_text)

                # Create TextBlock for view.Name
                view_name_text = TextBlock()
                view_name_text.Text = view.Name
                view_name_text.Foreground = SolidColorBrush(ColorConverter.ConvertFromString("#f2f2f2"))  # White color
                view_stack.Children.Add(view_name_text)

                # Set the StackPanel as the child of the view Border
                view_border.Child = view_stack

                # Add the view Border to the WrapPanel
                wrap_panel.Children.Add(view_border)

            # Add the WrapPanel to the DockPanel
            dock_panel.Children.Add(wrap_panel)

            # Add the DockPanel to the MainStackPanel
            main_stack_panel.Children.Add(dock_panel)

            # Add a bottom Border line for the DockPanel
            bottom_border = Border()
            bottom_border.Height = 1
            bottom_border.Margin = Thickness(0, 5, 0, 5)
            bottom_border.Background = SolidColorBrush(
                ColorConverter.ConvertFromString("#404040"))  # Gray color for the line
            main_stack_panel.Children.Add(bottom_border)

    def UIe_view_button_click(self, sender, e):
        view = sender.Tag

        try:
            uidoc = __revit__.ActiveUIDocument
            uidoc.ActiveView = view
        except:
            import traceback
            print(traceback.format_exc())


    def UIe_header_drag(self, sender, e):
        """Drag window by holding LeftButton on the header."""
        # No Idea why, but you have to re-import this shit again.
        # I crashed Revit more than 100 times to come to this conclusion.
        # Let me know if you find better solution.
        from System.Windows.Window import DragMove
        from System.Windows.Input import MouseButtonState, Cursors


        if e.LeftButton == MouseButtonState.Pressed:
            self.DragMove()
    #

    def UIe_RequestNavigate(self, sender, e):
        """Forwarding for a Hyperlinks."""
        from System.Diagnostics.Process import Start
        Start(e.Uri.AbsoluteUri)

    def button_close(self,sender,e):
        # print(self)
        # print('test')
        self.Close()

#👀 Display Report Card
Report = EF_ReportTable(report_data)