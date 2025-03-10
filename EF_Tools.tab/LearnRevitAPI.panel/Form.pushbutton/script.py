# -*- coding: utf-8 -*-
__title__   = "EF-Tools Form Test"

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
class MyForm(Window):
    def __init__(self):
        #⬇️ Connect to .xaml File (in the same folder!)
        path_xaml_file = os.path.join(PATH_SCRIPT, 'Form.xaml')


        #🎨 Load Styles
        self.load_styles()

        #⬇️ Load XAML Base
        wpf.LoadComponent(self, path_xaml_file)

        #⬇️ ️Load Header & Body & Footer
        self.load_header()
        self.load_body()
        self.load_footer()


        # Show Form
        self.ShowDialog()

    # ╔╦╗╔═╗╔╦╗╦ ╦╔═╗╔╦╗╔═╗
    # ║║║║╣  ║ ╠═╣║ ║ ║║╚═╗
    # ╩ ╩╚═╝ ╩ ╩ ╩╚═╝═╩╝╚═╝
    #==================================================
    def read_xaml_file(self,xaml_filename):
        """Method to read XAML File and return WPF control."""
        filepath_xaml = os.path.join(PATH_SCRIPT, xaml_filename)

        with open(filepath_xaml, 'r') as file:
            data = file.read()

        return XamlReader.Parse(data)

    def load_header(self):
        #⬇️ Load XAML Header
        header_control         = self.read_xaml_file('header.xaml')
        self.UI_header.Content = header_control

        #🚨 Add .Click Event to UI_header_btn_close
        close_button        = header_control.FindName("UI_header_btn_close")
        close_button.Click += self.UIe_header_close

        #🚨 Add .MouseDown Event to UI_header
        header_grid            = header_control.FindName("UI_header_grid")
        header_grid.MouseDown += self.UIe_header_drag

    def load_body(self):
        #⬇️ Load XAML Body
        body_control = self.read_xaml_file('TestForm.xaml')
        self.UI_body.Content = body_control.Content


    def load_footer(self):
        #⬇️ Load XAML Fooger
        control         = self.read_xaml_file('footer.xaml')
        self.UI_footer.Content = control

        # img                  = control.FindName("UI_logo")
        # img.Source = BitmapImage(Uri(r"C:\Users\Erik\Documents\00_LearnRevitAPI\01_RevitAPI_Development\01_pyRevit Extensions\GitHub\EF-Tools.extension\EF_Tools.tab\LearnRevitAPI.panel\Form.pushbutton\Logo - LearnRevitAPI (Shadows).png"))

        hyper                  = control.FindName("UI_footer_cta")
        hyper.NavigateUri      = Uri("https://learnrevitapi.com/ef-tools-cta")
        hyper.RequestNavigate += self.UIe_HyperLinkNavigate


    def load_styles(self):
        #���️ Load XAML Styles
        styles_control         = self.read_xaml_file('styles.xaml')
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
UI = MyForm()
