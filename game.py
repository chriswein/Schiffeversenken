import random
import math
from engine import *
import pygame
from pygame import gfxdraw


class field(render_item, mouse_listener):
	""" A board for playing the game on """
	surface, am, audio_ids = None, None, None # Drawing surface, Audio Manager, Audio Ids
	hud = None
	is_turn = True # Indicates wether it is the players turn.
	board = None
	x, y = 0, 0
	width, height = 700, 700
	n = 10 
	radius = (width//n+1)//3
	hits = 0
	maxhits = 0

	def __init__(self, surface, audio_manager_reference, audio_ids, hud):
		self.surface = surface
		self.am = audio_manager_reference
		self.audio_ids = audio_ids
		self.hud = hud
		self.reset()
		self.place_boat((2,1),(2,6))
		self.place_boat((7,1),(9,1))
		self.place_boat((5,3),(5,7))
		self.maxhits = 14

	def reset(self):
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

	def is_hit(self, x, y):
		if self.hud != None:
			if self.board[y][x] == 0: 
				self.hud.add()
		if self.board[y][x] == 2:
			self.hits += 1
			return True
		return False
	
	def place_boat(self, point1, point2):
		""" Places a boat between to points """
		assert(len(point1) > 1 and len(point2) > 1)
		x1,y1 = point1
		x2,y2 = point2
		if y1 == y2:
			for x in range (min(x1,x2), max(x1,x2)+1):
				self.board[y1][x] = 2
			return True
		elif x1 == x2:
			for y in range (min(y1,y2), max(y1,y2)+1):
				self.board[y][x1] = 2
			return True
		else:
			return False

	def draw(self):
		for line in range(1, 11):
			# horizontal lines
			pygame.draw.aaline(
				self.surface,
				(255, 255, 255),
				(0, line*(self.width//self.n)),
				(self.width, line*(self.width//self.n))
			)
			# vertical line
			pygame.draw.aaline(
				self.surface,
				(255, 255, 255),
				(line*(self.width//self.n), 0),
				(line*(self.width//self.n), self.height)
			)

		for y, row in enumerate(self.board):
			for x, col in enumerate(row):
				if col == 1:
					# Boats
					pygame.draw.circle(
						self.surface,
						(255, 255, 255),
						((self.width//self.n)//2
							+x*(self.width//self.n),
						 (self.width//self.n)//2
						 	+y*(self.width//self.n)),
						self.radius 
					)
				elif col == 3:
					# Miss
					pygame.draw.circle(
						self.surface,
						(255, 255, 255),
						((self.width//self.n)//2
							+x*(self.width//self.n),
						 (self.width//self.n)//2
						 	+y*(self.width//self.n)),
						self.radius//2 
					)
					

	def random_setup(self):
		dice,col = random.randint(0,1), random.randint(0, len(self.board)-1)		
		self.place_boat((col, 2), (col, 5))
		col = random.randint(0, len(self.board)-1)		
		self.place_boat((col, 3), (col, 6))
		self.maxhits = 8
	

	def update(self):
		if self.hits == self.maxhits and self.hits != 0:
			self.reset()
			self.am.play(self.audio_ids[2])
			self.hits = 0
			self.hud.reset()
			self.random_setup()

	def mouse_click(self, e):
		x, y = e
		if (
			self.x <= x and x <= self.x+self.width # Is it in Box?
			and
			self.y <= y and y <= self.y+self.height # Is it in Box?
			and
			self.is_turn 
			):
			# the player clicked inside our board
			bx, by = x//(self.width//self.n), y//(self.height//self.n)
			if not self.is_hit(bx,by):
				if not self.board[by][bx] == 1:
					self.board[by][bx] = 3
					self.am.play(self.audio_ids[0])
			else:
				self.board[by][bx] = 1
				self.am.play(self.audio_ids[1])


class board_bridge(render_item):
	boards = []
	def add(self, board):
		self.boards.append(board)

	def attack(self, board, x, y):
		pass
        
	def draw(self):
		None

	def update(self):
		None

	def pool(self,pool):
		self.pool = pool
