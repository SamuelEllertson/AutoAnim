#!/usr/bin/env python

from pathlib import Path
import sys

from Animator import Animator
from args import parseArgs

from argparse import ArgumentTypeError

def main():
    args = getArgs()

    animator = Animator(args)
    animator.parse_script()

    if not args.no_output:
        animator.animate()

    if args.verbose:
        print("Finished")

def getArgs():
    arg_script_path = {
        "flags": ["-s", "--script-path"],
        "options": {
            "type": Path,
            "required": True,
            "metavar": "Path",
            "dest": "script_path",
            "help": "Path to script file"
        }
    }
    arg_output_path = {
        "flags": ["-o", "--output-path"],
        "options": {
            "default": Path("./output.avi"),
            "type": Path,
            "metavar": "Path",
            "dest": "output_path",
            "help": "Animation output path (default: output.avi)"
        }
    }
    arg_psd_path = {
        "flags": ["-p", "--psd-path"],
        "options": {
            "default": None,
            "type": Path,
            "metavar": "Path",
            "dest": "psd_path",
            "help": "Path to psd file that will be used to generate missing images"
        }
    }
    arg_directory_path = {
        "flags": ["-i", "--image-directory"],
        "options": {
            "default": Path("./image_cache"),
            "type": Path,
            "metavar": "Path",
            "dest": "directory",
            "help": "Path to directory for loading previously generated images and storing new images (default: ./image_cache)"
        }
    }
    arg_fps = {
        "flags": ["--fps"],
        "options": {
            "dest": "fps",
            "type": int,
            "default": 24,
            "metavar": "int",
            "help": "Sets the output Frames Per Second (default: 24)"
        }
    }
    arg_speed_multiplier = {
        "flags": ["--speed"],
        "options": {
            "dest": "speed_multiplier",
            "type": float,
            "default": 1.0,
            "metavar": "float",
            "help": "Set the speed of the output (default: 1.0)"
        }
    }
    arg_codec = {
        "flags": ["--codec"],
        "options": {
            "dest": "codec",
            "type": str,
            "default": "mp4v",
            "metavar": "codec",
            "help": "Sets the output video codec (default: mp4v)"
        }
    }
    arg_store_new = {
        "flags": ["--dont-store"],
        "options": {
            "dest": "store_new",
            "action": "store_false",
            "help": "If set newly generated images will not be stored to the image directory"
        }
    }
    arg_verbose = {
        "flags": ["-v", "--verbose"],
        "options": {
            "dest": "verbose",
            "action": "store_true",
            "help": "Enable verbose output"
        }
    }
    arg_print_states = {
        "flags": ["--print-states"],
        "options": {
            "dest": "print_states",
            "action": "store_true",
            "help": "Print the full list of parsed states"
        }
    }
    arg_no_output = {
        "flags": ["--no-output"],
        "options": {
            "dest": "no_output",
            "action": "store_true",
            "help": "Script will be parsed, but no output will be created"
        }
    }
    arg_create_texture = {
        "flags": ["-t", "--create-texture"],
        "options": {
            "dest": "create_texture",
            "action": "store_true",
            "help": "Instead of a video file, output animation as a tiled texture image"
        }
    }

    parserSetup = {
        "description": "Used to create animations",
        "args": [
            arg_script_path,
            arg_output_path,
            arg_psd_path,
            arg_directory_path,
            arg_fps,
            arg_speed_multiplier,
            arg_codec,
            arg_verbose,
            arg_print_states,
            arg_no_output,
            arg_store_new,
            arg_create_texture
        ]
    }

    args = parseArgs(parserSetup)

    args.directory.mkdir(exist_ok=True)

    if args.speed_multiplier <= 0:
        raise ArgumentTypeError(f"speed-multiplier must be a positive value")

    #if creating a texture, and default output not changed, use .png
    if args.create_texture and args.output_path == Path("./output.avi"):
        args.output_path = Path("./output.png")

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
