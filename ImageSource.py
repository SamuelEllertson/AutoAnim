#!/usr/bin/env python

from psd_tools import PSDImage
from psd_tools.api.layers import Group, Layer
import numpy as np

from pprint import pprint
from functools import lru_cache
import os
from pathlib import Path
from itertools import chain
from operator import attrgetter


class ImageSource:

    extension_to_glob = ["py", "avi"]


    def __init__(self, psd_path=None, directory=None, store_new=True):
        self.psd_path = Path(psd_path) if psd_path is not None else None
        self.directory = Path(directory) if directory is not None else None
        self.store_new = store_new

        self.directory_contents = None
        self.psd = None

        if self.psd_path is None and self.directory is None:
            raise TypeError(f"{self.__class__.__name__} requires either a psd filepath or a directory.")

        if self.psd_path is not None:
            self.psd = PSDImage.open(self.psd_path)

        if self.directory is not None:
            self.directory_contents = set(path.name for extension in self.extension_to_glob for path in self.directory.glob(f"*.{extension}"))

    @lru_cache
    def get_image(self, state):
        
        if 
        


ImageSource(psd_path="./anim.psd", directory=".")





psd = PSDImage.open('anim.psd')

#print(psd)
#pprint(dir(psd))

#for layer in psd.descendants():
#    print(layer)

#pprint(a)






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
    #frame = cv2.imread(os.path.join(image_folder, filename))

    return cv2.cvtColor(np.array(PILImage), cv2.COLOR_RGB2BGR)

    if frame is None:
        print(filename)
        raise ValueError("Bad filepath: Check your keys")

    return frame