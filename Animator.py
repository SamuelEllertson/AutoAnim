#!/usr/bin/env python

from pathlib import Path
from contextlib import contextmanager

import cv2

from ImageSource import ImageSource
from ScriptParser import ScriptParser


class Animator:

    def __init__(self, script_path, output_path, psd_path=None, directory=None, store_new=True, fps=24, codec="mp4v", verbose=False, skip_short_frames=False, speed_multiplier=1.0, **kwargs):
        self.script_parser = ScriptParser(script_path=script_path)
        self.output_path = Path(output_path)
        self.image_source = ImageSource(psd_path=psd_path, directory=directory, store_new=store_new, verbose=verbose)
        self.fps = fps
        self.codec = cv2.VideoWriter_fourcc(*codec)
        self.verbose = verbose
        self.skip_short_frames = skip_short_frames
        self.speed_multiplier = speed_multiplier

    def parse_script(self, print_states=False):

        temporal_dict = self.script_parser.parse_script(self.verbose)

        if len(temporal_dict) == 0:
            raise ValueError("Script contains no state")
        
        self.temporal_dict = temporal_dict

        if print_states:
            for state in temporal_dict.states(self.speed_multiplier, self.fps):
                print(state) 

        return self

    def animate(self):

        if self.verbose:
            print("Creating video")

        with self.video_writer as video:
            for frame in self.frames:
                video.write(frame)

        return self

    @property
    @contextmanager
    def video_writer(self):
        frame = next(self.frames)
        height, width, layers = frame.shape

        writer = cv2.VideoWriter(str(self.output_path), self.codec, self.fps, (width, height))

        try:
            yield writer
        finally:
            cv2.destroyAllWindows()
            writer.release()

    @property
    def frames(self):
        for state in self.temporal_dict.states(self.speed_multiplier, self.fps):
            yield self.image_source.get_image(state_obj)