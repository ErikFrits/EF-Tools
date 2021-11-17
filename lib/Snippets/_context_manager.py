# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import Transaction
import contextlib
import traceback

import sys, os
# ╔═╗╔═╗╔╗╔╔╦╗╔═╗═╗ ╦╔╦╗  ╔╦╗╔═╗╔╗╔╔═╗╔═╗╔═╗╦═╗╔═╗
# ║  ║ ║║║║ ║ ║╣ ╔╩╦╝ ║   ║║║╠═╣║║║╠═╣║ ╦║╣ ╠╦╝╚═╗
# ╚═╝╚═╝╝╚╝ ╩ ╚═╝╩ ╚═ ╩   ╩ ╩╩ ╩╝╚╝╩ ╩╚═╝╚═╝╩╚═╚═╝ CONTEXT MANAGERS
#====================================================================================================

@contextlib.contextmanager
def try_except(debug=False):
    try:
        yield
    except Exception as e:
        if debug:
            print("*"*20)
            print("Exception occured: " + traceback.format_exc())
            print("*"*20)


@contextlib.contextmanager
def ef_Transaction(doc, title, debug = False):
    t = Transaction(doc, title)
    try:
        t.Start()
        yield
        t.Commit()

    except Exception as e:
        if debug:
            print("*"*20)
            print("Exception occured - Transaction is being Rollbacked!")
            print(traceback.format_exc())
            print("*"*20)
        t.RollBack()







