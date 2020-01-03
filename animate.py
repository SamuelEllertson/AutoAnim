#!/usr/bin/env python

from enum import Enum
import cv2
import os
from functools import lru_cache
import re
from collections import defaultdict
from pprint import pprint

image_folder = 'D:/gifs'
video_name = 'gif2.avi'

class State:

    def __init__(self, duration, options, previous_state):
                
        self.duration = duration

        if isinstance(previous_state, dict):
            self.data = previous_state.copy()

        else:
            data = previous_state.data.copy()
            data.update(self.strings_to_dict(options))

            self.data = data

    def __repr__(self):
        return f"State(duration={self.duration}, options={self.data!r})"

    def __hash__(self):
        return hash(frozenset(self.data.items()))

    def strings_to_dict(self, options):

        new_dict = dict()

        if options is None:
            return new_dict

        #List of options strings not necessarily consistent, so concat then split first.
        option_pairs = ",".join(options).split(",")

        for pair in option_pairs:
            key, value = pair.split(":")

            new_dict[key.strip()] = value.strip()

        return new_dict

    def add_options(self, options):

        if isinstance(options, str):
            options = [options]

        self.data.update(self.strings_to_dict(options))

def make_video(fps, filenames):

    print("Creating Video")

    frame = get_frame(filenames[0])
    height, width, layers = frame.shape
    video = cv2.VideoWriter(video_name, 0, fps, (width,height))
    
    for filename in filenames:
        frame = get_frame(filename)
        video.write(frame)

    cv2.destroyAllWindows()
    video.release()

@lru_cache
def get_frame(filename):
    frame = cv2.imread(os.path.join(image_folder, filename))

    if frame is None:
        print(filename)
        raise ValueError("Bad filepath: Check your keys")

    return frame

def get_filename(state):

    filename_parts = []

    for key, value in state.data.items():
        filename_parts.append(f"{key}{value}")

    filename_parts.append(".png")

    return "".join(filename_parts)

def get_filename_list(states, fps):
    filenames = []

    for state in states:
        filename = get_filename(state)

        for _ in range(max(1, int(fps * state.duration/1000))):
            filenames.append(filename)

    return filenames

def parse_script(filename):

    with open(filename, "r") as script:
        dirty_lines = list(script)

    clean_lines = clean_script(dirty_lines)

    state_lines, directives = extract_metadata(clean_lines)


    fps = directives["fps"]
    keys = directives["keys"]

    states = get_states(keys, state_lines)

    for state in states:
        print(state)

    #if they specify no keys or state -> dont bother doing anything
    if keys == [""] or len(states) == 0:
        return

    if None in states[0].data.values():
        raise ValueError("Failed to define initial values for all keys.")

    filenames = get_filename_list(states, fps)

    make_video(fps, filenames)

def get_states(keys, lines):

    #Add fake loop and end declarations so that the script is consistent with recursion
    lines.append("}")

    line_iter = iter(lines)

    #done to make the dictionary so that key order is preserved as we make new states
    default_model = State(None, None, {key: None for key in keys})

    return get_states_recurse(line_iter, default_model)

def get_states_recurse(line_iter, previous_state, loop=1):

    states = []

    current_state = None

    for line in line_iter:

        #Case: Starting a new loop -> End current_state -> Call recursively to get list of states, and update states and previous_state
        if line.startswith("loop:"):

            if current_state is not None:
                states.append(current_state)
                previous_state = current_state
                current_state = None

            times_to_loop = int(line[len("loop:"):].strip(": {"))

            new_states = get_states_recurse(line_iter, previous_state, loop=times_to_loop)

            previous_state = new_states[-1]

            states.extend(new_states)

        #Case: Reached end of this loop -> Finish current state if it exists -> Return the current list of states
        elif line == "}":
            if current_state is not None:
                states.append(current_state)

            return states * loop

        #Case: Reached a number == New state declaration -> push current_state if it exists -> update previous_state -> create new state
        elif line.isnumeric():

            duration = int(line)

            if current_state is not None:
                states.append(current_state)
                previous_state = current_state

            current_state = State(duration, None, previous_state)

        #Case: Reached other text == These are options for the current state
        else:
            #reaching here with no current state means they created a loop without starting a new state -> not allowed
            if current_state is None:
                raise ValueError("Loops must contain at least one state definition")

            current_state.add_options(line)

    #Since we add an 'end' to the line stream artificially, we should never not return on the 'end' case above
    assert False

