from math import exp

import pygame, random

def calculate_length_between_2_coords(coords_1 : tuple[int], coords_2 : tuple[int]) -> int :
	
	# Pythagoras theorum
	dx_square : int = pow(abs(coords_1[0] - coords_2[0]), 2)
	dy_square : int = pow(abs(coords_1[1] - coords_2[1]), 2)

	return int(pow((dx_square + dy_square), 0.5))

class Droplet :
	
	# Droplets will be rendered as lines
	LINE_WIDTH_MIN : int = 1
	LINE_WIDTH_MAX : int = 1

	LINE_HEIGHT_MIN : int = 32
	LINE_HEIGHT_MAX : int = 64

	ACCEL_DUE_TO_GRAV : float = 9.81

	def __init__(self, x_max : int, foreground_level : float = 1.0, cursor_influence_radius : int = 0) -> None :
		
		self.foreground_level = foreground_level

		# To simulate the effect of an umbrella
		self.cursor_influence_radius : int = cursor_influence_radius

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
		self.accel : float = self.foreground_level * self.ACCEL_DUE_TO_GRAV

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

		# Push droplets to the side
		if self.cursor_influence_radius :

			# Gets position of the mouse
			mouse_x, mouse_y = pygame.mouse.get_pos()

			# Within range
			dist_from_cursor : int = calculate_length_between_2_coords(coords_1 = (self.x, self.y), coords_2 = (mouse_x, mouse_y))
			
			# The region of force around the cursor is a semi-ellipse
			if (dist_from_cursor <= self.cursor_influence_radius) and (self.y >= mouse_y - (self.cursor_influence_radius // 2)) :

				# Moves droplet according to y = 1 / ln x curve
				
				# Where x : Force to push droplet
				#       y : Distance from cursor

				force : int = int(exp(6 / (dist_from_cursor + 1)) + self.accel)

				# Moves to the right
				if self.x >= mouse_x :
					pass

				# Moves to the left
				else :
					force = -1 * force

				# Moves droplet
				self.x += force

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

def get_rain(x_max : int, n_droplets : int = 100, n_foreground_levels : int = 1, cursor_influence_radius : int = 0) -> list[Droplet] :

		# Creates Droplet objects
		return [
			
			Droplet(x_max = x_max, foreground_level  = 1 - (fg_level / 10), cursor_influence_radius = cursor_influence_radius)
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
	# pygame.mouse.set_visible(False)

	# Default values
	max_n_droplets          : int = 1000
	n_foreground_levels     : int = 2
	cursor_influence_radius : int = int(0.1 * screen_x) 

	# Setup particles
	rain : list[Droplet] = get_rain(
		x_max                   = screen_x,
		n_droplets              = max_n_droplets,
		n_foreground_levels     = n_foreground_levels,
		cursor_influence_radius = 0
		)

	# Pygame loop
	event_toggle : bool = False
	simulating   : bool = True
	umbrella     : bool = False
	fps          : int  = 120

	# Custom event (Called each x frames)
	heavy_rain : int = pygame.USEREVENT + 1
	pygame.time.set_timer(heavy_rain, int(fps * 100))

	while simulating :

		# Limits while loop iteration speed in FPS
		clock.tick(fps)

		for event in pygame.event.get() :

			# User closes window
			if event.type == pygame.QUIT :
				pygame.quit()
				
				# Ends sim
				simulating = False

			# Custom event
			if event.type == heavy_rain :
				
				# Varies rain
				if (event_toggle == False) and (random.choice([True, False])) :
					event_toggle = True

					# 1 : Varies acceleration

					# Generates a random float from 0.75 to 1.25
					accel_variation : float = random.randint(75, 125) / 100

					# Updates acceleration of droplets
					for i in rain :
						i.accel = accel_variation * i.accel

				# Resets droplets
				else :
					event_toggle = False

					# Resets acceleration of droplets
					for i in rain :
						i.accel = i.foreground_level * Droplet.ACCEL_DUE_TO_GRAV

			# Toggle umbrella effect
			if event.type == pygame.MOUSEBUTTONDOWN :
				
				# Activates umbrella effect
				if not umbrella :
					umbrella = True

				# Deactivates umbrella effect
				else :
					umbrella = False

		# Activates umbrella effect gradually
		if (umbrella) and (rain[0].cursor_influence_radius < cursor_influence_radius) :

			for i in rain :
				i.cursor_influence_radius += 1

		# Deactives umbrella effect gradually
		elif (not umbrella) and (rain[0].cursor_influence_radius > 0) :
			
			for i in rain :
				i.cursor_influence_radius -= 1

		if simulating :
			
			# Draws screen
			screen.fill(screen_colour)

			# Updates droplets
			for i in rain :
				i.fall()
				i.draw()

			# Updates screen
			pygame.display.update()