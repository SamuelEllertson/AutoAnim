#!/usr/bin/env python

from importlib import import_module
import sys

import API
import tools

class ScriptParser:
    def __init__(self, args):
        self.args = args
        self.script_path = args.script_path
        
        API.init_api(args)

    def get_script(self):
        
        script = self.import_script()

        self.setup_script(script)

        return script

    def import_script(self):
        #dynamic module importing is a bit gross
        sys.path.insert(0, str(self.script_path.resolve().parents[0]))
        script = import_module(str(self.script_path.stem))

        #Make the API functions and AnimTools inherently available to scripts
        script.__dict__.update(API.__dict__)
        script.__dict__["AnimTools"] = tools.AnimTools

        return script

    def setup_script(self, script):
        if not hasattr(script, "main"):
            raise SyntaxError("Scripts must define a 'main' function")

        script.main = API.Loopable(script.main)

        API.set_current_context(script.main)

    def parse_script(self):

        verbose = self.args.verbose

        if verbose:
            print("Setting up script environment")

        script = self.get_script()

        if verbose:
            print("Executing script")

        script.main()

        if verbose:
            print("Finished main")

        #All open loops get implicitly stopped at the end of main()
        for func in API.get_waiting_funcs():

            if verbose:
                print("Implicitly stopping unstopped loop")

            func.stop(should_wait=False)

        model = API.get_model()
        model.finish()

        #returns the dict of time:option pairs
        return model.temporal_dict