# -*- coding: utf-8 -*-

__title__ = "Place SingleViews on Sheets"
__doc__ = """Version = 2.0
Date    = 31.08.2020 | 29.11.2024
_____________________________________________________________________
Description:
>>> THIS TOOL IS STIL WORK IN PROGRESS <<<

Place selected views to new sheets.
_____________________________________________________________________
How-to:

-> Select views in ProjectBrowser
-> Click the button
-> Select TitleBlock
-> Set SheetNumbering rules
-> Run
_____________________________________________________________________
Prerequisite:

You have to select Views in ProjectBrowser.
_____________________________________________________________________
Last update:
- [29.11.2024] - Release V2.0 - Rewrote the code.
- [11.07.2021] - Release V0.2
- [11.07.2021] - Refactored

_____________________________________________________________________
To-do:
- Sort views for correct naming (Elevation/ViewNames)
- Allign view to the center of title block
- GUI
- Set selection to newly created sheets.
_____________________________________________________________________
"""

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> IMPORTS
from Autodesk.Revit.DB import *
from pyrevit import forms
import os, clr, wpf


# WPF Imports
clr.AddReference("System")
from System.Windows import Window, DragDropEffects, DataObject, DragDrop, Visibility, HorizontalAlignment, VerticalAlignment, CornerRadius, Thickness
from System.Windows.Window import DragMove
from System.Windows.Controls import Orientation, CheckBox, DockPanel, Button,ComboBoxItem, TextBox, ListBoxItem, StackPanel, TextBlock, WrapPanel, Border, ScrollViewer
from System.Windows.Input import MouseButtonState, Cursors
from System.Windows.Media import VisualTreeHelper, SolidColorBrush, Colors, SolidColorBrush, ColorConverter, Brushes
from System.Diagnostics.Process import Start
from System import Uri
from System.Collections.ObjectModel import ObservableCollection

from System import Activator
from System.Windows import Point
from System.Windows import Style, EventSetter
from System.Windows.Controls import ListBoxItem
from System.Windows.Input import MouseButtonEventHandler


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VARIABLES
PATH_SCRIPT = os.path.dirname(__file__)
doc     = __revit__.ActiveUIDocument.Document
uidoc   = __revit__.ActiveUIDocument
app     = __revit__.Application

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GUI

# CLAS

