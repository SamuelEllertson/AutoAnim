#!/usr/bin/env python

from psd_tools import PSDImage
import numpy as np
import cv2

from functools import cached_property, lru_cache


class ImageSource:

    ignore_character = "__"

    def __init__(self, args):
        self.args = args
        self.directory_contents = set(file.name for file in args.directory.glob("*.png"))
        self.psd = PSDImage.open(args.psd_path) if args.psd_path is not None else None

    @cached_property
    def psd_groups(self):
        '''Creates a mapping from group names to layer names to layers: group_name -> (layer_name -> layer)'''

        psd_groups = {}

        for group in self.psd:
            
            #ignore top level layers
            if not group.is_group():
                continue

            #ignore anything starting with specified ignore character
            if group.name.startswith(self.ignore_character):
                continue

            #get canonical groupname and layer names
            groupname = group.name.lower().strip()
            group_options = {layer.name.lower().strip(): layer for layer in group if not layer.name.startswith(self.ignore_character)}

            psd_groups[groupname] = group_options

        return psd_groups

    @lru_cache
    def get_image(self, state):

        #First check if it already exists in the directory if it was given
        if state.filename in self.directory_contents:

            if self.args.verbose:
                print("Found cached image")

            return cv2.imread(str(self.args.directory / state.filename))

        if self.psd is None:
            raise RuntimeError("Unable to gather all images needed for animation")

        #otherwise we revert to using the psd file
        return self.generate_image_from_psd(state)


    def convert_to_cv_image(self, pil_image):
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    def set_psd_state(self, state):
        for option, value in state:

            #make all layers in the group invisible
            for layer in self.psd_groups[option].values():
                layer.visible = False

            #Then make the selected layer visible
            self.psd_groups[option][value].visible = True

    def generate_image_from_psd(self, state):

        #validate given state options
        state.validate(self.psd_groups)

        if self.args.verbose:
            print("Generating new image")

        #setup psd file for composing
        self.set_psd_state(state)

        #generate the image
        pil_image = self.psd.compose(force=True) #todo: make force optional because its slow, but makes certain effects work

        #save the image to the directory if specified
        if self.args.store_new:
            pil_image.save(self.args.directory / state.filename)
            self.directory_contents.add(state.filename)

        return self.convert_to_cv_image(pil_image)
