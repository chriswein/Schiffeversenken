import math
from engine import *
import pygame
from pygame import gfxdraw
import random


class field(render_item, mouse_listener):
	""" A board for playing the game on """
	surface, am, audio_ids = None, None, None
	board = None
	x, y = 0, 0
	width, height = 700, 700
	n = 10

	def __init__(self, surface, audio_manager_reference, audio_ids):
		self.surface = surface
		self.am = audio_manager_reference
		self.audio_ids = audio_ids
		self.reset()

	def reset(self):
		self.board = [
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
			[0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
		]

	def isHit(self, x, y):
		return True

	def draw(self):
		for line in range(1, 11):
			pygame.draw.aaline(
				self.surface,
				(255, 255, 255),
				(0, line*(self.width//self.n)),
				(self.width, line*(self.width//self.n))
			)
			pygame.draw.aaline(
				self.surface,
				(255, 255, 255),
				(line*(self.width//self.n), 0),
				(line*(self.width//self.n), self.height)
			)
		for y, row in enumerate(self.board):
			for x, col in enumerate(row):
				if col == 1:
					pygame.draw.circle(
						self.surface,
						(255, 255, 255),
						((self.width//self.n)//2
							+x*(self.width//self.n),
						 (self.width//self.n)//2
						 	+y*(self.width//self.n)),
						25
					)

	def update(self):
		pass

	def mouse_click(self, e):
		x, y = e
		if (self.x <= x and x <= self.x+self.width and
				self.y <= y and y <= self.y+self.height):
			# the player clicked inside our board
			bx, by = x//(self.width//self.n), y//(self.height//self.n)
			if self.board[by][bx] == 0:
				self.board[by][bx] = 1
				self.am.play(self.audio_ids[0])
			else:
				self.board[by][bx] = 0
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