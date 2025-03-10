# -*- coding: utf-8 -*-
__title__   = "EF-Tools Form Test"

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#====================================================================================================
from pyrevit import forms   # By importing forms you also get references to WPF package! IT'S Very IMPORTANT !!!
import wpf, os, clr         # wpf can be imported only after pyrevit.forms!



# VARIABLES
PATH_SCRIPT = os.path.dirname(__file__)


# ╔╦╗╔═╗╦╔╗╔  ╔═╗╔═╗╦═╗╔╦╗
# ║║║╠═╣║║║║  ╠╣ ║ ║╠╦╝║║║
# ╩ ╩╩ ╩╩╝╚╝  ╚  ╚═╝╩╚═╩ ╩ MAIN FORM
#====================================================================================================
# Inherit .NET Window for your UI Form Class
from ef_forms.WPF_Base import EF_WPF_Base
class MyForm(EF_WPF_Base):
    def __init__(self):
        self.title = __title__
        
        #⬇️ Setup XAML Code
        xaml_file = os.path.join(PATH_SCRIPT, "NewForm.xaml")
        self.setup(xaml_file)

        self.ShowDialog()



# ╦ ╦╔═╗╔═╗  ╔═╗╔═╗╦═╗╔╦╗
# ║ ║╚═╗║╣   ╠╣ ║ ║╠╦╝║║║
# ╚═╝╚═╝╚═╝  ╚  ╚═╝╩╚═╩ ╩
#====================================================================================================
# Show form to the user
UI = MyForm()
