#!/usr/bin/env python

from math import ceil
import numpy as np
from contextlib import contextmanager

import cv2

from ImageSource import ImageSource
from ScriptParser import ScriptParser


class Animator:

    def __init__(self, args):
        self.args = args
        self.script_parser = ScriptParser(args)
        self.image_source = ImageSource(args)
        self.codec = cv2.VideoWriter_fourcc(*args.codec)

    def parse_script(self):

        temporal_dict = self.script_parser.parse_script()

        if len(temporal_dict) == 0:
            raise ValueError("Script contains no state")
        
        self.temporal_dict = temporal_dict

        if self.args.print_states:
            temporal_dict.print()

        return self

    def animate(self):

        if self.args.create_texture:
            self.create_texture()
        else:
            self.create_video()

        return self

    def create_texture(self):
        if self.args.verbose:
            print("Collecting frames")

        image_list = list(self.frames)

        if self.args.verbose:
            print(f"Creating texture from {len(image_list)} frames")

        texture = self.stitch_images(image_list)

        self.save_texture(texture)

    def save_texture(self, texture):
        #Defaults to saving texture in full resolution
        if self.args.texture_dimensions is None:

            if self.args.verbose:
                print("Saving full resolution texture")

            cv2.imwrite(str(self.args.output_path), texture)
            return

        #Otherwise we pull out path information to give each produced texture a proper filename
        original_path = self.args.output_path
        stem = str(original_path.stem)
        suffix = str(original_path.suffix)

        for width, height in self.args.texture_dimensions:

            if self.args.verbose:
                print(f"Saving {width}x{height} texture")

            new_path = str(original_path.with_name(f"{stem}_{width}x{height}{suffix}"))

            resized = cv2.resize(texture, (width, height), interpolation = cv2.INTER_AREA)#TODO: make interpolation a CL argument

            cv2.imwrite(new_path, resized)

    def create_video(self):
        if self.args.verbose:
            print("Writing frames to video")

        with self.video_writer as video:
            for frame in self.frames:
                video.write(frame)

    @property
    @contextmanager
    def video_writer(self):
        frame = next(self.frames)
        height, width, layers = frame.shape

        writer = cv2.VideoWriter(str(self.args.output_path), self.codec, self.args.fps, (width, height))

        try:
            yield writer
        finally:
            cv2.destroyAllWindows()
            writer.release()

    @property
    def frames(self):
        for state in self.temporal_dict.states:
            yield self.image_source.get_image(state)

    def stitch_images(self, images):
        image_matrix = self.get_image_matrix(images)
        return cv2.vconcat([cv2.hconcat(rows) for rows in image_matrix])

    def get_image_matrix(self, images):
        n = len(images)
        layout = self.args.texture_layout

        if layout == "square":
            width = ceil(n ** 0.5)
            height = ceil(n / width)
        elif layout == "horizontal":
            width = n
            height = 1
        elif layout == "vertical":
            width = 1
            height = n

        if n != width * height:
            images = self.pad_with_blank(images, width, height)

        return [images[i:i+width] for i in range(0, n, width)]

    def pad_with_blank(self, images, width, height):
        image_height, image_width, _ = images[0].shape
        blank_image = np.zeros((image_height,image_width,3), np.uint8)

        padding = [blank_image] * ((width * height) - len(images))

        return images + padding
