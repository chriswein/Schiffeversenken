import random
import math
from engine import *
import pygame
from pygame import gfxdraw


class field(render_item, mouse_listener):
    """ A board for playing the game on """
    surface, am, audio_ids = None, None, None  # Drawing surface, Audio Manager, Audio Ids
    hud = None
    is_turn = True  # Indicates wether it is the players turn.
    board = None
    x, y = 0, 0
    width, height = 700, 700
    n = 10
    radius = (width//n+1)//3
    hits = 0
    maxhits = 0

    def __init__(self, surface, audio_manager_reference, audio_ids, hud):
        self.surface = surface
        self.am = audio_manager_reference
        self.audio_ids = audio_ids
        self.hud = hud
        self.reset()
        # Place three boats at fixed positions
        self.place_boat((2, 1), (2, 6))
        self.place_boat((7, 1), (9, 1))
        self.place_boat((5, 3), (5, 7))
        self.maxhits = 14

    def reset(self):
        # Reset the board to empty (0 = water)
        self.board = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]

    def is_hit(self, x, y):
        # Check if the selected cell is a hit or miss
        if self.hud != None:
            self.hud.add_hit(
            ) if self.board[y][x] == 2 else self.hud.add_miss()
        if self.board[y][x] == 2:
            self.hits += 1
            return True
        return False

    def place_boat(self, point1, point2):
        """ Places a boat between two points (horizontal or vertical) """
        assert (len(point1) > 1 and len(point2) > 1)
        x1, y1 = point1
        x2, y2 = point2
        if y1 == y2:
            # Horizontal boat
            for x in range(min(x1, x2), max(x1, x2)+1):
                self.board[y1][x] = 2
            return True
        elif x1 == x2:
            # Vertical boat
            for y in range(min(y1, y2), max(y1, y2)+1):
                self.board[y][x1] = 2
            return True
        else:
            # Only straight boats allowed
            return False

    def draw(self):
        # Draw the grid
        for line in range(1, 11):
            # horizontal lines
            pygame.draw.aaline(
                self.surface,
                (255, 255, 255),
                (0, line*(self.width//self.n)),
                (self.width, line*(self.width//self.n))
            )
            # vertical lines
            pygame.draw.aaline(
                self.surface,
                (255, 255, 255),
                (line*(self.width//self.n), 0),
                (line*(self.width//self.n), self.height)
            )

        # Draw the board state (boats, misses)
        for y, row in enumerate(self.board):
            for x, col in enumerate(row):
                if col == 1:
                    # Hit boat
                    pygame.draw.circle(
                        self.surface,
                        (255, 255, 255),
                        ((self.width//self.n)//2
                         + x*(self.width//self.n),
                         (self.width//self.n)//2
                         + y*(self.width//self.n)),
                        self.radius+1
                    )
                    pygame.gfxdraw.aacircle(self.surface,
                                            (self.width//self.n)//2
                                            + x*(self.width//self.n),
                                            (self.width//self.n)//2
                                            + y*(self.width//self.n),
                                            self.radius,
                                            (255, 255, 255))
                elif col == 3:
                    # Miss
                    pygame.draw.circle(
                        self.surface,
                        (255, 255, 255),
                        ((self.width//self.n)//2
                         + x*(self.width//self.n),
                         (self.width//self.n)//2
                         + y*(self.width//self.n)),
                        self.radius//2
                    )
                    pygame.gfxdraw.aacircle(self.surface,
                                            (self.width//self.n)//2
                                            + x*(self.width//self.n),
                                            (self.width//self.n)//2
                                            + y*(self.width//self.n),
                                            self.radius//2,
                                            (255, 255, 255))

    def coord(self, maximum, minimum=0):
        # Get a random coordinate between minimum and maximum
        return random.randint(minimum, maximum)

    def random_setup(self):
        # Randomly place three ships on the board
        possible_target_points = 0
        ships = []
        for i in range(0, 3):
            dice, col, row = self.coord(1, 0), self.coord(
                len(self.board)-3), self.coord(len(self.board)-3)
            if dice:
                # go horizontal
                point = (col, self.coord(len(self.board)-1, row))
                possible_target_points += abs(point[1]-row)
                ships.append(abs(point[1]-row))
                self.place_boat(
                    (col, row),
                    point  # stay in line
                )
            else:
                # go vertical
                point = (self.coord(len(self.board)-1, col), row)
                possible_target_points += abs(point[0]-col)
                ships.append(abs(point[0]-col))
                self.place_boat(
                    (col, row),
                    point  # stay in row
                )
            """ TODO maybe this needs to be a little less random to enshure some constraints the user can
                                exploit
                        """
        print(possible_target_points, ships)
        self.maxhits = possible_target_points

    def update(self):
        # Check if all ships are hit, then reset and start new round
        if self.hits == self.maxhits and self.hits != 0:
			# Show winning screen for 2 seconds
            font = pygame.font.SysFont(None, 72)
            text = font.render("You Win!", True, (255, 255, 0))
            rect = text.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
            self.surface.blit(text, rect)
            pygame.display.flip()
            pygame.time.delay(2000)
            self.reset()
            self.am.play(self.audio_ids[2])
            self.hits = 0
            self.hud.reset()
            self.random_setup()

    def mouse_click(self, e):
        # Handle mouse click event
        x, y = e
        if (
                self.x <= x and x <= self.x+self.width  # Is it in Box?
                and
                self.y <= y and y <= self.y+self.height  # Is it in Box?
                and
                self.is_turn
        ):
            # the player clicked inside our board
            bx, by = x//(self.width//self.n), y//(self.height//self.n)
            if not self.is_hit(bx, by):
                if not self.board[by][bx] == 1:
                    self.board[by][bx] = 3  # Mark as miss
                    self.am.play(self.audio_ids[0])
            else:
                self.board[by][bx] = 1  # Mark as hit
                self.am.play(self.audio_ids[1])


class board_bridge(render_item):
    boards = []

    def add(self, board):
        # Add a board to the bridge
        self.boards.append(board)

    def attack(self, board, x, y):
        # Placeholder for attack logic between boards
        pass

    def draw(self):
        # Placeholder for drawing logic
        None

    def update(self):
        # Placeholder for update logic
        None

    def pool(self, pool):
        # Store a reference to a pool (purpose
        None