class Modes(Enum):
    NORMAL = 1
    DEFINING = 2

def extract_metadata(lines):

    #dict that will contain all directives. Starts with defaults
    directives = defaultdict(list)
    directives["fps"] = 24

    #The current parsing mode
    mode = Modes.NORMAL

    #keeps track of key of current define
    current_define = None

    while True:

        #We will iteratively build up a list of partially parsed lines. We will keep parsing it until there are no directives left.
        new_lines = []

        directive_found = False
        loop_level = 0

        for line in lines:

            #various flags
            is_directive = line.find("@") != -1

            is_define = line.startswith("@def")
            is_inline_define = is_define and not (line.find("{") != -1)
            is_multiline_define = is_define and not is_inline_define
            
            is_substitution = is_directive and not is_define
            is_standard_substitution = is_substitution and line[0] == "@" and line[1:].replace("_", "").isalnum()
            is_inline_substitution = is_substitution and not is_standard_substitution

            is_start_block = line.find("{") != -1   
            is_end_block = line.strip() == "}"

            if is_start_block:
                loop_level += 1

            if is_end_block:
                loop_level -= 1

            is_end_define = is_end_block and loop_level <= 0

            #simple validation -> all directives are either a define or substitution
            if is_directive and not is_define and not is_substitution:
                raise ValueError(f"Invalid directive: {line}")

            #current line is a directive -> set flag
            if is_directive:
                directive_found = True
            
            #BEGIN MAIN SWITCH
            if mode == Modes.NORMAL:

                #Case: Not a directive -> simple append
                if not is_directive:
                    new_lines.append(line)

                elif is_define:

                    #Case: inline define -> extract values and continue on in normal mode
                    if is_inline_define:
                        key, value = get_define_values(line, is_inline=True)
                        directives[key] = value

                    #Case: multiline define -> set current_define and swap to define mode
                    elif is_multiline_define:
                        current_define = get_define_values(line, is_inline=False)
                        mode = Modes.DEFINING

                    else:
                        assert False
        
                elif is_substitution:
                    
                    sub_key = get_sub_name(line)


                    if sub_key not in directives:
                        raise KeyError(f"substitution directive '{sub_key}' not defined")

                    sub_value = directives[sub_key]

                    #Case: inline substitution in normal mode -> append the line with given substituion made
                    if is_inline_substitution:

                        if not isinstance(sub_value, str):
                            raise ValueError("Can not inline substitute a multiline define")

                        new_line = sub_inline(line, sub_key, sub_value)

                        new_lines.append(new_line)

                    #Case: standard substitution in normal mode -> add substitution lines to new_lines
                    elif is_standard_substitution:

                        #if only a single lines -> convert to list with 1 value for consistency
                        if isinstance(sub_value, str):
                            sub_value = [sub_value]

                        for sub_line in sub_value:
                            new_lines.append(sub_line)

                    else:
                        assert False

                else:
                    assert False

            elif mode == Modes.DEFINING:
                
                #Case: is a define -> not allowed
                if is_define:
                    raise ValueError("Can not nest defines")
                
                #return to normal mode when we encounter the end define signal
                elif is_end_define:
                    mode = Modes.NORMAL

                else:
                    #Otherwise just append the line to the current directive being defined
                    directives[current_define].append(line)
            else:
                assert False

        #Swap out the old lines for the partially parsed lines
        lines = new_lines

        #We are done parsing when we have looped through all lines and not found any more directives
        if not directive_found:
            break

    if "keys" not in directives:
        raise ValueError("Given script does not define keys.")


    #convert keys string to proper list
    directives["keys"] = directives["keys"].split(",")

    #ensure fps remains an int
    directives["fps"] = int(directives["fps"])

    return lines, directives

def get_sub_name(line):
    regex = r"\@([\w\_]+)"
    return re.search(regex, line).group(1).strip()

def sub_inline(line, key, value):
    regex = f"@{key}"
    return re.sub(regex, value, line).strip()

def get_define_values(line, is_inline):
    parts = line.split(" ")

    if is_inline:
        return parts[1], "".join(parts[2:])

    #multiline define -> return just name without '{'
    return parts[1].strip("{ ").strip()

def clean_script(lines):
    clean = []

    for line in lines:
        temp = line.partition("#")[0].lower().strip()

        if temp != "":
            clean.append(temp)

    return clean

parse_script("script.txt")