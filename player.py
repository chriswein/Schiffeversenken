
from engine import *
import pygame
from pygame import gfxdraw
from engine import *

class player_field(render_item, mouse_listener):
    """ A board for the player to place their ships on """
    surface = None
    audio_manager = None
    audio_ids = None
    hud = None
    x, y = 0, 0
    width, height = 700, 700
    n = 10
    radius = (width//n+1)//3
    boats = []#[Boat.Fregate, Boat.Destroyer, Boat.Submarine]
    placed_boats = []#[False,False,False]
    selected_boat = None
    placing_boat = True
    boat_start = None
    boat_end = None
    is_turn = False  # Indicates wether it is the players turn.
    board = None
    hits = 0
    maxhits = 0
    maxboats = 3
    placement_direction = Direction.Horizontal

  
    def __init__(self, surface, audio_manager_reference, audio_ids, hud, offset_x=720, offset_y=0):
        self.surface = surface
        self.audio_manager = audio_manager_reference
        self.audio_ids = audio_ids
        self.hud = hud
        self.x, self.y = offset_x, offset_y
        self.selected_boat = self.boats[1] if len(self.boats) > 0 else None
        self.is_turn = True
        self.reset()
        message_center_instance.subscribe("game_over", self)
        message_center_instance.subscribe(attack_message.__name__, self)
        message_center_instance.subscribe(attack_result_message.__name__, self)
        message_center_instance.subscribe(turn_over_message.__name__, self)
        message_center_instance.subscribe(boat_choice_message.__name__, self)   

    def mouse_in_board(self, x, y):
        return (
            self.x <= x and x <= self.x+self.width  # Is it in Box?
            and
            self.y <= y and y <= self.y+self.height  # Is it in Box?
        )
    
    def boat_placement_modus(self):
        return self.selected_boat != None and not all(self.placed_boats)
    
    def draw_indicator_circle(self, x_in_grid_coordinates, y_in_grid_coordinates, color, radius=-1):
        assert(x_in_grid_coordinates<12 and y_in_grid_coordinates<12)
        # size of one cell
        cell = self.width / self.n

        # grid origin (use 0 if you don't have a top/left offset)
        origin_x = getattr(self, "x", 0)
        origin_y = getattr(self, "y", 0)

        # center of cell (float -> int only once)
        cx = int(x_in_grid_coordinates * cell + cell / 2)
        cy = int(y_in_grid_coordinates * cell + cell / 2)
        r  = int(self.radius) if radius == -1 else radius

        # Preferred: use gfxdraw for filled + antialiased outline (they take ints)
        pygame.gfxdraw.filled_circle(self.surface, self.x+cx, self.y+cy, r, color)
        pygame.gfxdraw.aacircle(self.surface, self.x+cx, self.y+cy, r, color)
 

    def can_place_boat(self, direction : Direction, x,y, boat : Boat ):
        boat_size = boat_sizes[boat]
        boat_start_offset = boat_size//2
        boat_end_offset = boat_size-boat_start_offset-1
        if direction == Direction.Horizontal:
            if x-boat_start_offset < 0 or x+boat_end_offset >= self.n:
                return False
            for i in range(-boat_start_offset, boat_end_offset+1):
                if self.board[y][x+i] != Status.Water.value:
                    return False
            return True
        elif direction == Direction.Vertical:
            if y-boat_start_offset < 0 or y+boat_end_offset >= self.n:
                return False
            for i in range(-boat_start_offset, boat_end_offset+1):
                if self.board[y+i][x] != Status.Water.value:
                    return False
            return True

    def get_mouse_board_position_in_grid_coordinates(self, x, y):
        if not self.mouse_in_board(x,y):
            return None
        x -= self.x
        y -= self.y
        cell = self.width / self.n
        bx = int(x // cell)
        by = int(y // cell)
        bx = bx if bx < 10 else 9
        by = by if by < 10 else 9
        return (bx,by) # Hier muss noch der Offset rein
    
    def get_grid_coordinates_in_word_coordinates(self, x, y):
        cell = self.width / self.n
        x = x*(cell)+self.radius+self.x
        y = y*(cell)+self.radius+self.y
        return (x,y)    

#MARK: Boat plcmnt
    def show_boat_placement(self, x, y):
        if not self.boat_placement_modus():
            return
        bx, by = self.get_mouse_board_position_in_grid_coordinates(x,y)

        boat_size = boat_sizes[self.selected_boat]
        boat_start_offset = boat_size//2
        boat_end_offset = boat_size-boat_start_offset-1
        
        if(self.can_place_boat(self.placement_direction, bx, by, self.selected_boat)):
            for i in range(-boat_start_offset, boat_end_offset+1):
                self.draw_indicator_circle(
                    bx+i if self.placement_direction == Direction.Horizontal else bx,
                    by if self.placement_direction == Direction.Horizontal else by+i,
                    (0,255,0) 
                )
                
#MARK: draw & update
    def draw(self):
        for line in range(0, 11):
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
        m_x,m_y = pygame.mouse.get_pos()

        if self.mouse_in_board(m_x,m_y) and self.boat_placement_modus():
            self.show_boat_placement(m_x,m_y)
        
            bx,by = self.get_mouse_board_position_in_grid_coordinates(m_x,m_y) if self.mouse_in_board(m_x,m_y) else (None,None)
            if bx != None:
                self.draw_indicator_circle(bx,by, (255,255,255), self.radius) # Dummy to fix gfxdraw issue

        for by in range(0,10):
            for bx in range(0,10):
                if self.board[by][bx] == Status.Boat.value:
                    self.draw_indicator_circle(bx, by, (0,0,255), self.radius)
                elif self.board[by][bx] == Status.Hit.value:
                    self.draw_indicator_circle(bx, by, (255,0,0), self.radius)
                elif self.board[by][bx] == Status.Miss.value:
                    self.draw_indicator_circle(bx, by, (255,255,255), self.radius//2)

        
    def is_placing_boats(self):
        return self.placing_boat
    
    def update(self):
        None

    def place_boat_at_position(self, xw, yw):
        if self.mouse_in_board(xw,yw) == False or not self.boat_placement_modus():
            return
        
        bx, by = self.get_mouse_board_position_in_grid_coordinates(xw,yw)

        if self.can_place_boat(self.placement_direction, bx, by, self.selected_boat):
            boat_size = boat_sizes[self.selected_boat]
            boat_start_offset = boat_size//2
            boat_end_offset = boat_size-boat_start_offset-1

            if self.placement_direction == Direction.Horizontal:
                for i in range(-boat_start_offset, boat_end_offset+1):
                    self.board[by][bx+i] = Status.Boat.value

            elif self.placement_direction == Direction.Vertical:
                for i in range(-boat_start_offset, boat_end_offset+1):
                    self.board[by+i][bx] = Status.Boat.value

            self.placed_boats[-1] = True
            self.maxhits += boat_size

            message_center_instance.publish(boat_placed_message.__name__, boat_placed_message(player_field.__name__, self.selected_boat))
            
            if len(self.boats) > self.maxboats: # Placed all boats
                self.selected_boat = None
                self.placing_boat = False

    def mouse_click(self, event, button):
        x, y = event
        if button == MouseButton.Right:
            self.placement_direction = Direction.Horizontal if self.placement_direction == Direction.Vertical else Direction.Vertical
        if button == MouseButton.Left and self.boat_placement_modus() and self.placing_boat:
            print("Place Boat")
            self.place_boat_at_position(x,y)
        if self.is_turn:
            None
        None

    def reset(self):
        self.placed_boats = []
        self.boats = []
        self.selected_boat = None
        self.is_turn = True
        self.placing_boat = True
        self.hits = 0
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

    #MARK: Msg Listener
    def receive(self, message_type, data):
        match message_type:
            case "game_over":
                self.reset()

            case attack_message.__name__:
                data : attack_message = data
                if data.player_id_has_been_attacked == self.__class__.__name__:
                    ax, ay = data.x, data.y
                    if self.board[ax][ay] == Status.Boat.value:
                        message_center_instance.publish(attack_result_message.__name__,attack_result_message(data.player_id_has_been_attacked,ax,ay ,True))
                        self.board[ax][ay] = Status.Hit.value
                        self.hits += 1
                        if self.hits >= self.maxhits:
                            message_center_instance.publish("game_over", None)
                    else:
                        message_center_instance.publish(attack_result_message.__name__,attack_result_message(data.player_id_has_been_attacked,ax,ay ,False))
                        self.board[ax][ay] = Status.Miss.value

            case attack_result_message.__name__: 
                data : attack_result_message = data
                if data.attacked_player == "field":
                    message_center_instance.publish(turn_over_message.__name__, turn_over_message(player_field.__name__))                   

            case turn_over_message.__name__:
                if data.player_id != self.__class__.__name__:
                    self.is_turn = True
#MARK: Boat choice
            case boat_choice_message.__name__:
                print("Player field received boat choice message")
                data : boat_choice_message = data
                if data.player_id == self.__class__.__name__:
                    if not all(self.placed_boats): # This happens if the player changes his mind and wants to place another boat
                        if len(self.boats) > 0 and self.placed_boats[-1] == False:
                            self.boats.pop()
                            self.placed_boats.pop()
                    self.boats.append(data.boat)
                    self.placed_boats.append(False)
                    print(f"Player field boats: {len(self.boats)}")
                    self.selected_boat = data.boat
                    self.placement_direction = Direction.Horizontal