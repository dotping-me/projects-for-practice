from turtle import speed, color, bgcolor, goto, done

# For the heart
from math import sin, cos, pow

def calc_heart_coords(centre : tuple[int] = (0, 0), n_points : int = 6000, scale_factor : int = 1) -> list[tuple[float]] :
	
	# Heart function
	# Calculated by iterating through a range of t values

	# Note that heart is drown bigger than given radius

	heart_coords : list[tuple[int]] = []

	for t in range(n_points) :
		
		x : float = 15 * pow(sin(t), 3)
		y : float =	(12 * cos(t)) - (5 * cos(2 * t)) - (2 * cos(3 * t)) - cos(4 * t)

		heart_coords.append(((centre[0] + x) * scale_factor, (centre[1] + y) * scale_factor))

	return heart_coords

if __name__ == '__main__' :
	
	# Setting the drawing attributes
	speed(9999)
	color('red')

	# Setting the background colour
	bgcolor('black')

	# Calculates coordinates
	heart_coords : list[tuple[int]] = calc_heart_coords(scale_factor = 15)

	for x, y in heart_coords :
		goto(x, y)
		
		# Resets
		goto(0, 0)

	# Stops drawing
	done()