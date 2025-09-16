import pygame 
from engine import Boat, boat_choice_message, boat_placed_message, mouse_listener, render_item, message_center_instance
from player import player_field

class HUD(render_item):
	points = 0
	misses = 0
	surface = None

	def __init__(self, surface, x = 0, y = 0):
		self.surface = surface
		self.x, self.y = x, y
		pygame.font.init()


	def draw(self):
		font = pygame.font.SysFont("Comic Sans MS", 30)
		text1 = font.render("Daneben: {}".format(self.misses), False, (255,255,255))
		text2 = font.render("Getroffen: {}".format(self.points), False, (255,255,255))
		self.surface.blit(text1, (self.x, self.y))
		self.surface.blit(text2, (self.x, self.y + text1.get_height() + 5))  # 5 Pixel Abstand
		None

	def update(self):
		None	
	
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
	selectable_boats = []
	position_of_boats = {}
	max_text_width = 0
	text_height = 0
	currently_selected_boat : int = None 
	clicked_label : bool = False

	def __init__(self, surface, x = 0, y = 0):
		self.surface = surface
		self.x, self.y = x, y
		self.selectable_boats = [boat for boat in Boat]#list(map(lambda x: x.value, Boat._member_map_.values())) 
		message_center_instance.subscribe(boat_placed_message.__name__, self)
		pygame.font.init()	
	
	def __del__(self):
		message_center_instance.unsubscribe(boat_placed_message.__name__, self)

	def draw(self):
		font = pygame.font.SysFont("Comic Sans MS", 30)
		text1 = font.render("Platzierungsmodus", False, (255,255,255))
		self.surface.blit(text1, (self.x, self.y))
		text2 = font.render("Right click to turn ship 90deg", False, (255,255,255))
		self.surface.blit(text2, (self.x+750, self.y))
		for i, boat in enumerate(self.selectable_boats):
			boat_text = font.render(f"{i+1}: {boat.name}", False, (255,255,255) if i != self.currently_selected_boat else (255,0,0))
			self.max_text_width = max(self.max_text_width, boat_text.get_width())
			self.text_height = boat_text.get_height()
			self.surface.blit(boat_text, (self.x, self.y + text1.get_height() + 5 + i * (boat_text.get_height() + 5)))
			if boat not in self.position_of_boats:
				self.position_of_boats[boat] = (self.x, self.y + text1.get_height() + 5 + i * (boat_text.get_height() + 5))
		#pygame.draw.rect(self.surface,(255,255,255)
		None

	def get_selected_boat(self, x,y) -> int | None:
		assert isinstance(x, int) and isinstance(y, int), "x and y must be integers"

		for key, value in self.position_of_boats.items():
			text_x, text_y = value
			if (
				text_x <= x <= text_x + self.max_text_width
				and
				text_y <= y <= text_y + self.text_height
			):
				return key.value
		return None
	
	def mouse_click(self, event, button):
		if self.currently_selected_boat is not None and not self.clicked_label:
			key = self.selectable_boats[self.currently_selected_boat]
			self.clicked_label = True
			message_center_instance.publish(boat_choice_message.__name__, boat_choice_message(player_field.__name__, key))


	def update(self):
		x,y = pygame.mouse.get_pos()
		if(self.get_selected_boat(x,y) is not None and not self.clicked_label):
			pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
			self.currently_selected_boat = self.get_selected_boat(x,y)
		else:
			pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
			# self.currently_selected_boat = None
	
	def receive(self, message_type, data):
		match message_type:
			case boat_placed_message.__name__:
				if data.player_id == player_field.__name__:
					self.currently_selected_boat = None
					self.clicked_label = False