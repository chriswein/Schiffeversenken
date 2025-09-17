from typing import Dict, List, Tuple
import pygame
from engine import Boat, boat_choice_message, boat_placed_message, mouse_listener, render_item, message_center_instance
from player import player_field


class HUD(render_item):
    points = 0
    misses = 0
    surface = None

    def __init__(self, surface, x: int = 0, y: int = 0):
        self.surface = surface
        self.x, self.y = x, y
        pygame.font.init()

    def draw(self):
        font = pygame.font.SysFont("Comic Sans MS", 30)
        text1 = font.render("Daneben: {}".format(
            self.misses), False, (255, 255, 255))
        text2 = font.render("Getroffen: {}".format(
            self.points), False, (255, 255, 255))
        self.surface.blit(text1, (self.x, self.y))
        # 5 Pixel Abstand
        self.surface.blit(text2, (self.x, self.y + text1.get_height() + 5))
        None

    def update(self):
        pass

    def add_miss(self):
        self.misses += 1

    def add_hit(self):
        self.points += 1

    def reset(self):
        self.points = 0

    def receive(self, message_type, data):
        if message_type == "hit":
            self.add_hit()
        elif message_type == "miss":
            self.add_miss()


class Placement_HUD(render_item, mouse_listener):
    surface = None
    selectable_boats: List[Boat] = []
    position_of_boats: Dict[Boat, Tuple[int, int]] = {}
    max_text_width: int = 0
    text_height: int = 0
    currently_selected_boat: int = None
    user_clicked_on_label: bool = False

    def __init__(self, surface, x=0, y=0):
        self.surface = surface
        self.x, self.y = x, y
        self.selectable_boats = [boat for boat in Boat]
        pygame.font.init()
        self.font = pygame.font.SysFont("Comic Sans MS", 30)
        self.text1 = self.font.render(
            "Platzierungsmodus", False, (255, 255, 255))
        self.text2 = self.font.render(
            "Right click to turn ship 90deg", False, (255, 255, 255))
        message_center_instance.subscribe(boat_placed_message.__name__, self)

    def __del__(self):
        message_center_instance.unsubscribe(boat_placed_message.__name__, self)

    def draw(self):
        self.surface.blit(self.text1, (self.x, self.y))
        self.surface.blit(self.text2, (self.x+750, self.y))
        self.position_of_boats = {}

        # draw selectable boats
        for i, boat in enumerate(self.selectable_boats):
            boat_text = self.font.render(
                f"{i+1}: {boat.name}",
                False,
                (255, 255, 255) if i != self.currently_selected_boat else (255, 0, 0)
            )

            self.max_text_width = max(
                self.max_text_width, boat_text.get_width()
            )

            self.text_height = boat_text.get_height()

            self.surface.blit(
                boat_text,
                (self.x, self.y + self.text1.get_height() +
                 5 + i * (boat_text.get_height() + 5))
            )

            self.position_of_boats[boat] = (
                self.x, self.y + self.text1.get_height() + 5 + i * (boat_text.get_height() + 5)
            )

    def get_selected_boat(self, x: int, y: int) -> int | None:
        for key, value in self.position_of_boats.items():
            text_x, text_y = value
            if (
                    text_x <= x <= text_x + self.max_text_width
                    and
                    text_y <= y <= text_y + self.text_height
            ):
                return key.value
        return None
# MARK: mouse

    def mouse_click(self, event, button):
        # We hovered and clicked. But none is selected yet
        if self.currently_selected_boat is not None and not self.user_clicked_on_label:
            key = self.selectable_boats[self.currently_selected_boat]
            self.user_clicked_on_label = True
            message_center_instance.publish(
                boat_choice_message.__name__, boat_choice_message(player_field.__name__, key))

        # We clicked again on a label but have already selected one
        elif self.user_clicked_on_label and self.get_selected_boat(*pygame.mouse.get_pos()) is not None:
            self.user_clicked_on_label = False  # Enable a second click on a label

    def update(self):
        x, y = pygame.mouse.get_pos()
        if ((bt := self.get_selected_boat(x, y)) is not None and not self.user_clicked_on_label):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            self.currently_selected_boat = bt
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def receive(self, message_type, data):
        match message_type:
            case boat_placed_message.__name__:
                if data.player_id == player_field.__name__:
                    self.currently_selected_boat = None
                    self.user_clicked_on_label = False
