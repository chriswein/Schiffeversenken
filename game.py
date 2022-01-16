import math
from engine import *
import pygame
from pygame import gfxdraw
import random


class field(render_item, mouse_listener):
    surface, am, audio_ids = None, None, None
    board = None
    width, height = 700, 700

    def __init__(self, surface, audio_manager_reference, audio_ids):
        self.surface = surface
        self.am = audio_manager_reference
        self.audio_ids = audio_ids
        self.reset()

    def reset(self):
        self.board = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        ]

    def isHit(self, x, y):
        return True

    def draw(self):
        for line in range(1, 11):
            pygame.draw.aaline(
                self.surface,
                (255, 255, 255),
                (0, line*(self.width//10)),
                (self.width, line*(self.width//10))
            )
            pygame.draw.aaline(
                self.surface,
                (255, 255, 255),
                (line*(self.width//10), 0),
                (line*(self.width//10), self.height)
            )
        for y, row in enumerate(self.board):
            for x, col in enumerate(row):
                if col == 1:
                    pygame.draw.circle(
                        self.surface,
                        (255, 255, 255),
                        ((self.width//10)//2+x*(self.width//10),
                         (self.width//10)//2+y*(self.width//10)),
                        25
                    )

    def update(self):
        pass

    def mouse_click(self, e):
        pass
