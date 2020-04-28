import pygame
import threading
import os
import json
import typing


class Asset:
    pass


class AssetManager:
    def __init__(self, root: str):
        self.__root = root
        self.__loaded_files = 0
        self.__files = []
        self.__exts = []

    def __load(self):
        for fname in self.__files:
            self.__load_file(fname)
            self.__loaded_files = self.__loaded_files + 1

    def __load_file(self, fname):
        # Assets are looked up via their name but that name does not include the file
        # extension.
        n = os.path.splitext(fname)[0]
        # Individual assets are loaded based on their file type.
        ext = os.path.splitext(fname)[1]

    def set_root(self, root: str):
        self.__root = root

    def start(self, preload: typing.List[str], root: str = None):
        if root is not None:
            self.__root = root
        # Find all the files in our asset folder that we can load.
        for dname, dpath, files in os.walk(self.__root):
            for fname in files:
                # Only preload files that have a compatible file extension. This
                # will remember all the files that we have to load and they will
                # later be loaded by the multi-threaded asset loader.
                if os.path.splitext(fname)[1] in self.__exts:
                    self.__files.append(fname)
        # Usually the game will have some sort of loading screen which means that a few assets will need to be
        # loaded right away and not in a background thread. We can take care of that by having a list of assets
        # to load on the main thread rather than in the background.
        for fname in preload:
            self.__load_file(fname)
        threading.Thread(target=self.__load).start()

    def is_finished(self) -> bool:
        return len(self.__files) == self.__loaded_files

    def get_progress(self) -> float:
        return self.__loaded_files / len(self.__files)
