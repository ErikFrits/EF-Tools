def lib_test():
    print("/lib imports work!")
    import os
    print('[lib] Current dir:', os.path.abspath(os.curdir))
    print('[lib] File dir:'   , os.path.abspath(__file__))
    print('[lib] Parent dir'            ,os.path.dirname(__file__))
