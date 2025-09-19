import pygame
from ai import AI
from hud import *
from engine import *
from game import *
from player import *

# pygame constants
width = 1421
height = 720
fps = 60

# pygame initialization
pygame.init()
pygame.mixer.init() 
screen = pygame.display.set_mode((width, height), pygame.SCALED)
clock = pygame.time.Clock()

class GameState(enumerate):
	EnterBuildingPhase = 0
	InBuildingPhase = 1
	GamePhase = 2

phase = GameState.EnterBuildingPhase

pygame.display.set_caption("Schiffeversenken")

pool = render_pool()
audiomng = audio_manager()
PLACE = audiomng.add("./sounds/place.wav")
REMOVE = audiomng.add("./sounds/remove.wav")
SHOT = audiomng.add("./sounds/shot.wav")
EXPLOSION = audiomng.add("./sounds/explosion.wav")
CLEAR = audiomng.add("./sounds/clear.wav")
hud = HUD(screen, 750, 10)
placement_HUD = Placement_HUD(screen, 50, 10)
f = field(screen, audiomng, [PLACE, REMOVE, CLEAR, EXPLOSION], hud)
pf = player_field(screen, audiomng, [SHOT, EXPLOSION], hud)
pfx = pf.x
def init():
	pool.add(f)
	pool.add(pf)
	pool.add(hud)
init()

ai = AI()

## Game loop

def handle_building_phase_ui():
	pf.x = width//2 - pf.width//2

def handle_game_phase_ui():
	pf.x = pfx

class GameOverListener:
	def receive(message_type, data):
		global phase
		global pf
		match message_type:
			case "game_over":
				print("Game Over received in GameOverListener")
				phase = GameState.EnterBuildingPhase
				pf.is_turn = True

def handle_phase_transition():
	global phase
	if phase == GameState.EnterBuildingPhase:
		if pf.is_placing_boats(): # Enable building phase
			pf.is_turn = True
			pool.clear()
			handle_building_phase_ui()
			pool.add(pf)
			pool.add(Placement_HUD(screen,50,10))
			phase = GameState.InBuildingPhase
			print("Exiting building phase")
	else:
		if phase == GameState.InBuildingPhase: # Lave building phase
			if not pf.is_placing_boats():
				phase = GameState.GamePhase
				handle_game_phase_ui()
				f.is_turn = True
				pf.is_turn = False
				pool.clear()
				pool.add(f)
				pool.add(pf)
				pool.add(hud)

running = True
message_center_instance.subscribe("game_over", GameOverListener)

while running:

	clock.tick(fps)	
	
	handle_phase_transition()

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
