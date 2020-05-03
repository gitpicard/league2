import pygame
import os
import json
import appdirs
import league2.assets
import typing


def get_settings_path(app:  str, company: str) -> str:
    """
    Get a path where the game can store settings. This path will have both read and write permissions.
    :param app: The game's name.
    :param company: The name of the group that created the game.
    :return: A path that is guarantied to exist.
    """
    path = appdirs.user_config_dir(app, company)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def get_storage_path(app: str, company: str) -> str:
    """
    Get a path to where the game can write data. On some platforms, a game can't write to its own directory and
    must write to a special storage directory. This function will create or find that directory.
    :param app: The game's name.
    :param company: The name of the group that created the game.
    :return: A path that is guarantied to exist.
    """
    path = appdirs.user_data_dir(app, company)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def get_executing_path(code: str) -> str:
    """
    Get a path to the package in which the code file resides. Depending on the platform, you may not be
    able to write to this path.
    :param code: Pass in the __file__ special to get the folder.
    :return: A path that is guarantied to exist.
    """
    return os.path.dirname(os.path.realpath(code))


class Settings:
    """
    Configuration for both the game and for the engine. You can use this to set graphics, audio, and input
    options for the game. It is also possible to save custom settings provided that the data consists of primitive
    types such as integers, booleans, strings, etc. Note that some settings can change the game instantly and
    others will require a call to apply_settings() to be made.
    """
    def __init__(self, fname: typing.Optional[str] = None):
        """
        Create a new settings object. Optionally, you can provide a JSON file to load settings from. If the
        file does not exist, it will be created and default settings saved to it.
        :param fname: An optional JSON file to load settings from or create.
        """
        self.__title = 'Made with League 2'
        self.__fullscreen = False
        self.__resizable = True
        self.__game_size = (640, 480)
        self.__size = self.__game_size
        self.__native_size = pygame.display.Info().current_w, pygame.display.Info().current_h
        self.__fps = 40
        self.__asset_folder = '../assets'
        self.__preload_files = []
        self.__custom = {}

        # If there is no settings file then we will create one with the default settings.
        if fname is not None and not os.path.isfile(fname):
            self.save(fname)
        elif fname is not None:
            self.load(fname)

    def load(self, fname: str):
        """
        Load settings information from a JSON file. Not all the settings will take affect immediately and might
        require a call to apply_settings().
        :param fname: The JSON file to load.
        """
        f = open(fname, 'r')
        data = json.dumps(f.read())
        f.close()

        self.__title = data['title']
        self.__fullscreen = data['fullscreen']
        self.__game_size = data['size']
        self.__fps = data['fps']
        self.__asset_folder = data['assets']
        self.__preload_files = data['preload']
        self.__custom = data['custom']

    def save(self, fname: str):
        """
        Save the game and engine settings to a JSON file This file can be loaded again later. This allows
        the user to have persistent settings as they will expect a game to behave like they last left it.
        :param fname: The JSON file to load.
        """
        data = {
            'title': self.__title,
            'fullscreen': self.__fullscreen,
            'size': self.__game_size,
            'fps': self.__fps,
            'assets': self.__asset_folder,
            'preload': self.__preload_files,
            'custom': self.__custom
        }

        f = open(fname, 'w')
        f.write(json.dumps(data))
        f.close()

    def get_title(self) -> str:
        """
        Get the string to put in the game's window.
        :return: The string representing the title-bar text.
        """
        return self.__title

    def set_title(self, title: str):
        """
        Set the string that should be put in the title-bar text. Must call apply_settings() to change the
        actual game window.
        :param title: The title of the window.
        """
        self.__title = title

    def get_flags(self) -> int:
        """
        This will get the pygame display flags needed to support the requested settings. It is not
        a configurable setting but the result of other settings.
        :return: An integer that acts as a flag mask.
        """
        if self.__fullscreen:
            return pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE
        else:
            if self.__resizable:
                return pygame.RESIZABLE
            return 0

    def get_resizeable(self) -> bool:
        """
        Can the window be resized by the user? Allow allows the maximize button.
        :return: True if the window can be resized.
        """
        return self.__resizable

    def set_resizable(self, resizable: bool):
        """
        Allows the window to be resized by the user. On some Linux distributions and some
        versions of pygame, resizing does not work very well. If this is the case, update to
        pygame 2.0.0dev8 or later.
        :param resizable: True if the window can be resized.
        """
        self.__resizable = resizable

    def get_fullscreen(self) -> bool:
        """
        Should the game run in exclusive fullscreen mode?
        :return: True if the game should be fullscreen and false if in a window.
        """
        return self.__fullscreen

    def set_fullscreen(self, fullscreen: bool):
        """
        Should the game be running in a window or fullscreen? Must call apply_settings() to take affect.
        :param fullscreen: True for fullscreen and false for window.
        """
        self.__fullscreen = fullscreen

    def set_buffer_size(self, size: typing.Tuple[int, int]):
        """
        Set the size of the game area that will be rendered to the screen. You can think of this as the resolution
        that the game is rendering at. It is a virtual resolution because the engine will automatically add black
        boxes to the side of the screen if the window is larger. This results in the same area being visible no
        matter what the actual resolution of the player's computer is. A call to apply_settings() must be made for
        this to take affect.
        :param size: A tuple containing the virtual resolution in pixels.
        """
        self.__game_size = size

    def get_buffer_size(self) -> typing.Tuple[int, int]:
        """
        Get the virtual resolution (in pixels) that the game is rendering at.
        :return: The virtual resolution as a tuple.
        """
        return self.__game_size

    def get_size(self) -> typing.Tuple[int, int]:
        """
        This is the actual resolution of the window. The size of the window in pixels disregarding how much
        of that the game can render to.
        :return: The size as a tuple.
        """
        if self.__fullscreen:
            return self.__native_size
        else:
            return self.__size

    def set_size(self, size: typing.Tuple[int, int]):
        """
        Set the render resolution of the window. This will change the size of the actual window. The
        size will be ignored when running fullscreen as fullscreen is always done at the native resolution.
        :param size: The new size of the window in pixels.
        """
        self.__size = size

    def get_fps(self) -> float:
        """
        Get the target frame rate. This is not the actual frame rate but what the engine is trying
        to run at.
        :return: The desired frame rate.
        """
        return self.__fps

    def set_fps(self, fps: float):
        """
        Set the target frame rate. This will slow down the game if it is running faster then the target. This is
        desirable because it prevents the CPU from working to hard and draining the battery if it is not needed.
        Setting the target frame rate to zero tells the engine to run at maximum possible speed.
        :param fps: The frame rate the game should try to run at.
        """
        self.__fps = fps

    def get_asset_folder(self) -> str:
        """
        The folder that the engine will try to load assets from.
        :return: A path to the folder to get assets from.
        """
        return self.__asset_folder

    def set_asset_folder(self, folder: str):
        """
        Set the folder that the engine will try to load assets from. Must call apply_settings() for this to
        do anything.
        :param folder: A path to the folder to get assets from.
        """
        self.__asset_folder = folder

    def set_preload_files(self, files: typing.List[str]):
        """
        These files will be loaded on the main thread and not on the asset
        loading thread. This is done because a loading screen also needs assets
        which will need to be loaded before we can display it and load the rest.
        :param files: A list of files to load on the main thread causing it to block for a while.
        """
        self.__preload_files = files

    def get_preload_files(self) -> typing.List[str]:
        """
        A list of the assets to load before the game starts and not on the loading thread.
        :return: A list of file names.
        """
        return self.__preload_files

    def set_custom_setting(self, setting: str, data: typing.Union[int, float, bool, str]):
        """
        Set a custom setting for your game. It will be saved and loaded along with the other
        game and engine settings that are builtin.
        :param setting: The name of the setting to store.
        :param data: A primitive data type to store.
        """
        self.__custom[setting] = data

    def has_custom_settings(self, setting: str) -> bool:
        """
        Checks if a custom settings field is stored in this object.
        :param setting: The settings field to look for.
        :return: True if there is data and false if there is not.
        """
        return setting in self.__custom

    def get_custom_setting(self, setting: str) -> typing.Union[int, float, bool, str]:
        """
        Get a primitive data value that was stored as a setting in this object.
        :param setting: The name of the settings field.
        :return: The value loaded from the settings file.
        """
        return self.__custom[setting]


