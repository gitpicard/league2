import pygame
import abc
import typing


class Control(abc.ABC):
    def __init__(self, margin: typing.Optional[typing.Tuple[int, int, int, int]] = (0, 0, 0, 0)):
        self.__margin = margin

    def get_margin(self) -> typing.Tuple[int, int, int, int]:
        return self.__margin

    def set_margin(self, margin: typing.Tuple[int, int, int, int]):
        self.__margin = margin

    @abc.abstractmethod
    def get_width(self) -> float:
        return 0

    @abc.abstractmethod
    def get_height(self) -> float:
        return 0

    @abc.abstractmethod
    def render(self, surface: pygame.Surface, rect: pygame.Rect):
        pass


class Label(Control):
    def __init__(self, text: str, font: pygame.font.Font, color: pygame.Color,
                 margin: typing.Optional[typing.Tuple[int, int, int, int]] = (0, 0, 0, 0)):
        super().__init__(margin)
        self.__text = text
        self.__font = font
        self.__color = color
        self.__surface = font.render(text, False, color)

    def get_width(self) -> float:
        return self.__surface.get_width()

    def get_height(self) -> float:
        return self.__surface.get_height()

    def set_text(self, text: str):
        self.__text = text
        self.__surface = self.__font.render(text, False, self.__color)

    def get_text(self) -> str:
        return self.__text

    def set_font(self, font: pygame.font.Font):
        self.__font = font
        # We need to re-render the surface since the font changed.
        self.set_text(self.__text)

    def get_font(self) -> pygame.font.Font:
        return self.__font

    def set_color(self, color: pygame.Color):
        self.__color = color
        self.set_text(self.__text)

    def get_color(self) -> pygame.Color:
        return self.__color

    def render(self, surface: pygame.Surface, rect: pygame.Rect):
        surface.blit(self.__surface, rect)


class Container(Control, abc.ABC):
    pass


class FreeContainer(Container):
    def __init__(self):
        super().__init__()
        self.__items = []

    def add(self, pos: pygame.Vector2, item: Control):
        self.__items.append([pos, item])

    def remove(self, item: Control):
        for v in self.__items:
            if v[1] == item:
                self.__items.remove(v)

    def get_width(self):
        most_right = 0
        for v in self.__items:
            x = v[0].x + v[1].get_width() + v[1].get_margin()[2]
            if x > most_right:
                most_right = x
        return most_right

    def get_height(self):
        most_bottom = 0
        for v in self.__items:
            y = v[0].y + v[1].get_height() + v[1].get_margin()[3]
            if y > most_bottom:
                most_bottom = y
        return most_bottom

    def render(self, surface: pygame.Surface, rect: pygame.Rect):
        for v in self.__items:
            # The free container has the simplest layout code: no layout code! It simply allows controls to
            # be placed with pixel-perfect positioning meaning that margins are also meaningless.
            v[1].render(surface, (v[0].x, v[0].y, v[1].get_width(), v[1].get_height()))