class EF_SingleViewsOnSheetsForm(Window):

    def __init__(self):

        self.view_name_to_checkbox = {}

        # 🎨 Load XAML
        path_xaml_file = os.path.join(PATH_SCRIPT, 'SingleViewsOnSheets.xaml')
        wpf.LoadComponent(self, path_xaml_file)
        self.load_logo()

        self.isDragging = False
        self.draggedItemIndex = None
        self.placeholderItem = None

        # Initialize variables for drag-and-drop
        self.start_point = None
        # self.sheet_cards = []
        self.sheet_cards = ObservableCollection[str]()
        self.UI_sheetCardsListBox.ItemsSource = self.sheet_cards

        # Call the method to add right-click functionality
        self.add_listbox_style()
        self.UI_sheetCardsListBox.PreviewMouseRightButtonDown += self.UI_sheetCardsListBox_PreviewMouseRightButtonDown


        #⬇️ Populate the ListBox with views
        self.populate_views_listbox()
        self.populate_title_blocks_combo()

        #👀 Show Form
        self.ShowDialog()

    def add_listbox_style(self):
        existing_style = self.UI_sheetCardsListBox.ItemContainerStyle

        if existing_style is None:
            # If there's no existing style, create one and assign it
            existing_style = Style()
            self.UI_sheetCardsListBox.ItemContainerStyle = existing_style

        # Add the EventSetter to the existing style's Setters
        eventSetter = EventSetter()
        eventSetter.Event = ListBoxItem.MouseRightButtonDownEvent
        eventSetter.Handler = MouseButtonEventHandler(self.UI_sheetCardsListBox_MouseRightButtonDown)
        existing_style.Setters.Add(eventSetter)

    # Add this method to your class:
    def UI_sheetCardsListBox_PreviewMouseRightButtonDown(self, sender, e):
        try:
            # Get the ListBoxItem under the mouse
            item = self.GetListBoxItemUnderMouse(e)
            if item is not None:
                view_name = item.Content  # The content is the view name

                # Remove from sheet_cards
                if view_name in self.sheet_cards:
                    self.sheet_cards.Remove(view_name)

                # Uncheck the corresponding CheckBox in UI_viewsListBox
                self.UncheckViewInLeftListBox(view_name)
                e.Handled = True
        except Exception as ex:
            print("Exception in UI_sheetCardsListBox_PreviewMouseRightButtonDown:", ex)


    def GetListBoxItemUnderMouse(self, e):
        point = e.GetPosition(self.UI_sheetCardsListBox)
        element = self.UI_sheetCardsListBox.InputHitTest(point)
        while element is not None and not isinstance(element, ListBoxItem):
            element = VisualTreeHelper.GetParent(element)
        return element

    def UncheckViewInLeftListBox(self, view_name):
        try:
            check = self.view_name_to_checkbox.get(view_name)
            if check is not None:
                check.IsChecked = False
        except Exception as ex:
            print("Exception in UncheckViewInLeftListBox:", ex)

    def UI_sheetCardsListBox_MouseRightButtonDown(self, sender, e):
        try:
            item = sender
            view_name = item.Content
            print('Hi')
            e.Handled = True
        except Exception as ex:
            print("Exception in UI_sheetCardsListBox_MouseRightButtonDown:", ex)

    def ListBox_MouseLeftButtonUp(self, sender, e):
        try:
            if self.isDragging:
                self.isDragging = False
                self.draggedItemIndex = None
        except Exception as ex:
            print("Exception in ListBox_MouseLeftButtonUp:", ex)

    def ListBox_PreviewMouseLeftButtonDown(self, sender, e):
        try:
            # Get the ListBoxItem under the mouse
            item = self.GetListBoxItemUnderMouse(e)
            if item is not None:
                self.isDragging = True
                self.start_point = e.GetPosition(self.UI_sheetCardsListBox)
                self.draggedItemIndex = self.UI_sheetCardsListBox.Items.IndexOf(item.Content)
                e.Handled = True
        except Exception as ex:
            print("Exception in ListBox_PreviewMouseLeftButtonDown:", ex)

    def ListBox_PreviewMouseMove(self, sender, e):
        try:
            if self.isDragging and self.draggedItemIndex is not None:
                current_position = e.GetPosition(self.UI_sheetCardsListBox)
                diff_y = current_position.Y - self.start_point.Y

                # Define minimum distance to start moving the item
                drag_threshold = 5  # Adjust as needed
                if abs(diff_y) > drag_threshold:
                    # Determine the new index
                    newIndex = self.GetCurrentIndex(current_position)
                    if newIndex != self.draggedItemIndex and newIndex >= 0 and newIndex < len(self.sheet_cards):
                        # Move the item in the ObservableCollection
                        self.sheet_cards.Move(self.draggedItemIndex, newIndex)
                        self.draggedItemIndex = newIndex
                        self.start_point = current_position  # Reset start point
        except Exception as ex:
            print("Exception in ListBox_PreviewMouseMove:", ex)

    def GetListBoxItemUnderMouse(self, e):
        # Get the element under the mouse
        try:
            point = e.GetPosition(self.UI_sheetCardsListBox)
            element = self.UI_sheetCardsListBox.InputHitTest(point)
            while element is not None and not isinstance(element, ListBoxItem):
                element = VisualTreeHelper.GetParent(element)
            return element
        except Exception as ex:
            print("Exception in GetListBoxItemUnderMouse:", ex)
            return None

    def GetCurrentIndex(self, position):
        index = -1
        for i in range(len(self.sheet_cards)):
            item = self.UI_sheetCardsListBox.ItemContainerGenerator.ContainerFromIndex(i)
            if item is not None:
                transform = item.TransformToVisual(self.UI_sheetCardsListBox)
                item_position = transform.Transform(Point(0, 0))
                item_height = item.ActualHeight
                if position.Y < item_position.Y + item_height:
                    index = i
                    break
        if index == -1:
            index = len(self.sheet_cards) - 1
        return index




    def MoveItemUp_Click(self, sender, e):
        try:
            item = sender.DataContext
            index = self.sheet_cards.index(item)
            if index > 0:
                self.sheet_cards[index], self.sheet_cards[index - 1] = self.sheet_cards[index - 1], self.sheet_cards[index]
                self.RefreshListBox()
        except Exception as ex:
            print("Exception in MoveItemUp_Click:", ex)

    def MoveItemDown_Click(self, sender, e):
        try:
            item = sender.DataContext
            index = self.sheet_cards.index(item)
            if index < len(self.sheet_cards) - 1:
                self.sheet_cards[index], self.sheet_cards[index + 1] = self.sheet_cards[index + 1], self.sheet_cards[index]
                self.RefreshListBox()
        except Exception as ex:
            print("Exception in MoveItemDown_Click:", ex)

    def RefreshListBox(self):
        # Refresh the ItemsSource binding
        self.UI_sheetCardsListBox.ItemsSource = None
        self.UI_sheetCardsListBox.ItemsSource = self.sheet_cards



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


    def populate_views_listbox(self):
        """Populate the ListBox with all views in the project."""
        # Get Views
        views = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).WhereElementIsNotElementType().ToElements()
        views = [view for view in views if not view.IsTemplate]  # Remove Templates
        views = [view for view in views if not view.get_Parameter(BuiltInParameter.VIEWPORT_SHEET_NUMBER).AsString()]  # Unplaced

        # Create Dict Views {ViewType_ViewName : View}}
        dict_views = {'[{}] {}'.format(view.ViewType, view.Name): view for view in views}

        for view_name, view in sorted(dict_views.items()):
            #🟦 Create TextBlock
            textblock = TextBlock()
            textblock.Text = view_name
            textblock.Foreground = Brushes.White #Remove?

            #🟦 Create CheckBox
            check         = CheckBox()
            check.Content = textblock
            check.Tag     = view

            # Store the CheckBox in the mapping
            self.view_name_to_checkbox[view.Name] = check

            #🚨 CheckBox Events
            check.Checked   += self.UIe_add_to_list
            check.Unchecked += self.UIe_remove_from_list

            #🟦 Create ListboxItem
            item = ListBoxItem()
            item.Content = check
            item.Tag     = view

            #🟧 Add ListBoxItem to ListBox
            self.UI_viewsListBox.Items.Add(item)

    def ListBox_DragOver(self, sender, e):
        try:
            position = e.GetPosition(self.UI_sheetCardsListBox)
            index_new = self.GetCurrentIndex(position)
            if index_new < 0:
                return

            # Get the item being dragged
            listbox_item = e.Data.GetData("ListBoxItem")
            if listbox_item is None:
                return
            item_text = listbox_item.Content

            if item_text not in self.sheet_cards:
                return

            index_old = self.sheet_cards.IndexOf(item_text)
            if index_old != index_new:
                # Move the item in the ObservableCollection
                self.sheet_cards.Move(index_old, index_new)
                # Optionally update start_point
                self.start_point = position  # Update with current position if needed
        except Exception as ex:
            print("Exception in ListBox_DragOver:", ex)

    def UIe_add_to_list(self, sender, e):
        view = sender.Tag  # Get the view object from the CheckBox's Tag
        view_name = view.Name
        if view_name not in self.sheet_cards:
            self.sheet_cards.Add(view_name)

    def UIe_select_all(self, sender, e):

        for item in self.UI_viewsListBox.Items:
            if item.Visibility == Visibility.Visible:
                check = item.Content
                check.IsChecked = True


    def UIe_select_none(self, sender, e):
        for item in self.UI_viewsListBox.Items:
            if item.Visibility == Visibility.Visible:
                check = item.Content
                check.IsChecked = False

    def UIe_remove_from_list(self, sender, e):
        view = sender.Tag  # Get the view object from the CheckBox's Tag
        view_name = view.Name
        if view_name in self.sheet_cards:
            self.sheet_cards.Remove(view_name)

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


    def load_logo(self):
        import os
        PATH_SCRIPT = os.path.dirname(__file__)
        logo_path   = os.path.join(PATH_SCRIPT, 'ef_logo.png')

        from System.Windows.Media.Imaging import BitmapImage
        from System import Uri
        self.UI_ef_logo.Source = BitmapImage(Uri(logo_path))

    # ╦  ╦╔═╗╔╦╗╔╗ ╔═╗═╗ ╦  ╔═╗╔═╗╔╗╔╔╦╗╦═╗╔═╗╦  ╔═╗
    # ║  ║╚═╗ ║ ╠╩╗║ ║╔╩╦╝  ║  ║ ║║║║ ║ ╠╦╝║ ║║  ╚═╗
    # ╩═╝╩╚═╝ ╩ ╚═╝╚═╝╩ ╚═  ╚═╝╚═╝╝╚╝ ╩ ╩╚═╚═╝╩═╝╚═╝




    # ╔═╗╦  ╦╔═╗╔╗╔╔╦╗╔═╗
    # ║╣ ╚╗╔╝║╣ ║║║ ║ ╚═╗
    # ╚═╝ ╚╝ ╚═╝╝╚╝ ╩ ╚═╝

    def UIe_search_changed(self, sender, e):
        """Filter items in the viewsListBox based on search input.
        Use Visibility to Hide and Show items instead of recreating the list."""
        search_input  = self.UI_search.Text.strip().lower()
        search_words  = search_input.split() if search_input else []

        # Control Views Visibility
        for item in self.UI_viewsListBox.Items:
            check     = item.Content
            textblock = check.Content
            view_name = textblock.Text.lower()
            view      = item.Tag
            view_id   = view.Id

            if all(word in view_name for word in search_words) or not search_words:
                item.Visibility = Visibility.Visible
            else:
                item.Visibility = Visibility.Collapsed


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

    def UIe_btn_run(self, sender, e):
        self.Close()

