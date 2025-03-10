# -*- coding: utf-8 -*-
__title__ = "Place SingleViews on Sheets"
__doc__ = """Version = 2.0
Date    = 31.08.2020 | 29.11.2024
_____________________________________________________________________
Description:
Place individual Views on new Sheets in Revit with specified 
Titleblock and ShetNumbering Rules
_____________________________________________________________________
How-to:

-> Start the tool
-> Select Views
-> Specify:
            - Prefix
            - Start Count
            - TitleBlock
-> Generate Sheets

_____________________________________________________________________
Last update:
- [29.11.2024] - Release V2.0 - Rewrote the code.
- Forgot to mention changes in between ...
- [11.07.2021] - Release V0.2
- [11.07.2021] - Refactored
_____________________________________________________________________
To-do:
- Allign view to the center of title block
- Report Card
_____________________________________________________________________
"""

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> IMPORTS
from Autodesk.Revit.DB import *
from pyrevit import forms
import os, clr, wpf


# WPF Imports
clr.AddReference("System")
from System.Collections.ObjectModel import ObservableCollection
from System.Diagnostics.Process     import Start
from System.Windows.Controls        import Orientation, CheckBox, DockPanel, Button,ComboBoxItem, TextBox, ListBoxItem, StackPanel, TextBlock, WrapPanel, Border, ScrollViewer
from System.Windows.Window          import DragMove
from System.Windows.Input           import MouseButtonState, Cursors, MouseButtonEventHandler
from System.Windows.Media           import VisualTreeHelper, SolidColorBrush, Colors, SolidColorBrush, ColorConverter, Brushes
from System.Windows                 import Window, DragDropEffects, DataObject, DragDrop, Visibility, HorizontalAlignment, VerticalAlignment, CornerRadius, Thickness, Style, EventSetter, Point
from System                         import Uri


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VARIABLES
PATH_SCRIPT = os.path.dirname(__file__)
doc     = __revit__.ActiveUIDocument.Document
uidoc   = __revit__.ActiveUIDocument
app     = __revit__.Application

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GUI

