import random
from typing import List, Tuple
from engine import *
import pygame
from pygame import gfxdraw

from player import player_field


class field(render_item, mouse_listener):
    """ A board for playing the game on """
    surface, audio_manager, audio_ids = None, None, None  # Drawing surface, Audio Manager, Audio Ids
    hud = None
    is_turn = True  # Indicates wether it is the players turn.
    board = None
    x, y = 0, 0
    width, height = 700, 700
    n = 10
    radius = (width//n+1)//3
    hits = 0
    maxhits = 0
    boats : List[List[Tuple[int,int]]] = []

    def __init__(self, surface, audio_manager_reference, audio_ids, hud, offset_x=1, offset_y=1):
        self.surface = surface
        self.audio_manager = audio_manager_reference
        self.audio_ids = audio_ids
        self.hud = hud
        self.x, self.y = offset_x, offset_y
        self.reset()
        # Place three boats at fixed positions
        self.place_boat((2, 1), (2, 6))
        self.place_boat((7, 1), (9, 1))
        self.place_boat((5, 3), (5, 7))
        self.maxhits = 14
        message_center_instance.subscribe("game_over", self)
        message_center_instance.subscribe(turn_over_message.__name__, self)

    def reset(self):
        # Reset the board to empty (0 = water)
        self.boats = []
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

    def this_sunk_the_boat(self, x,y) -> Tuple[bool,int]:
        for i,boat in enumerate(self.boats):
            if (x,y) in boat:
                for coord in boat:
                    xi,yi = coord
                    if self.board[yi][xi] != Status.Hit:
                        return False,-1
                return True,i
        
        return False,-1

    def is_hit(self, x, y):
        # Check if the selected cell is a hit or miss
        if self.hud != None and self.board[y][x] in [Status.Water.value,Status.Boat.value]:
            self.hud.add_hit(
            ) if self.board[y][x] == Status.Boat else self.hud.add_miss()
        if self.board[y][x] in [Status.Boat.value]:
            self.hits += 1
            return True
        return False

    def place_boat(self, point1, point2):
        """ Places a boat between two points (horizontal or vertical) """
        assert (len(point1) > 1 and len(point2) > 1)
        x1, y1 = point1
        x2, y2 = point2
        boat = []
        if y1 == y2:
            # Horizontal boat
            for x in range(min(x1, x2), max(x1, x2)+1):
                self.board[y1][x] = Status.Boat.value
                boat.append((x,y1))
            self.boats.append(boat)
            return True
        elif x1 == x2:
            # Vertical boat
            for y in range(min(y1, y2), max(y1, y2)+1):
                self.board[y][x1] = Status.Boat.value
                boat.append((x1,y))
            self.boats.append(boat)
            return True
        else:
            # Only straight boats allowed
            return False

    def draw(self):
        # Draw the grid
        for line in range(0, 11):
            # horizontal lines
              # horizontal lines
            pygame.draw.aaline(
                self.surface,
                (255, 255, 255),
                (0+self.x, line*(self.width//self.n)),
                (self.width+self.x, line*(self.width//self.n))
            )
            # vertical lines
            pygame.draw.aaline(
                self.surface,
                (255, 255, 255),
                ((line*(self.width//self.n))+self.x, 0+self.y),
                ((line*(self.width//self.n))+self.x, self.height+self.y)
            )

        # Draw the board state (boats, misses)
        for y, row in enumerate(self.board):
            for x, col in enumerate(row):
                if col == Status.Hit:
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
                elif col == Status.Miss:
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

    def rnd_coord(self, maximum, minimum=0):
        # Get a random coordinate between minimum and maximum
        return random.randint(minimum, maximum)

    def random_setup(self):
        # Randomly place three ships on the board
        boats = [Boat.Fregate, Boat.Destroyer, Boat.Carrier] #TODO: This should match the opponent
       
        possible_target_points = 0
        for i in range(0, len(boats)):
            dice = random.choice([True, False])
            len_boat = boat_sizes[boats[i]]
            possible_target_points += len_boat
            if dice:    # go horizontal 
                start = self.rnd_coord(len(self.board)-1-len_boat,0)
                row = self.rnd_coord(len(self.board)-1)
                self.place_boat((start, row), (start+len_boat-1,row))
            else:    # go vertical
                start = self.rnd_coord(len(self.board)-1-len_boat,0)
                col = self.rnd_coord(len(self.board)-1)
                self.place_boat((col, start), (col,start+len_boat-1))
        self.maxhits = possible_target_points

    def update(self):
        # Check if all ships are hit, then reset and start new round
        if self.hits == self.maxhits and self.hits != 0:
			# Show winning screen for 2 seconds
            message_center_instance.publish("game_over", None)
            font = pygame.font.SysFont(None, 72)
            text = font.render("You Win!", True, (255, 255, 0))
            rect = text.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
            self.surface.blit(text, rect)
            pygame.display.flip()
            pygame.time.delay(2000)
            self.reset()
            self.audio_manager.play(self.audio_ids[2])
            self.hits = 0
            self.hud.reset()
            self.random_setup()


    def mouse_click(self, e, button):
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
            
            message_center_instance.publish(message_type=attack_message.__name__, # for the ai
                                             data=attack_message(self.__class__.__name__, bx, by))
            if self.is_hit(bx, by):
                self.board[by][bx] = Status.Hit  # Mark as hit
                b, i = self.this_sunk_the_boat(bx,by)
                print(f"this sunk {b} boat {i}")
                if(b):
                    self.boats.pop(i)
                    self.audio_manager.play(self.audio_ids[3])

                self.audio_manager.play(self.audio_ids[1])
                message_center_instance.publish(attack_result_message.__name__,attack_result_message(self.__class__.__name__,bx,by ,True))
            else:
                if self.board[by][bx] == Status.Water.value:
                    self.board[by][bx] = Status.Miss  # Mark as miss
                    self.audio_manager.play(self.audio_ids[0])
                    message_center_instance.publish(attack_result_message.__name__,attack_result_message(self.__class__.__name__,bx,by ,False))
                # Else do nothing, already hit/miss
    #MARK: Messages
    def receive(self, message_type, data):
        print(f"Field received message: {message_type}")
        if message_type == turn_over_message.__name__:
            if data.player_id == field.__name__:
                self.is_turn = True
                print("Player's turn")
        elif message_type == "game_over":
            print("Game Over received in field")
            self.is_turn = False  # Disable further input until reset
            self.reset()
        None    

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
    def receive_message(self, message_type, data):  
        None  # Placeholder for message handling