x = EF_SingleViewsOnSheetsForm()

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
#==================================================







#
#
# prefix = GUI.prefix
# start_count = GUI.start_count
#
# # >>>>>>>>>> MAIN LOOP
#
# print("=" * 30 + " Placing {} views on sheets.".format(len(selected_views)))
#
# t = Transaction(doc, "Py: New Sheets")
# t.Start()
#
# for view in selected_views:
#
#     # >>>>>>>>>> CREATE SHEET
#     Sheet = ViewSheet.Create(doc, selected_title_block)
#
#     # >>>>>>>>>> SET SHEET NUMBER
#     count = "{:02d}".format(start_count)  # 1 -> 01...
#     sheet_number = prefix + count
#
#     fail_count = 0
#     while True:
#         fail_count += 1
#         if fail_count > 10:
#             break
#         try:
#             Sheet.SheetNumber = sheet_number
#             break
#         except:
#             sheet_number += "*"
#     start_count += 1
#
#     # >>>>>>>>>> PLACE VIEW ON SHEET
#
#     Viewport.Create(doc, Sheet.Id, view.Id, XYZ(0, 0, 0))
#     Sheet.Name = view.Name
#     print('Created sheet: {} - {}'.format(sheet_number, Sheet.Name))
# t.Commit()
#
#