class EF_SingleViewsOnSheetsForm(Window):

    def __init__(self):
        # Form Toggles and Container
        self.isDragging            = False
        self.draggedItemIndex      = None
        self.start_point           = None
        self.view_name_to_checkbox = {}

        # 🎨 Load XAML and Styling
        path_xaml_file = os.path.join(PATH_SCRIPT, 'SingleViewsOnSheets.xaml')
        wpf.LoadComponent(self, path_xaml_file)
        self.add_listbox_style()
        self.load_logo()

        #⬇️ Populate the ListBox with views
        self.populate_views_listbox()
        self.populate_title_blocks_combo()


        #📦 Create Observable Collection to enable Dragging feature
        self.sheet_cards                      = ObservableCollection[str]()
        self.UI_sheetCardsListBox.ItemsSource = self.sheet_cards


        #👀 Show Form
        self.ShowDialog()



    # ╔╦╗╔═╗╔╦╗╦ ╦╔═╗╔╦╗╔═╗
    # ║║║║╣  ║ ╠═╣║ ║ ║║╚═╗
    # ╩ ╩╚═╝ ╩ ╩ ╩╚═╝═╩╝╚═╝

    def create_listbox_view(self, view_name, view):
        # 🟦 Create TextBlock
        textblock = TextBlock()
        textblock.Text = view_name
        textblock.Foreground = Brushes.White  # Remove?

        # 🟦 Create CheckBox
        check = CheckBox()
        check.Content = textblock
        check.Tag = view

        # Store the CheckBox in the mapping
        self.view_name_to_checkbox[view.Name] = check

        # 🚨 CheckBox Events
        check.Checked   += self.UIe_add_to_list
        check.Unchecked += self.UIe_remove_from_list

        # 🟦 Create ListboxItem
        item = ListBoxItem()
        item.Content = check
        item.Tag = view

        return item

    def populate_views_listbox(self):
        """Populate the ListBox with all views in the project."""
        # Get Views
        views = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).WhereElementIsNotElementType().ToElements()
        views = [view for view in views if not view.IsTemplate]  # Remove Templates
        views = [view for view in views if not view.get_Parameter(BuiltInParameter.VIEWPORT_SHEET_NUMBER).AsString()]  # Unplaced

        # Create Dict Views {ViewType_ViewName : View}}
        dict_views = {'[{}] {}'.format(view.ViewType, view.Name): view for view in views}

        for view_name, view in sorted(dict_views.items()):
            #🟦 Create ListBoxItem for Views
            item = self.create_listbox_view(view_name, view)

            #🟧 Add ListBoxItem to ListBox
            self.UI_viewsListBox.Items.Add(item)


    def add_listbox_style(self):
        existing_style = self.UI_sheetCardsListBox.ItemContainerStyle

        if not existing_style :
            existing_style = Style()
            self.UI_sheetCardsListBox.ItemContainerStyle = existing_style

        # Add the EventSetter to the existing style's Setters
        eventSetter = EventSetter()
        eventSetter.Event = ListBoxItem.MouseRightButtonDownEvent
        eventSetter.Handler = MouseButtonEventHandler(self.UI_sheetCardsListBox_MouseRightButtonDown)
        existing_style.Setters.Add(eventSetter)


        self.UI_sheetCardsListBox.PreviewMouseRightButtonDown += self.UIe_sheetCardsListBox_PreviewMouseRightButtonDown


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
            new_item = self.create_listbox_view(view_name, new_view)

            # Insert Duplicated View after original
            index = self.UI_viewsListBox.Items.IndexOf(listBoxItem)
            self.UI_viewsListBox.Items.Insert(index + 1, new_item)

            # Refresh the search filter
            self.UIe_search_changed(None, None)

        except Exception as ex:
            print("Error duplicating view: {}".format(ex))

        finally:
            t.Commit()


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


    # ╔═╗╦  ╦╔═╗╔╗╔╔╦╗╔═╗
    # ║╣ ╚╗╔╝║╣ ║║║ ║ ╚═╗
    # ╚═╝ ╚╝ ╚═╝╝╚╝ ╩ ╚═╝
    # Add this method to your class:
    def UIe_sheetCardsListBox_PreviewMouseRightButtonDown(self, sender, e):
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
            print("Exception in UIe_sheetCardsListBox_PreviewMouseRightButtonDown:", ex)


    def UncheckViewInLeftListBox(self, view_name):
        try:
            check = self.view_name_to_checkbox.get(view_name)
            if check is not None:
                check.IsChecked = False
        except Exception as ex:
            print("Exception in UncheckViewInLeftListBox:", ex)


    # ╔═╗╦  ╦╔═╗╔╗╔╔╦╗╔═╗  ╔╦╗╦═╗╔═╗╔═╗
    # ║╣ ╚╗╔╝║╣ ║║║ ║ ╚═╗   ║║╠╦╝╠═╣║ ╦
    # ╚═╝ ╚╝ ╚═╝╝╚╝ ╩ ╚═╝  ═╩╝╩╚═╩ ╩╚═╝

    def GetListBoxItemUnderMouse(self, e):
        point = e.GetPosition(self.UI_sheetCardsListBox)
        element = self.UI_sheetCardsListBox.InputHitTest(point)
        while element is not None and not isinstance(element, ListBoxItem):
            element = VisualTreeHelper.GetParent(element)
        return element


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


    # ╔═╗╔═╗╔╗╔╔═╗╦═╗╔═╗╦    ╔═╗╦  ╦╔═╗╔╗╔╔╦╗╔═╗
    # ║ ╦║╣ ║║║║╣ ╠╦╝╠═╣║    ║╣ ╚╗╔╝║╣ ║║║ ║ ╚═╗
    # ╚═╝╚═╝╝╚╝╚═╝╩╚═╩ ╩╩═╝  ╚═╝ ╚╝ ╚═╝╝╚╝ ╩ ╚═╝

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

    # ╔═╗╦═╗╔═╗╔═╗╔═╗╔╦╗╦╔═╗╔═╗
    # ╠═╝╠╦╝║ ║╠═╝║╣  ║ ║║╣ ╚═╗
    # ╩  ╩╚═╚═╝╩  ╚═╝ ╩ ╩╚═╝╚═╝
    @property
    def selected_views(self):
        selected_views = []
        for item in self.UI_viewsListBox.Items:
            check = item.Content
            if check.IsChecked:
                selected_views.append(item.Tag)

        return selected_views

    @property
    def selected_title_block(self):
        selected_item = self.UI_combo_title_blocks.SelectedItem
        title_block   = selected_item.Tag

        return title_block



# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
#==================================================
UI = EF_SingleViewsOnSheetsForm()


selected_views      = UI.selected_views
selected_titleblock = UI.selected_title_block


prefix = '05.04.'
start_count = 1

# >>>>>>>>>> MAIN LOOP

print("=" * 30 + " Placing {} views on sheets.".format(len(selected_views)))

t = Transaction(doc, "Py: New Sheets")
t.Start()

for view in selected_views:

    # >>>>>>>>>> CREATE SHEET
    Sheet = ViewSheet.Create(doc, selected_titleblock.Id)

    # >>>>>>>>>> SET SHEET NUMBER
    count = "{:02d}".format(start_count)  # 1 -> 01...
    sheet_number = prefix + count

    fail_count = 0
    while True:
        fail_count += 1
        if fail_count > 10:
            break
        try:
            Sheet.SheetNumber = sheet_number
            break
        except:
            sheet_number += "*"
    start_count += 1

    # >>>>>>>>>> PLACE VIEW ON SHEET

    Viewport.Create(doc, Sheet.Id, view.Id, XYZ(0, 0, 0))
    Sheet.Name = view.Name

    from pyrevit import script
    output = script.get_output()
    link = output.linkify(Sheet.Id, title='{}_{}'.format(Sheet.SheetNumber, Sheet.Name))

    print('Created Sheet: {}'.format(link))
t.Commit()


