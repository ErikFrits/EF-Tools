import os
def get_gui_filepath():

    base = os.path.dirname(__file__)
    file = "GUI_test.xaml"
    print(os.path.join(base,file))
    return os.path.join(base,file)
