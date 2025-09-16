from typing import override
from engine import Status, message_subscriber, message_center_instance, attack_message, attack_result_message, turn_over_message
import random
from game import field
from player import player_field

class AI(message_subscriber):
    def __init__(self):
        self.board = None
        self.reset()
        message_center_instance.subscribe(turn_over_message.__name__, self)
        message_center_instance.subscribe(attack_result_message.__name__, self)

    def get_hunt_targets(self):
        targets = []
        for y in range(10):
            for x in range(10):
                # The 'checkerboard' pattern: (x + y) is even
                if (x + y) % 2 == 0 and self.board[x][y] == Status.Water.value:
                    targets.append((x, y))
        return targets
    
    def send_attack_message(self, x, y):
        message_center_instance.publish(attack_message.__name__,
                                        attack_message(player_field.__name__, x, y))
        
    def attack(self):
        print("AI attacking")
        if self.mode == "hunt":
            # Hunting for a new ship
            possible_attacks = [(x, y) for x in range(0, 10) for y in range(0, 10) 
                        if self.board[y][x] == Status.Water.value 
                        and (x, y) not in self.attacked_cells]

            if not possible_attacks:
                # Fallback to a simpler hunt if checkerboard is exhausted
                possible_attacks = [(x, y) for x in range(10) for y in range(10) if self.board[y][x] == Status.Water.value]
            
            if possible_attacks:
                random.shuffle(possible_attacks)
                x, y = possible_attacks.pop()
                print(f"AI hunting at {x}, {y}")
                # The result of the attack will determine if we switch to target mode
                self.send_attack_message(x, y)
    
        elif self.mode == "target":
            # Targeting a known ship
            if self.potential_targets:
                x, y = self.potential_targets.pop()
                print(f"AI targeting at {x}, {y}")
                self.send_attack_message(x, y)
            else:
                # If we've exhausted all targets around a hit, go back to hunting
                self.mode = "hunt"
                self.attack() # Recursively call to start hunting
                 
    @override
    def receive(self, message_type, data):
        match message_type:
            case turn_over_message.__name__:
                if data.player_id != field.__name__:
                    self.is_turn = True
                    self.attack()
            case attack_result_message.__name__:
                if data.attacked_player == player_field.__name__:
                    if data.boat_hit:
                        self.board[data.y][data.x] = Status.Hit.value
                        self.mode = "target"
                        self.last_hit = (data.x, data.y)
                        self.attacked_cells.add((data.x, data.y))
                        # Add adjacent cells to potential targets   
                        x, y = data.x, data.y
                        adjacent = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
                        for ax, ay in adjacent: 
                            if 0 <= ax < 10 and 0 <= ay < 10 and self.board[ay][ax] == Status.Water.value and (ax, ay) not in self.attacked_cells:
                                self.potential_targets.append((ax, ay))
                    else:
                        self.board[data.y][data.x] = Status.Miss
                    message_center_instance.publish(turn_over_message.__name__, turn_over_message(field.__name__))
                    self.is_turn = False
            case "game_over":
                print("Game Over received in AI")   
                self.reset()
            case _:
                pass

    def reset(self):
        self.mode = "hunt"  # Can be "hunt" or "target"
        self.last_hit = None
        self.potential_targets = []
        self.is_turn = False
        self.attacked_cells = set()
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