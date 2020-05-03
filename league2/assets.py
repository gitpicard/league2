import pygame
import threading
import os
import json
import typing
import pathlib


class TileSheet:
    """
    A tile-sheet is a grid of tiles that are stored on a single surface rather than having a
    surface for each tile. This improves memory usage and loading times as only a single file
    needs to be processed. A tile-sheet has the tiles in a grid, if you want to pack the surfaces
    differently use a sprite-sheet.
    """
    def __init__(self, surface: pygame.Surface, rows: int, cols: int):
        """
        Create a new tile-sheet from a pygame surface. The size of each tile will be calculated
        automatically from the number of rows and columns.
        :param surface: The surface containing the tile data.
        :param rows: The number of rows on the sheet.
        :param cols: The number of tiles on the sheet.
        """
        self.__surface = surface
        self.__rows = rows
        self.__cols = cols
        self.__cell_width = surface.get_width() / cols
        self.__cell_height = surface.get_height() / rows

    def get_max_rows(self) -> int:
        """
        How many rows are there on this sheet?
        :return: The number of rows as an integer.
        """
        return self.__rows

    def get_max_columns(self) -> int:
        """
        How many columns are there on this sheet?
        :return: The number of columns as an integer.
        """
        return self.__cols

    def get_tile(self, row, column) -> pygame.Surface:
        """
        Get a specific tile on the sheet. The surface returned will not be a copy but a sub-surface of
        the tile-sheet. This means that if the tile-sheet changes, this tile will also change since it
        shares pixel data.
        :param row: The row (starting at zero) to look at.
        :param column: The column (starting at zero) to look at.
        :return: The tile as a pygame sub-surface.
        """
        x = column * self.__cell_width
        y = row * self.__cell_height
        return self.__surface.subsurface((x, y, self.__cell_width, self.__cell_height))


class SpriteSheet:
    pass


class AssetManager:
    """
    The asset manager acts as a universal asset cache. It is used to load assets before they are needed
    and keep a reference to them so that they can be accessed later without having to load them again. It
    is multi-threaded meaning that assets will load while the game is still running. This allows for a smoother
    game experience.

    Assets are looked up via their name (without file extension) and with a path relative to the root folder. So a file
    at C:/Program Files (x86)/My Game/assets/sprites/player.png would be called sprites/player.
    """
    def __init__(self, root: str):
        """
        Create a new asset manager that will load from the passed in directory.
        :param root: The directory that will be searched for assets.
        """
        self.__root = root
        self.__finished = True
        self.__loaded_files = 0
        self.__files = []
        self.__cached_files = []
        self.__image_exts = ['.png', '.jpg', '.jpeg', '.bmp']
        self.__exts = self.__image_exts
        self.__surfaces = {}
        self.__tilesheets = {}

    def __load(self):
        # This wait call is awful but it is needed because if we are starting to load and we just switched to
        # fullscreen, we need to give the operating system some time to reset the display mode. It is simply a
        # consequence of using a multi-threaded asset system. The delay is very short and happening on a separate
        # thread so the game can keep running.
        pygame.time.wait(100)

        for fname in self.__files:
            self.__load_file(fname)
            self.__loaded_files += 1
        # Finished loading!
        self.__files.clear()
        self.__finished = True

    def __fill_defaults(self, ext):
        # Base on the passed in file extension, we will try and guess the correct settings
        # that the asset needs. The settings can be overridden by a JSON file in the same directory
        # with the same name as the asset.
        if ext in self.__image_exts:
            return {
                'type': 'sprite',
                'alpha': 'True'
            }

    def __load_file(self, fname):
        # Some files may already have been loaded during preloading so make sure that
        # we don't load them again now.
        if fname in self.__cached_files:
            return
        # Assets are looked up via their name but that name does not include the file
        # extension. The name is also relative to the base asset directory.
        n = os.path.splitext(pathlib.Path(fname).relative_to(self.__root))[0]
        # Individual assets are loaded based on their file type.
        ext = os.path.splitext(fname)[1]

        # Make sure to use a cross-platform name with cross-platform separators.
        n = n.replace('\\', '/')

        self.__cached_files.append(fname)

        # Look for a JSON file that will contain asset settings. JSON files are only needed if an asset
        # should be loaded with special settings.
        data = self.__fill_defaults(ext)
        if os.path.isfile(os.path.splitext(fname)[0] + '.json'):
            json_file = open(os.path.splitext(fname)[0] + '.json', 'r')
            data = json.loads(json_file.read())
            json_file.close()
        # Based on the asset type, load it correctly.
        if data['type'] == 'sprite':
            self.__surfaces[n] = pygame.image.load(fname)
            # Each surface can have transparency enabled or disabled.
            if data['alpha']:
                self.__surfaces[n] = self.__surfaces[n].convert_alpha()
            else:
                self.__surfaces[n] = self.__surfaces[n].convert()
                self.__surfaces[n].set_alpha(None)
        elif data['type'] == 'tilesheet':
            image = pygame.image.load(fname)
            # Like all visuals in league, transparency can be disabled for performance and often will
            # be for tile-maps.
            if data['alpha']:
                image = image.convert_alpha()
            else:
                image = image.convert()
            self.__tilesheets[n] = TileSheet(image, data['rows'], data['columns'])
        else:
            raise IOError('Unidentified asset of type %s.' % data['type'])

    def set_root(self, root: str):
        self.__root = root

    def start(self, preload: typing.List[str], root: str = None):
        """
        Asynchronously load all the assets in the root folder. Since some assets are required right away and
        can't be loaded on a separate thread, a list of assets to load on the main thread can also be provided.
        Those assets will be available as soon as this method returns.
        :param preload: A list of assets to load right away.
        :param root: Optionally provide a new root folder for assets to be found in.
        """
        if not self.__finished:
            raise RuntimeError('Unable to start loading when a load is still in progress.')

        if root is not None:
            self.__root = root
        # Find all the files in our asset folder that we can load.
        for dname, dpath, files in os.walk(self.__root):
            for fname in files:
                # Only load files that have a compatible file extension. This
                # will remember all the files that we have to load and they will
                # later be loaded by the multi-threaded asset loader.
                if os.path.splitext(fname)[1] in self.__exts:
                    self.__files.append(os.path.join(dname, fname))
        # Usually the game will have some sort of loading screen which means that a few assets will need to be
        # loaded right away and not in a background thread. We can take care of that by having a list of assets
        # to load on the main thread rather than in the background.
        for fname in preload:
            self.__load_file(fname)
        self.__finished = False
        threading.Thread(target=self.__load).start()

    def is_finished(self) -> bool:
        """
        Is the asset loading thread finished loading?
        :return: True if no more assets are being loaded.
        """
        return self.__finished

    def get_progress(self) -> float:
        """
        Get the percentage of files loaded.
        :return: Returns 1 when complete and 0 if no files are loaded.
        """
        return self.__loaded_files / len(self.__files)

    def get_surface(self, name: str) -> pygame.Surface:
        """
        Find a single surface that was loaded. It will be cached so that there is
        only one instance of the surface.
        :param name: The name of the asset (without the extension).
        :return: The cached pygame surface.
        """
        return self.__surfaces[name]

    def get_tilesheet(self, name: str) -> TileSheet:
        """
        Find a tile-sheet that was automatically loaded.
        :param name: The name of the tile-sheet (without the extension).
        :return: The cached tile-sheet asset.
        """
        return self.__tilesheets[name]
