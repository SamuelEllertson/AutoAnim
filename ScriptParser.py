#!/usr/bin/env python

from importlib import import_module
import types
import builtins

from API import wait, time, ignore, ignored, Model, FuncWrapper, set_current_context, get_waiting_funcs

def decorate_all_in_module(module, decorator, to_ignore):
    for name in dir(module):
        obj = getattr(module, name)

        if isinstance(obj, types.FunctionType):
            if obj in to_ignore:
                continue

            setattr(module, name, decorator(obj))

class ScriptParser:
    def __init__(self, script_path):
        self.script_path = script_path

    def setup(self):
        builtins.wait = wait
        builtins.time = time
        builtins.ignore = ignore
        builtins._ = Model()

        module = import_module(self.script_path[:-3])###

        if not hasattr(module, "main"):
            raise SyntaxError("Must define a main method")

        decorate_all_in_module(module, FuncWrapper, ignored())

        set_current_context(module.main)

        return module.main

    def parse_script(self):###needs better name

        main = self.setup()

        main()

        for func in get_waiting_funcs():
            func.stop()

        _.finish()

        return list(_), {} ###


