import pygame 
from engine import render_item

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
		#pygame.draw.rect(self.surface,(255,255,255)
		None

	def update(self):
		None	
	
	def add_miss(self):
		self.misses += 1

	def add_hit(self):
		self.points += 1

	def reset(self):
		self.points = 0
