from abc import ABC, abstractmethod
import pygame 


#
class render_item(ABC):
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

	def pool(self,pool):
		self.pool = pool

class mouse_listener(ABC):
	"""
	Implement this class to listen to mouse events distributed by the mouse_pool
	"""
	@abstractmethod
	def mouse_click(self, event):
		pass		

class mouse_pool():
	"""
	Register your mouse_listener here to be notified of mouse events
	"""
	mouse_event_listeners = []

	def add_mouse_listener(self,e):
		self.mouse_event_listeners.append(e)

	def mouse_down(self,x,y):
		for listener in self.mouse_event_listeners:
			listener.mouse_click([x,y])
	def mouse_up(self,x,y):
		self.mouse_down(x,y)

class render_pool(mouse_pool):
	elements = []

	def add(self,element):
		assert isinstance(element, render_item)
		element.pool(self)

		if isinstance(element, mouse_listener):
			self.add_mouse_listener(element)

		self.elements.append(element)

	def remove(self,id_element):
		None
	
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
		except():
			return -1
	def play(self,id):
		self.audiofiles[id].play()

	def loop(self):
		return 1		
