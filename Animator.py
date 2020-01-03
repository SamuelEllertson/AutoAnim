#!/usr/bin/env python

from pathlib import Path
from contextlib import contextmanager

import cv2

from ImageSource import ImageSource
from ScriptParser import ScriptParser

class Animator:

    def __init__(self, script_path, output_path, psd_path=None, directory=None, store_new=True, **directives):
        self.script_parser = ScriptParser(script_path=script_path)
        self.output_path = Path(output_path)
        self.image_source = ImageSource(psd_path=psd_path, directory=directory, store_new=store_new)
        self.directives = {"fps": 8, **directives}

        self.parse_script()

    @property
    def fps(self):
        return self.directives["fps"]

    def parse_script(self):
        states, directives = self.script_parser.parse_script()

        if len(states) == 0:
            raise ValueError("Script contains no state")

        if directives.get("print_states", False):
            for state in states:
                print(state)

        self.states = states
        self.directives.update(directives)

    def animate(self):

        with self.video_writer as video:
            for frame in self.frames:
                video.write(frame)

    @property
    @contextmanager
    def video_writer(self):
        frame = next(self.frames)
        height, width, layers = frame.shape

        try:
            codec = cv2.VideoWriter_fourcc(*"mp4v")
            codec = 0
        except:
            print("Bad Codec")
            codec = 0

        writer = cv2.VideoWriter(str(self.output_path), codec, self.fps, (width, height))

        try:
            yield writer
        finally:
            cv2.destroyAllWindows()
            writer.release()

    @property
    def frames(self):
        for state in self.states:
            frame = self.image_source.get_image(state)

            for _ in range(max(1, int(self.fps * state.duration))):
                yield frame
