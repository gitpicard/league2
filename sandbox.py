import league2


GAME_SIZE = (426, 240)


class SandboxGame(league2.Application):
    def __init__(self, settings):
        super().__init__(settings)
        self.__test = None
        self.__tilesheet = None

    def on_start(self):
        while not self.get_assets().is_finished():
            continue
        self.__test = self.get_assets().get_surface('sprites/test')

    def on_end(self):
        pass

    def on_draw(self, frame_time: float):
        self.get_surface().blit(self.__test, (10, 10))

    def on_update(self, frame_time: float):
        pass
