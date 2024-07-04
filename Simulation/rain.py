import pygame, random

class Droplet :
	
	# Droplets will be rendered as lines
	LINE_WIDTH_MIN : int = 1
	LINE_WIDTH_MAX : int = 1

	LINE_HEIGHT_MIN : int = 32
	LINE_HEIGHT_MAX : int = 64

	ACCEL_DUE_TO_GRAV : float = 9.81

	def __init__(self, x_max : int, foreground_level : float = 1.0) -> None :
		
		# The smallest mass of a droplet can be estimated to be 4e-8 Kg
		# The greatest mass of a droplet can be estimated to be 0.0003 Kg (= 30 000e-8 Kg)
		
		self.mass : float = random.randrange(4, 30000) * 1e-8

		# The value of the droplet on the x-axis is randomised
		self.x_max : int = x_max
		self.x     : int = random.randint(0, self.x_max)

		# The height of rainclouds above ground varies

		# Low  level -> less or equal to 1981.2 m
		# Mid  level -> from 1981.2 m to 4572.0 m
		# High level -> more or equal to 4572.0 m

		# However, estimations will be used instead
		# Because they are easier to work with

		#   | --- Low --- | --- Mid --- | --- High --- |
		# 1500 m        2000 m        4500 m         5000 m

		# Moreover,
		# Heavier clouds (> average droplet mass ) are lower in altitude
		# Than lighter clouds (< average droplet mass )

		# height ∝ (1 / droplet mass)
		# height = (k / droplet mass)

		# The average mass of a droplet is 0.000150002 Kg
		# The average height from the range of heights is 3250 m

		# Therefore,
		# k = 0.525007 Kg(m)

		self.y : float = - 0.525007 / self.mass

		# Droplets on lower planes will fall slower
		self.accel : float = foreground_level * self.ACCEL_DUE_TO_GRAV

		# For rendering,
		# The greater the mass of the droplet, the more pixels it takes

		self.w : int = int(self.mass / (30000e-8 - 4e-8)) * self.LINE_WIDTH_MAX

		# Without this snippet of code, line will not be rendered
		if self.w < self.LINE_WIDTH_MIN :
			self.w = self.LINE_WIDTH_MIN

		# The faster the droplet falls, the longer the line to draw it is 
		self.h : int = int(self.accel / self.ACCEL_DUE_TO_GRAV) * self.LINE_HEIGHT_MAX

		# Without this snippet of code, line will not be rendered
		if self.h < self.LINE_HEIGHT_MIN :
			self.h = self.LINE_HEIGHT_MIN

	def fall(self) -> None :

		# Accelerates droplets
		self.y += self.accel

	def draw(self) -> None :

		# Note that screen is globally defined

		# Draws droplet
		pygame.draw.line(
			surface   = screen,
			color     = (10, 50, 75),
			start_pos = (self.x, self.y - self.h),
			end_pos   = (self.x, self.y),
			width     = self.w
			)

		# Resets the position of the droplet if it goes offscreen
		if self.y > screen.get_height() :

			self.x : int = random.randint(0, self.x_max)

			# Adds a random factor
			# Else, rainfall would follow a static pattern which is not natural
			self.y : float = (- 0.525007 / self.mass) * (random.randint(5, 10) / 10)

def get_rain(x_max : int, n_droplets : int = 100, n_foreground_levels : int = 1) -> list[Droplet] :

		# Creates Droplet objects
		return [
			
			Droplet(x_max = x_max, foreground_level  = 1 - (fg_level / 10))
				for _ in range(n_droplets // n_foreground_levels)
					for fg_level in range(n_foreground_levels)

			]

if __name__ == '__main__' :

	# Screen properties
	screen_x      : int        = 800
	screen_y      : int        = 400
	screen_colour : tuple[int] = (14, 14, 14)

	# Setting up pygame
	pygame.init()
	pygame.display.set_caption(title = "Rain Sim")

	screen : pygame.Surface    = pygame.display.set_mode((screen_x, screen_y))
	clock  : pygame.time.Clock = pygame.time.Clock()

	# Hides cursor
	pygame.mouse.set_visible(False)

	# Setup particles
	rain : list[Droplet]    = get_rain(
		x_max               = screen_x,
		n_droplets          = 1000,
		n_foreground_levels = 2
		)

	# Pygame loop
	simulating : bool  = True

	while simulating :

		# Limits while loop iteration speed in FPS
		clock.tick(120)

		for event in pygame.event.get() :

			# User closes window
			if event.type == pygame.QUIT :
				pygame.quit()
				
				# Ends sim
				simulating = False

		if simulating :
			
			# Draws screen
			screen.fill(screen_colour)

			# Updates droplets
			for i in rain :
				i.fall()
				i.draw()

			# Updates screen
			pygame.display.update()