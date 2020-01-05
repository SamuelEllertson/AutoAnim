#!/usr/bin/env python

from pathlib import Path
import sys

from Animator import Animator
from my_utils.args import parseArgs



def main():
    args = getArgs()

    animator = Animator(**args.__dict__)
    animator.parse_script(print_states=args.print_states)

    if not args.skip_video:
        animator.animate()

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
    arg_minimum_frames = {
        "flags": ["--skip-short-frames"],
        "options": {
            "dest": "skip_short_frames",
            "action": "store_true",
            "help": "if set, states with a duration shorter than the minimum frame time defined by the fps will be skipped. Default behavior is that all states get a minimum of one frame"
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
    arg_skip_video = {
        "flags": ["--skip-video"],
        "options": {
            "dest": "skip_video",
            "action": "store_true",
            "help": "Video file will not be created"
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
            arg_codec,
            arg_verbose,
            arg_minimum_frames,
            arg_print_states,
            arg_skip_video,
            arg_store_new
        ]
    }

    args = parseArgs(parserSetup)

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
