#!/usr/bin/env python

from psd_tools import PSDImage
import numpy as np
import cv2

from pathlib import Path

class ImageSource:

    extension_to_glob = ["png"]
    extension_to_save_as = "png"
    ignore_character = "__"
    default_dir = Path("./image_cache")

    def __init__(self, psd_path=None, directory=None, store_new=True, verbose=False):
        self.psd_path = Path(psd_path) if psd_path is not None else None
        self.directory = Path(directory) if directory is not None else self.default_dir if self.default_dir.exists() else None
        self.store_new = store_new
        self.verbose = verbose
        self.directory_contents = set(path.name for extension in self.extension_to_glob for path in self.directory.glob(f"*.{extension}"))
        self.cache = {}

        if self.psd_path is None and self.directory is None:
            raise TypeError(f"{self.__class__.__name__} requires either a psd filepath or a directory.")

    @property
    def psd(self):
        '''We lazily open the psd file, and cache it for use later'''

        if hasattr(self, "_psd"):
            return self._psd

        if self.psd_path is None:
            return None

        self._psd = PSDImage.open(self.psd_path)

        return self._psd

    @property
    def psd_groups(self):
        '''We lazily store the psd_groups and cache it for use later'''

        if hasattr(self, "_psd_groups"):
            return self._psd_groups

        psd_groups = {}

        for group in self.psd:
            
            #ignore top level layers
            if not group.is_group():
                continue

            #ignore anything starting with '__'
            if group.name.startswith(self.ignore_character):
                continue

            #get canonical groupname and layer names
            groupname = group.name.lower().strip()
            group_options = {layer.name.lower().strip(): layer for layer in group if not layer.name.startswith(self.ignore_character)}

            psd_groups[groupname] = group_options

        self._psd_groups = psd_groups

        return psd_groups

    def get_image(self, state):
        hash_val = hash(state)

        if hash_val in self.cache:
            if self.verbose:
                print("Found Cached Image")
                
            return self.cache[hash_val]

        image = self._get_image(state)
        self.cache[hash_val] = image
        return image

    def _get_image(self, state):

        #First check if it already exists in the directive if it was given
        if state.filename in self.directory_contents:

            if self.verbose:
                print("Found Image")

            return cv2.imread(str(self.directory / state.filename))

        if self.psd is None:
            raise RuntimeError("Unable to gather all images needed for animation")

        #otherwise we revert to using the psd file
        return self.generate_image_from_psd(state)


    def convert_to_cv_image(self, pil_image):
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    def generate_image_from_psd(self, state):

        if self.verbose:
                print("Generating new image")

        #validate given state options
        for key, value in state.data.items():
            if key not in self.psd_groups:
                raise KeyError(f"Received invalid key value: {key}:{value}")

            if value not in self.psd_groups[key]:
                raise ValueError(f"Received invalid option value: {key}:{value}")

            undefined_keys = set(self.psd_groups.keys()) - set(state.data.keys())

            if len(undefined_keys) != 0:
                raise ValueError(f"All keys must be defined. Currently missing: {undefined_keys!r}")

        #setup psd file for composing
        for key, value in state.data.items():

            #make all layers in the group invisible
            for layer in self.psd_groups[key].values():
                layer.visible = False

            #Then make the selected layer visible
            self.psd_groups[key][value].visible = True

        #generate the image
        pil_image = self.psd.compose(force=True)

        #save the image to the directory if specified
        if self.store_new:
            directory = self.directory or self.default_dir
            directory.mkdir(exist_ok=True)
            pil_image.save(directory / state.filename)
            self.directory_contents.add(state.filename)

        return self.convert_to_cv_image(pil_image)
