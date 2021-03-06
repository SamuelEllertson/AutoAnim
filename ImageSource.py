#!/usr/bin/env python

from psd_tools import PSDImage, compose
import numpy as np
import cv2

from functools import cached_property, lru_cache, partial

from multiprocessing.pool import Pool as ProcessPool
from concurrent.futures import ThreadPoolExecutor as ThreadPool

import signal

def ignore_signal():
    """Ignore CTRL+C in the worker process."""

    signal.signal(signal.SIGINT, signal.SIG_IGN)

class ImageSource:

    ignore_character = "__"

    def __init__(self, args):
        self.args = args
        self.psd = PSDImage.open(args.psd_path) if args.psd_path is not None else None
        self.default_layers = set()

    def current_directory_contents(self):
        return set(file.name for file in self.args.directory.glob("*.png"))

    @cached_property
    def psd_groups(self):
        '''Creates a mapping from group names to layer names to layers: group_name -> (layer_name -> layer)'''

        psd_groups = {}

        for group in self.psd:
            
            #top level layers are not controllable, but are important if visible
            if not group.is_group():
                if group.is_visible():
                    self.default_layers.add(group)
                continue

            #ignored groups are not controllable, but layers are important if visible
            if group.name.startswith(self.ignore_character):
                for layer in group:
                    if layer.is_visible():
                        self.default_layers.add(layer)
                continue

            #get canonical groupname and layer names
            groupname = group.name.lower().strip()
            group_options = {layer.name.lower().strip(): layer for layer in group if not layer.name.startswith(self.ignore_character)}

            psd_groups[groupname] = group_options

        return psd_groups

    def create_frames(self, states):

        self.validate_states(states)

        states_to_be_created = self.get_nonexistent_states(states)

        if len(states_to_be_created) != 0 and self.psd is None:
            raise RuntimeError("Need to generate states but no psd file supplied.")
    
        #ProcessPool for CPU bound image creation, ThreadPool for IO bound file saving
        with ProcessPool(initializer=ignore_signal) as process_pool, ThreadPool() as thread_pool:
            try:
                for image, state in process_pool.imap_unordered(self.generate_image, states_to_be_created):
                    save_image = partial(image.save, self.args.directory / state.filename)
                    thread_pool.submit(save_image)
            except KeyboardInterrupt:
                process_pool.terminate()
                thread_pool.shutdown(wait=False)

                raise KeyboardInterrupt from None

    def validate_states(self, states):
        for state in states:
            state.validate(self.psd_groups)

    def get_nonexistent_states(self, states):
        current_files = self.current_directory_contents()
        needed_states = (state for state in states if state.filename not in current_files)
        required = list(dict.fromkeys(needed_states)) #removes duplicates, keep order

        return required

    @lru_cache
    def get_image(self, state):

        state.validate(self.psd_groups)

        #First check if it already exists in the directory if it was given
        if state.filename in self.current_directory_contents():

            if self.args.verbose:
                print("Found cached image")

            return cv2.imread(str(self.args.directory / state.filename))

        #otherwise we revert to using the psd file
        image, _ = self.generate_image(state)

        return self.convert_to_cv_image(image)

    def convert_to_cv_image(self, pil_image):
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    def generate_image(self, state):

        if self.args.verbose:
            print("Generating new image")
        
        wanted_layers = set(self.psd_groups[option][value] for option, value in state) | self.default_layers
        pil_image = compose(list(self.psd.descendants()), layer_filter=wanted_layers.__contains__, bbox=self.psd.viewbox)

        return pil_image, state
