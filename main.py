import pygame
from engine import *
from game import *

# pygame constants
width = 1400
height = 720
fps = 60

# pygame initialization
pygame.init()
pygame.mixer.init() 
screen = pygame.display.set_mode((width, height), pygame.SCALED)
clock = pygame.time.Clock()

pygame.display.set_caption("Schiffeversenken")

pool = render_pool()
am = audio_manager()
PLACE = am.add("place.wav")
REMOVE = am.add("remove.wav")
SHOT = am.add("shot.wav")
EXPLOSION = am.add("explosion.wav")
def init():
	pool.add(field(screen, am, [PLACE, REMOVE]))

init()
## Game loop
running = True
while running:

	clock.tick(fps)	

	for event in pygame.event.get(): # event handling
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.MOUSEBUTTONDOWN:
			pool.mouse_down(event.pos[0],event.pos[1])
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_f:
				pygame.display.toggle_fullscreen()

	screen.fill((0,0,0))

	pool.render_and_update() # update all elements of the game

	pygame.display.flip()	   

pygame.quit()
