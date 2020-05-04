import league2
import pygame


GAME_SIZE = (640, 480)


class SandboxGame(league2.Application):
    def __init__(self, settings):
        super().__init__(settings)
        self.__test = None
        self.__tilesheet = None
        self.__gui = league2.gui.FreeContainer()

    def on_start(self):
        while not self.get_assets().is_finished():
            continue
        self.__test = self.get_assets().get_surface('sprites/test')
        self.__tilesheet = self.get_assets().get_tilesheet('tilesheets/test')
        font = self.get_assets().get_font('fonts/test')
        self.set_root_gui_container(self.__gui)

        self.__gui.add(pygame.Vector2(70, 70), league2.gui.Label('Hello world!', font, pygame.Color(255, 255, 255)))

    def on_end(self):
        pass

    def on_draw(self, frame_time: float):
        self.get_surface().blit(self.__test, (10, 10))
        self.get_surface().blit(self.__tilesheet.get_tile(3, 3), (200, 200))

    def on_update(self, frame_time: float):
        pass