class Application:
    """
    The core component of a game. This will receive and process all the life-cycle events of the
    game. It will render and play the game according to the settings given to it.
    """
    def __init__(self, settings: Settings):
        """
        Create a new game from the passed in settings.
        :param settings: The engine and game settings to use.
        """
        self.__done = False
        self.__settings = settings
        self.__assets = league2.assets.AssetManager(settings.get_asset_folder())
        self.__clock = pygame.time.Clock()
        self.__screen = None
        self.__buffer = pygame.Surface(self.__settings.get_buffer_size())
        self.__scaled_buffer = None
        self.__screen_dirty = []

        self.__configure_screen(self.__settings.get_size())
        self.apply_settings()
        self.__buffer.fill((100, 149, 237))

        # Finally start loading assets.
        self.__assets.start(self.__settings.get_preload_files())

    def __get_scaled_size(self):
        bx, by = self.__screen.get_size()
        ix, iy = self.__buffer.get_size()
        sx = 0
        sy = 0
        if ix > iy:
            # In this case we must fit to the width.
            scale_factor = bx / float(ix)
            sy = scale_factor * iy
            if sy > by:
                scale_factor = by / float(iy)
                sx = scale_factor * ix
                sy = by
            else:
                sx = bx
        else:
            # In this case we must fit to the height.
            scale_factor = by / float(iy)
            sx = scale_factor * ix
            if sx > bx:
                scale_factor = bx / float(ix)
                sx = bx
                sy = scale_factor * iy
            else:
                sy = by
        return int(sx), int(sy)

    def __get_scaled_buffer(self):
        return pygame.Surface(self.__get_scaled_size())

    def __configure_screen(self, size):
        # Transparency is disabled on the screen and on the scaled buffer because they hold the
        # completed drawing which can't have a transparent background. This gives a big performance
        # boost since we will copying 25% less pixels each time we blit to the screen.
        self.__screen = pygame.display.set_mode(size, self.__settings.get_flags())
        self.__scaled_buffer = self.__get_scaled_buffer().convert()

        self.__screen.set_alpha(None)
        self.__scaled_buffer.set_alpha(None)
        self.__screen_dirty.append(self.__screen.fill((0, 0, 0)))

    def get_settings(self) -> Settings:
        """
        Get the settings that are used to configure this game.
        :return: A settings object that can be used to change game and engine settings.
        """
        return self.__settings

    def get_assets(self) -> league2.assets.AssetManager:
        """
        Get the asset manager for this game. It is used to load assets ahead of time and access them.
        :return: The asset manager object.
        """
        return self.__assets

    def apply_settings(self):
        """
        Applies the settings from the settings object to this game. This is a rather slow function as it
        needs to recreate several resources and should only be used when settings have actually changed.
        """

        # The size of the game's display may have changed and we will need to redo the aspect ratio buffer
        # if this is the game.
        if self.__settings.get_buffer_size() != self.__buffer.get_size():
            self.__buffer = pygame.Surface(self.__settings.get_buffer_size())
        size = self.__screen.get_size()
        # If we are going fullscreen we can't just use the same size again like we can for windowed mode because
        # the screen will be a different size. If the window is not resizable we will also use the size from the
        # settings.
        if self.__settings.get_fullscreen() or not self.__settings.get_resizeable():
            size = self.__settings.get_size()
        self.__configure_screen(size)
        # Update where we get assets from.
        self.__assets.set_root(self.__settings.get_asset_folder())
        # Change the name of the window.
        pygame.display.set_caption(self.__settings.get_title())

    def run(self):
        """
        Enters the main game loop and starts rendering and updating the game.
        """
        while not self.__done:
            resize = None
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.__done = True
                if event.type == pygame.QUIT:
                    self.__done = True
                elif event.type == pygame.VIDEORESIZE:
                    # We don't want to handle the resize here because some window managers spam the resize
                    # event and it would result in us processing several slow resize event in a single frame. Just
                    # cache the size and wait until we processed them all.
                    resize = event.w, event.h
            if resize is not None:
                self.__configure_screen(resize)
                resize = None

            frame_time = self.__clock.tick(self.__settings.get_fps())

            # Scale our game up so that it fits nicely onto the screen without any stretching or showing more
            # of the game. We scale up to preserve aspect ratio. This is one of the slower parts of the game
            # because of the sheer amount of pixels that need to be scaled up.
            pygame.transform.scale(self.__buffer, self.__get_scaled_size(), self.__scaled_buffer)
            # Now we need to figure out where to position the scaled buffer on the screen to put the
            # bars in the right place.
            scaled_width, scaled_height = self.__scaled_buffer.get_size()
            screen_width, screen_height = self.__screen.get_size()
            final_pos = ((screen_width - scaled_width) / 2, (screen_height - scaled_height) / 2)

            # Draw the finished result and present it on the screen. Since all drawing is done on the CPU, we need
            # to preserve performance as much as possible. Rather than redrawing the screen every single frame, we
            # keep track of the regions that changed this frame and only update those parts of the screen.
            self.__screen_dirty.append(self.__screen.blit(self.__scaled_buffer, final_pos))
            pygame.display.update(self.__screen_dirty)
            self.__screen_dirty.clear()


def init():
    """
    Initialize the engine. This should be the very first thing called.
    """
    pygame.init()


def quit():
    """
    Release all engine resources and exit. This should be called when the program
    is finished.
    """
    pygame.quit()


def run(app: typing.Type[Application], settings: Settings):
    """
    Run the provided game with the provided settings. The game class must have a constructor that
    takes no arguments other than the settings object.
    :param app: The class to instantiate and run.
    :param settings: The settings to create the game with.
    """
    app(settings).run()
