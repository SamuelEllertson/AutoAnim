#!/usr/bin/env python

from pathlib import Path
import sys

from Animator import Animator
from args import parseArgs

from argparse import ArgumentTypeError

def main(args):

    handle_image_cache(args)

    animator = Animator(args)
    animator.parse_script()

    if not args.no_output:
        animator.animate()

    if args.verbose:
        print("Finished")

def handle_image_cache(args):
    args.directory.mkdir(exist_ok=True)

    if args.clear_cache:

        if args.verbose:
            print("Clearing the image cache")

        for item in args.directory.iterdir():
            if item.is_file():
                item.unlink(missing_ok=True)

def getArgs():
    parserSetup = {
        "description": "Create animations programatically from a psd file.",
        "args": [
            {
                "flags": ["-s", "--script-path"],
                "options": {
                    "type": Path,
                    "required": True,
                    "metavar": "Path",
                    "dest": "script_path",
                    "help": "Path to animation script file"
                }
            },
            {
                "flags": ["-o", "--output-path"],
                "options": {
                    "default": None,
                    "type": Path,
                    "metavar": "Path",
                    "dest": "output_path",
                    "help": "Animation output path (default: output.avi for video, output.png for textures)"
                }
            },
            {
                "flags": ["-p", "--psd-path"],
                "options": {
                    "default": None,
                    "type": Path,
                    "metavar": "Path",
                    "dest": "psd_path",
                    "help": "Path to psd file that will be used to generate images"
                }
            },
            {
                "flags": ["-i", "--image-cache"],
                "options": {
                    "default": Path("./image_cache"),
                    "type": Path,
                    "metavar": "Path",
                    "dest": "directory",
                    "help": "Path to the image cache (defaults to ./image_cache)"
                }
            },
            {
                "flags": ["--clear-cache"],
                "options": {
                    "dest": "clear_cache",
                    "action": "store_true",
                    "help": "Clears the image cache"
                }
            },
            {
                "flags": ["--fps"],
                "options": {
                    "dest": "fps",
                    "type": int,
                    "default": 24,
                    "metavar": "int",
                    "help": "Sets the output frames per second (default: 24)"
                }
            },
            {
                "flags": ["--speed"],
                "options": {
                    "dest": "speed_multiplier",
                    "type": float,
                    "default": 1.0,
                    "metavar": "float",
                    "help": "Set the speed multiplier for the output (default: 1.0)"
                }
            },
            {
                "flags": ["--codec"],
                "options": {
                    "dest": "codec",
                    "type": str,
                    "default": "mp4v",
                    "metavar": "codec",
                    "help": "Sets the codec used when generating output video (default: mp4v)"
                }
            },
            {
                "flags": ["--dont-store"],
                "options": {
                    "dest": "store_new",
                    "action": "store_false",
                    "help": "If set newly generated images will not be stored to the image directory"
                }
            },
            {
                "flags": ["-v", "--verbose"],
                "options": {
                    "dest": "verbose",
                    "action": "store_true",
                    "help": "Enable verbose output"
                }
            },
            {
                "flags": ["--print-states"],
                "options": {
                    "dest": "print_states",
                    "action": "store_true",
                    "help": "Print the full list of parsed states"
                }
            },
            {
                "flags": ["--no-output"],
                "options": {
                    "dest": "no_output",
                    "action": "store_true",
                    "help": "Script will be parsed, but no output will be created"
                }
            },
            {
                "flags": ["-t", "--create-texture"],
                "options": {
                    "dest": "create_texture",
                    "action": "store_true",
                    "help": "Instead of a video file, output animation as a tiled texture image"
                }
            },
            {
                "flags": ["--texture-layout"],
                "options": {
                    "dest": "texture_layout",
                    "default":"square",
                    "choices":("square", "horizontal", "vertical"),
                    "help": "Sets texture image layout (default: square)"
                }
            }
        ]
    }

    args = parseArgs(parserSetup)

    if args.speed_multiplier <= 0:
        raise ArgumentTypeError("speed-multiplier must be a positive value")

    #Use the given output path, or default to output.{avi, png} depending on if we are creating a texture or video
    if args.output_path is None:
        args.output_path = Path("./output.png") if args.create_texture else Path("./output.avi")

    return args

if __name__ == '__main__':
    
    DEBUG = True

    args = getArgs()

    if DEBUG:
        main(args)
        exit()

    try:
        main(args)
    except Exception as e:
        print(f"AutoAnim: an error occured: {e}", file=sys.stderr)
