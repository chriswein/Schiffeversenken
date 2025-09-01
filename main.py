import pygame
from hud import *
from engine import *
from game import *

# pygame constants
width = 1400
height = 720
fps = 30

# pygame initialization
pygame.init()
pygame.mixer.init() 
screen = pygame.display.set_mode((width, height), pygame.SCALED)
clock = pygame.time.Clock()

pygame.display.set_caption("Schiffeversenken")

pool = render_pool()
am = audio_manager()
PLACE = am.add("./sounds/place.wav")
REMOVE = am.add("./sounds/remove.wav")
SHOT = am.add("./sounds/shot.wav")
EXPLOSION = am.add("./sounds/explosion.wav")
CLEAR = am.add("./sounds/clear.wav")
def init():
	hud = HUD(screen, 750, 10)
	pool.add(field(screen, am, [PLACE, REMOVE, CLEAR], hud))
	pool.add(hud)
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
			if event.key == pygame.K_q:
				running = False

	screen.fill((0,0,0))

	pool.render_and_update() # update all elements of the game

	pygame.display.flip()	   

pygame.quit()
