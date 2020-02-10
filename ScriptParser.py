#!/usr/bin/env python

from importlib import import_module
from pathlib import Path
import types
import builtins
import sys

from API import wait, time, ignore, endloop, ignored, get_model, Loopable, set_current_context, get_waiting_funcs

def decorate_all_in_module(module, decorator, to_ignore):
    for name in dir(module):
        obj = getattr(module, name)

        if isinstance(obj, types.FunctionType):
            if obj in to_ignore:
                continue

            setattr(module, name, decorator(obj))

class ScriptParser:
    def __init__(self, script_path):
        self.script_path = Path(script_path)

    def setup(self):
        #Make the API functions inherently available to scripts
        builtins.wait = wait
        builtins.time = time
        builtins.ignore = ignore
        builtins.ignored = ignored
        builtins.endloop = endloop
        builtins.Loopable = Loopable
        builtins.get_model = get_model
        builtins._ = get_model()

        #allow for scripts to be stored anywhere
        sys.path.insert(0, str(self.script_path.resolve().parents[0]))
        module = import_module(str(self.script_path.stem))

        if not hasattr(module, "main"):
            raise SyntaxError("Scripts must define a 'main' function")

        decorate_all_in_module(module, Loopable, ignored())

        set_current_context(module.main)

        return module.main

    def parse_script(self, verbose=False):

        if verbose:
            print("Setting up script environment")

        script_main = self.setup()
        model = get_model()

        if verbose:
            print("Executing script")

        script_main()

        if verbose:
            print("Finished main")

        #All open loops get implicitly stopped at the end of main()
        for func in get_waiting_funcs():

            if verbose:
                print("Implicitly stopping unstopped loop")

            func.stop()

        model.finish()

        #returns the dict of time:option pairs
        return model.temporal_dict
