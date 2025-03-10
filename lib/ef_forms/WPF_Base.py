# -*- coding: utf-8 -*-
__LEARN_MORE__ = "https://learnrevitapi.com/courses/wpf" #🚀 Get Started with WPF

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#====================================================================================================
from pyrevit import forms   # By importing forms you also get references to WPF package! IT'S Very IMPORTANT !!!
import wpf, os, clr         # wpf can be imported only after pyrevit.forms!

# .NET Imports
clr.AddReference("System")
from System.Windows import Window
from System.Windows.Window import DragMove
from System.Windows.Input import MouseButtonState
from System.Windows.Markup import XamlReader
from System.Diagnostics.Process import Start
from System.Windows.Media.Imaging import BitmapImage

from System import Uri

# VARIABLES
PATH_SCRIPT = os.path.dirname(__file__)


# ╔╦╗╔═╗╦╔╗╔  ╔═╗╔═╗╦═╗╔╦╗
# ║║║╠═╣║║║║  ╠╣ ║ ║╠╦╝║║║
# ╩ ╩╩ ╩╩╝╚╝  ╚  ╚═╝╩╚═╩ ╩ MAIN FORM
#====================================================================================================
# Inherit .NET Window for your UI Form Class
class EF_WPF_Base(Window):
    """Setup Class for EF WPF Form. Use self.setup(xaml_file) to setup your form."""

    # ╔╦╗╔═╗╔╦╗╦ ╦╔═╗╔╦╗╔═╗
    # ║║║║╣  ║ ╠═╣║ ║ ║║╚═╗
    # ╩ ╩╚═╝ ╩ ╩ ╩╚═╝═╩╝╚═╝
    #==================================================
    def setup(self, xaml_path, W=300, H=None):
        #🎨 Load Styles
        self.load_styles()

        #⬇️ ️Load Header & Body & Footer
        self.load_base()
        self.load_header()
        self.load_body(xaml_path)
        self.load_footer()

        # Adjust WxH
        self.Width  = W
        self.Height = H



    def get_resource_path(self, filename):
        return os.path.join(PATH_SCRIPT, 'Resources', filename)

    def read_xaml_file(self,xaml_filepath):
        """Method to read XAML File and return WPF control."""
        with open(xaml_filepath, 'r') as file:
            data = file.read()
        return XamlReader.Parse(data)

    def copy_styles(self, control):
        control.Resources = self.Resources

    def load_body(self,xaml_file_body):
        """Provide Absolute path to your raw XAML file."""
        #⬇️ Load XAML Body
        body_control = self.read_xaml_file(xaml_file_body)

        #🎨 Copy Window.Resources
        self.copy_styles(body_control)

        # Copy XAML
        self.UI_body.Content = body_control.Content


    def load_base(self):
        xaml_file_base = self.get_resource_path('Base_WPF_Form.xaml')
        wpf.LoadComponent(self, xaml_file_base)


    def load_header(self):
        #⬇️ Load XAML Header
        xaml_file_header       = self.get_resource_path('header.xaml')
        header_control         = self.read_xaml_file(xaml_file_header)
        self.UI_header.Content = header_control

        #🎨 Copy Window.Resources
        self.copy_styles(header_control)

        #🚨 Add .Click Event to UI_header_btn_close
        close_button        = header_control.FindName("UI_header_btn_close")
        close_button.Click += self.UIe_header_close

        #🚨 Add .MouseDown Event to UI_header
        header_grid            = header_control.FindName("UI_header_grid")
        header_grid.MouseDown += self.UIe_header_drag

        #🟧 Update Custom Title
        UI_title = header_control.FindName("UI_Title")
        UI_title.Text = self.Title

    def load_footer(self):
        #⬇️ Load XAML Fooger
        xaml_file_footer       = self.get_resource_path('footer.xaml')
        footer_control         = self.read_xaml_file(xaml_file_footer)
        self.UI_footer.Content = footer_control

        #🎨 Copy Window.Resources
        self.copy_styles(footer_control)


        # img        = control.FindName("UI_logo")
        # img.Source = BitmapImage(Uri(r"C:\Users\Erik\...\img.png"))

        #🚨 Add .RequestNavigate Event to UI_footer_cta
        hyper                  = footer_control.FindName("UI_footer_cta")
        hyper.NavigateUri      = Uri("https://learnrevitapi.com/ef-tools-cta")
        hyper.RequestNavigate += self.UIe_HyperLinkNavigate


    def load_styles(self):
        #���️ Load XAML Styles
        xaml_file_styles = self.get_resource_path('styles.xaml')
        styles_control         = self.read_xaml_file(xaml_file_styles)
        self.Resources.MergedDictionaries.Add(styles_control)

    # ╔═╗╦  ╦╔═╗╔╗╔╔╦╗  ╦ ╦╔═╗╔╗╔╔╦╗╦  ╔═╗╦═╗╔═╗
    # ║╣ ╚╗╔╝║╣ ║║║ ║   ╠═╣╠═╣║║║ ║║║  ║╣ ╠╦╝╚═╗
    # ╚═╝ ╚╝ ╚═╝╝╚╝ ╩   ╩ ╩╩ ╩╝╚╝═╩╝╩═╝╚═╝╩╚═╚═╝
    #==================================================
    def UIe_header_close(self, sender,e):
        self.Close()


    def UIe_header_drag(self, sender, e):
        """EventHandler for Header Drag Functionality with LeftClick"""
        if e.LeftButton == MouseButtonState.Pressed:
            DragMove(self)

    def UIe_HyperLinkNavigate(self, sender, e):
        """EventHandler for Hyperlinks in the form."""
        Start(e.Uri.AbsoluteUri)


# ╦ ╦╔═╗╔═╗  ╔═╗╔═╗╦═╗╔╦╗
# ║ ║╚═╗║╣   ╠╣ ║ ║╠╦╝║║║
# ╚═╝╚═╝╚═╝  ╚  ╚═╝╩╚═╩ ╩
#====================================================================================================
# Show form to the user
UI = EF_WPF_Base()
