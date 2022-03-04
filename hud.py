import pygame 
from engine import render_item

class HUD(render_item):
	points = 0
	surface = None

	def __init__(self, surface, x = 0, y = 0):
		self.surface = surface
		self.x, self.y = x, y
		pygame.font.init()

	def draw(self):
		font = pygame.font.SysFont("Comic Sans MS", 30)
		image = font.render("Versuche {}".format(self.points), False, (255,255,255))
		self.surface.blit(image, (self.x,self.y))
		#pygame.draw.rect(self.surface,(255,255,255)
		None

	def update(self):
		None	
	
	def add(self):
		self.points += 1
