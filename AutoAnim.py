#!/usr/bin/env python

from Animator import Animator

from my_utils.args import parseArgs

import sys


def main():
    #args = getArgs()

    script_path = "s1.py"
    output_path = "./test.avi"
    psd_path = "./anim.psd"
    directory = None
    store_new = True

    directives = {
        "print_states": True
    }

    Animator(script_path, output_path, psd_path=psd_path, directory=directory, store_new=store_new, **directives).animate()###

def getArgs():
    argExpression = {
        "flags": "input",
        "options": {
            "nargs": "?",
            "default": None,
            "help": "The expression to evaluate"
        }
    }
    argPerLine = {
        "flags": ["-l","--lines"],
        "options": {
            "dest": "perLine",
            "action": "store_true",
            "help": "Evaluate each line as unique expression"
        }
    }

    parserSetup = {
        "description": "Evaluates a simple math expression using python syntax",
        "args": [
            argPerLine,
            argExpression
        ]
    }

    args = parseArgs(parserSetup)

    #read from stdin if no expression is passed
    if(args.input is None):
        args.input = sys.stdin.read()

    #default behavior: remove all whitespace, newlines, and tabs
    regex = r"[\s]*"

    #optional: if perLine option given, remove whitespace but not newlines
    if args.perLine:
        regex = r"[ \t]*"

    #perform regex substitution and split on any newlines
    args.expressions = re.sub(regex,"", args.input).rstrip().split("\n")

    return args

if __name__ == '__main__':
    
    DEBUG = True

    if DEBUG:
        #import doctest
        #print(doctest.testmod())
        main()
        exit()

    try:
        main()
    except Exception as e:
        print(f"AutoAnim: an error occured: {e}", file=sys.stderr)
