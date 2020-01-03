
from enum import Enum
import re
from collections import defaultdict

from State import State

class Modes(Enum):
    NORMAL = 1
    DEFINING = 2

class ScriptParser:

    def __init__(self, script_path):
        self.script_path = script_path

    def parse_script(self):

        with open(self.script_path, "r") as script:
            dirty_lines = list(script)

        clean_lines = self.clean_script(dirty_lines)

        state_lines, directives = self.extract_metadata(clean_lines)

        states = self.get_states(state_lines)

        return states, directives

        #if they specify no keys or state or to supress video -> dont bother doing anything
        if self.keys == [""] or len(states) == 0 or self.supress_video:###
            return

        if None in states[0].data.values():###
            raise ValueError("Failed to define initial values for all keys.")

        #self.make_video(self.fps, filenames) ###

    def get_states(self, lines):

        #Add fake end declaration so that the script is consistent with recursion
        lines.append("}")

        line_iter = iter(lines)

        return self.get_states_recurse(line_iter)

    def get_states_recurse(self, line_iter, previous_state=None, loop=1):

        if previous_state is None:
            previous_state = State()

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

                new_states = self.get_states_recurse(line_iter, previous_state, loop=times_to_loop)

                previous_state = new_states[-1]

                states.extend(new_states)

            #Case: Reached end of this loop -> Finish current state if it exists -> Return the current list of states
            elif line == "}":
                if current_state is not None:
                    states.append(current_state)

                return states * loop

            #Case: Reached a number == New state declaration -> push current_state if it exists -> update previous_state -> create new state
            elif line.isnumeric():

                duration = int(line) / 1000

                if current_state is not None:
                    states.append(current_state)
                    previous_state = current_state

                current_state = State(duration, data=previous_state)

            #Case: Reached other text == These are options for the current state
            else:
                #reaching here with no current state means they created a loop without starting a new state -> not allowed
                if current_state is None:
                    raise ValueError("Loops must contain at least one state definition")

                current_state.add_options(line)

        #Since we add an 'end' to the line stream artificially, we should never not return on the 'end' case above
        assert False

    def extract_metadata(self, lines):

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
                            key, value = self.get_define_values(line, is_inline=True)
                            directives[key] = value

                        #Case: multiline define -> set current_define and swap to define mode
                        elif is_multiline_define:
                            current_define = self.get_define_values(line, is_inline=False)
                            mode = Modes.DEFINING

                        else:
                            assert False
            
                    elif is_substitution:
                        
                        sub_key = self.get_sub_name(line)

                        if sub_key not in directives:
                            raise KeyError(f"substitution directive '{sub_key}' not defined")

                        sub_value = directives[sub_key]

                        #Case: inline substitution in normal mode -> append the line with given substituion made
                        if is_inline_substitution:

                            if not isinstance(sub_value, str):
                                raise ValueError("Can not inline substitute a multiline define")

                            new_line = self.sub_inline(line, sub_key, sub_value)

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

        #ensure fps remains an int
        directives["fps"] = int(directives["fps"])

        return lines, directives

    def get_sub_name(self, line):
        regex = r"\@([\w\_]+)"
        return re.search(regex, line).group(1).strip()

    def sub_inline(self, line, key, value):
        regex = f"@{key}"
        return re.sub(regex, value, line).strip()

    def get_define_values(self, line, is_inline):
        parts = line.split(" ")

        if is_inline:
            return parts[1], "".join(parts[2:])

        #multiline define -> return just name without '{'
        return parts[1].strip("{ ").strip()

    def clean_script(self, lines):
        clean = []

        for line in lines:
            temp = line.partition("#")[0].lower().strip()

            if temp != "":
                clean.append(temp)

        return clean