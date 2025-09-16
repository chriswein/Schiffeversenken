from abc import ABC, abstractmethod
import pygame 
from enum import Enum

DEBUG = True

class Status(Enum):
    Water = 0
    Hit = 1
    Boat = 2
    Miss = 3
    Placement = 4

class Direction(Enum):
    Horizontal = 0
    Vertical = 1    

class Boat(Enum):
    Fregate = 0
    Destroyer = 1
    Submarine = 2
    Carrier = 3
    Battleship = 4

boat_sizes = {
    Boat.Fregate: 2,
    Boat.Destroyer: 3,
    Boat.Submarine: 3,
    Boat.Carrier: 4,
    Boat.Battleship: 5
}

class MouseButton(Enum):
	Left = 1
	Middle = 2
	Right = 3

class attack_message():
	def __init__(self,player_id_has_been_attacked, x, y):
		self.player_id_has_been_attacked = player_id_has_been_attacked
		self.x = x
		self.y = y

class attack_result_message():
	def __init__(self,attacked_player, x, y, boat_hit : bool):
		self.attacked_player = attacked_player
		self.x = x
		self.y = y
		self.boat_hit = boat_hit

class turn_over_message():
	def __init__(self,player_id):
		self.player_id = player_id

class boat_choice_message():
	def __init__(self, player_id, boat : Boat):
		self.player_id = player_id
		self.boat = boat

class boat_placed_message():
	def __init__(self, player_id, boat : Boat):
		self.player_id = player_id
		self.boat = boat

class message_subscriber(ABC):
	@abstractmethod
	def receive(self, message_type, data):
		pass
	
class render_item(message_subscriber):
	""" 
	This is the baseclass of every render item.
	"""
	pool = None

	@abstractmethod
	def draw(self):
		None

	@abstractmethod
	def update(self):
		None

	def set_pool(self,pool):
		self.pool = pool

class mouse_listener(ABC):
	"""
	Implement this class to listen to mouse events distributed by the mouse_pool
	"""
	@abstractmethod
	def mouse_click(self, event, button: MouseButton):
		pass		

class mouse_pool():
	"""
	Register your mouse_listener here to be notified of mouse events
	"""
	mouse_event_listeners = []

	def add_mouse_listener(self,e):
		self.mouse_event_listeners.append(e)

	def mouse_down(self,x,y):
		pressed_button = pygame.mouse.get_pressed()
		button = MouseButton.Left if pressed_button[0] else (MouseButton.Middle if pressed_button[1] else (MouseButton.Right if pressed_button[2] else None))
		for listener in self.mouse_event_listeners:
			listener.mouse_click([x,y],button)
	def mouse_up(self,x,y):
		self.mouse_down(x,y)

class render_pool(mouse_pool):
	elements : render_item = []

	def add(self,element):
		assert isinstance(element, render_item)
		element.set_pool(self)

		if isinstance(element, mouse_listener):
			self.add_mouse_listener(element)

		self.elements.append(element)

	def remove(self,element):
		self.elements.remove(element)
		if isinstance(element, mouse_listener):
			self.mouse_event_listeners.remove(element)	
		element.set_pool(None)

	def clear(self):
		for idx, element in enumerate(self.elements):
			if isinstance(element, mouse_listener):
				self.mouse_event_listeners.remove(element)	
			self.elements[idx].set_pool(None)
		self.elements = []
		self.mouse_event_listeners = []

	def render(self):
		for element in self.elements:
			element.draw() 

	def update(self):
		for element in self.elements:
			element.update() 
	
	def render_and_update(self):
		for element in self.elements:
			element.update() 
			element.draw()

class audio_manager():
	audiofiles = {}
	last_id = 0
	def __init__(self):
		pass
	def add(self,audiofile):
		try:
			self.audiofiles[self.last_id] = pygame.mixer.Sound(audiofile)
			self.last_id += 1 
			return self.last_id-1
		except:
			return -1
	def play(self,id):
		self.audiofiles[id].play()

	def loop(self):
		return 1		



class message_center():
	subscribers = {}

	def subscribe(self, message_type, listener : message_subscriber):
		if message_type not in self.subscribers:
			self.subscribers[message_type] = []
		self.subscribers[message_type].append(listener)

	def unsubscribe(self, message_type, listener : message_subscriber):
		if message_type in self.subscribers:
			self.subscribers[message_type].remove(listener)
			if not self.subscribers[message_type]:
				del self.subscribers[message_type]

	def publish(self, message_type, data=None):
		assert(message_type in [turn_over_message.__name__, attack_message.__name__, attack_result_message.__name__, "game_over", boat_choice_message.__name__, boat_placed_message.__name__])
		try:
			print(f"Publishing message of type {message_type} with data {vars(data)}")
		except:
			print(f"Publishing message of type {message_type} with data {data}")
		if message_type in self.subscribers:
			for listener in self.subscribers[message_type]:
				listener.receive(message_type, data)

message_center_instance = message_center()