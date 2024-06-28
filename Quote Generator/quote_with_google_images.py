from PIL import Image, ImageDraw, ImageFont
from io  import BytesIO

import requests, random

# For Quote requests
__APININJAS_API_KEY : str = ""
__APININJAS_API_URL : str = "https://api.api-ninjas.com/v1/quotes" # Already includes GET request endpoint

# For Google Images requests
__SERPAPI_API_KEY : str = ""
__SERPAPI_API_URL : str = "https://serpapi.com/search?engine=google_images" # Already includes GET request endpoint

# For creating the gradient image mask
__GRADIENT_BASE_RGBA    : tuple[int] = (16, 16, 16, 200)
__GRADIENT_H_PERCENTAGE : int        = 1

# For writing out the quote (font, ...)
__BASE_FONT                 : str        = "https://github.com/dotping-me/fonts/blob/main/HelveticaMediumItalic.ttf?raw=true"
__BASE_FONT_SIZE            : int        = 32
__BASE_FONT_FILL            : tuple[int] = (253, 234, 122, 255)
__LINE_TO_IMAGE_WIDTH_RATIO : float      = 0.75
__MAX_CHARACTERS_PER_LINE   : int        = 80

def get_random_quote(category : str = "") -> dict[str, str] :
	print(f"\n--- Random Quote ---\n")

	try :

		# 📜📜📜 
		# GET request
		print(f"GET | Quote from [{__APININJAS_API_URL}]")
		
		quote_request : dict[str, str] = (requests.get(url = __APININJAS_API_URL, headers = {"X-Api-Key" : __APININJAS_API_KEY}, params = {"category" : category}).json())[0]
		print(f"√√√ | Successful!\n\nQuote (By '{quote_request['author']}' about '{quote_request['category']}') :\n{quote_request['quote']}")

		# 😐😐😐
		# Sometimes, quote doesn't have a '.' at the end
		# Tsk...

		# Adds '.' at the end of quote
		if "." not in quote_request["quote"] :
			quote_request["quote"] = f"{quote_request['quote']}."

		return quote_request

	except Exception as E :

		print(f"!!! | {E.__class__.__name__}")
		exit()

def get_random_image(query : str, page : int = 0) -> list[dict] :
	print(f"\n--- Random Images ---\n\nSearch term :\n{query}")

	try :
		
		# 🖼🖼🖼
		# GET request

		# Requests for only 1 page (= 100 images)
		images_json : list[dict] = requests.get(
			url     = __SERPAPI_API_URL,
			params  = {

				# Required
				"engine"  : "google_images",
				"api_key" : __SERPAPI_API_KEY,
				"q"       : query,

				# Optional
				"safe"   : "active",
				"filter" : 0,
				"ijn"    : page,
			}

			).json()

		# Extract only images
		return images_json["images_results"]

	except Exception as E :

		print(f"!!! | {E.__class__.__name__}")
		exit()

def find_hcf(x : int, y : int) -> int :
	
	# Finds the maximum value that the HCF could have
	if x < y :
		max_hcf_range : int = x

	else :
		max_hcf_range : int = y

	# Finds HCF	
	for i in range(max_hcf_range + 1) :
		
		# Starts backwards ((max_hcf_range + 1) -> 0)
		factor : int = abs((max_hcf_range + 1) - i)

		# Returns first factor that can divide both numbers
		if (x % factor == 0) and (y % factor == 0) :
			return factor

	# Failed to find HCF
	return -1

def filter_images(images_json : list[dict], min_width = 1000, aspect_ratio : str = "Any") -> list[dict] :
	# Returns a list of images (JSON objects) that meet specific criterias

	filtered_images_json : list[dict] = []

	for json in images_json :
		is_this_json_valid : bool = True

		# 1 : Filters out images that are licensable
		if "tag" in json :
			if json["tag"] == "Licensable" :
				is_this_json_valid = False

		# 2 : Filters out images that are products
		if json["is_product"] == True :
			is_this_json_valid = False

		# 3 : Filters out images that don't meet specific modes/orientations
		if (aspect_ratio != "Any") and ("original_width" in json) :
			
			# 3.1 : Filters out images that are too small
			if json["original_width"] < min_width :
				is_this_json_valid = False

			# 3.2 : Filters out images that are not portraits
			if aspect_ratio.lower() == "p" :
				if (json["original_height"] < json["original_width"]) :
					is_this_json_valid = False

			# 3.3 : Filters out images that are not landscapes
			elif aspect_ratio.lower() == "l" :
				if (json["original_width"] < json["original_height"]) :
					is_this_json_valid = False

			# 3.3 : Filters out images that don't meet aspect ratio
			else :

				# Calculates aspect ratio
				hcf : int = find_hcf(x = json["original_width"], y = json["original_height"])
				ar  : str = f"{json['original_width'] // hcf}:{json['original_height'] // hcf}" # Integer division so that calculated values are not floats (hence, don't contain ".0")

				# In the case where no hcf was found,
				# This condition will evaluate to True

				if ar != aspect_ratio :
					is_this_json_valid = False

		# 4 : Filters out images that don't have a valid link
		if "original" in json :
			if json["original"][-4] != "." :
				
				# For extensions like ".jpeg", ...
				if json["original"][-5] != "." :
					is_this_json_valid = False

		else :
			is_this_json_valid = False

		# 5 : Filters out images that are not provided by secure websites
		if json["original"][:5] != "https" :
			is_this_json_valid = False

		# Appends JSON if it passed all checks
		if is_this_json_valid :
			filtered_images_json.append(json)

	return filtered_images_json

def create_gradient_mask_img(mask_wh : tuple[int], base_gradient_rgba : tuple[int]) -> Image :
	
	# 🎭
	# Creates mask
	gradient_mask_img : Image = Image.new("RGBA", mask_wh, __GRADIENT_BASE_RGBA)

	# Iterates through each row of pixels
	# Reduces alpha channel value of pixels
	# Depending on their y-value past a certain threshold

	pixel_map = gradient_mask_img.load()

	for y in range(mask_wh[1]) :

		# Changes alpha channel value
		alpha_value            : int        = int((y / mask_wh[1]) * __GRADIENT_BASE_RGBA[3])
		new_pixel_rgba_for_row : tuple[int] = (pixel_map[0, y][0], pixel_map[0, y][1], pixel_map[0, y][2], alpha_value)

		# Changes rgba of each pixel in this row
		for x in range(mask_wh[0]) :
			pixel_map[x, y] = new_pixel_rgba_for_row

	return gradient_mask_img

def breakdown_quote_into_phrases(quote_content) -> list[str] :
	print(f"\n--- Parsing Quote ---\n\nQuote :\n{quote_content}\n\nPhrases :")

	# Characters that indicates the end of a phrase
	seperators : list[str] = [".", ",", "!", "?", ":", ";", "—"]

	quote_phrases     : list[str] = []
	this_phrase_start : int       = 0

	for i, character in enumerate(quote_content) :
		
		# End of phrase found
		if character in seperators :
			quote_phrases.append(quote_content[this_phrase_start : i + 1])
			this_phrase_start = i + 1

	# Remove whitespace at the start of phrase
	for i, phrase in enumerate(quote_phrases) :
		if phrase[0] == " " :
			quote_phrases[i] = phrase[1:]

		print(f"{i + 1}. {quote_phrases[i]}")

	# Special case for "..."
	# ... = ["foo.", ".", "."]
	for i, phrase in enumerate(quote_phrases) :
		
		# Not first phrase
		if i != 0 :
			if phrase == "." :
				quote_phrases[i - 1] = f"{quote_phrases[i - 1]}."
				quote_phrases[i]     = ""

	quote_phrases = [i for i in quote_phrases if i]

	# Processes phrases
	print(f"\n--- Processing Phrases ---")
	i : int = 0

	while i < len(quote_phrases) :
		phrase                 : str = quote_phrases[i]
		n_chars_in_this_phrase : int = len(phrase)

		if phrase != "" :
			print(f"\nProcessing ({n_chars_in_this_phrase} chars):\n>>> {phrase}")

			if i < (len(quote_phrases) - 1) :
				
				# New phrase doesn't exceed max words per line if joined with next phrase
				n_chars_in_next_phrase : int = len(quote_phrases[i + 1])

			else :

				# Disables ability to join phrases
				n_chars_in_next_phrase : int = 99999

			# Specific case scenario
			# Quote is only one phrase that exceeds max words per line

			# Or 

			# Too long
			if ((len(quote_phrases) == 1) and (n_chars_in_this_phrase > __MAX_CHARACTERS_PER_LINE)) or (n_chars_in_this_phrase > __MAX_CHARACTERS_PER_LINE) :

				# Split phrase into 2
				print(f">>> Too long!\n>>> Splitting phrase in 2!")
				median : int = (len(phrase.split(" ")) + 1) // 2
				
				phrase_half_1 : str = " ".join(phrase.split(" ")[:median + 1])
				phrase_half_2 : str = " ".join(phrase.split(" ")[median + 1:])

				# Trims current phrase to its first half
				quote_phrases[i] = phrase_half_1

				# Adds next half of phrase in the list

				# Last phrase
				if i == (len(quote_phrases) - 1) :
					quote_phrases.append(phrase_half_2)

				# Continue list afterwards
				else :
					quote_phrases = quote_phrases[:i + 1] + [phrase_half_2] + quote_phrases[i + 1:]

			# Too short
			elif (i < (len(quote_phrases) - 1)) and (n_chars_in_this_phrase + n_chars_in_next_phrase < __MAX_CHARACTERS_PER_LINE) :
								
				# Joins phrases
				print(f">>> Too short!\n>>> Joining this phrase with next phrase!\n>>> Chars : {n_chars_in_this_phrase} + {n_chars_in_next_phrase} = {n_chars_in_this_phrase + n_chars_in_next_phrase} (< {__MAX_CHARACTERS_PER_LINE})")
				quote_phrases[i] = f"{quote_phrases[i]} {quote_phrases[i + 1]}"

				# Removes next phrase from list
				# Because it already exists in newly joined phrase
				quote_phrases = quote_phrases[:i + 1] + quote_phrases[i + 2:]

				# Next pass will process newly joined phrase
				i -= 1

			else :
				pass

		# Processes next phrase
		i += 1

	# Removes empty phrases
	quote_phrases = [i for i in quote_phrases if i]

	print(f"\n--- Processed Phrases ---\n")
	for i, phrase in enumerate(quote_phrases) :
		print(f"{i + 1}. {phrase} ({len(phrase)})")

	return quote_phrases

def calculate_rendered_text_wh(text : str, font : ImageFont) -> tuple[int] :
	
	# This is a temporary/buffer image
	render_text_on : Image = Image.new("RGBA", (0, 0), (255, 255, 255, 255))

	draw_layer          : ImageDraw = ImageDraw.Draw(render_text_on)
	space_taken_by_text : list[int] = draw_layer.textbbox(xy = (0, 0), text = text, font = font)

	text_w : int = space_taken_by_text[2] - space_taken_by_text[0]
	text_h : int = space_taken_by_text[3] - space_taken_by_text[1]

	return (text_w, text_h)

def fit_text_into_width(text : str, width_allocated : int, font_path : str, starting_font_size : int = 32) : # -> tuple[(str | ImageFont), int]
	print(f"\n--- Calculating Ideal Font Size ---\n")

	# Finds the maximum font size for text to fit into entire width
	current_font_size : int = starting_font_size

	while True :

		# For locally installed fonts
		if "\\" in font_path :
			font_file = font_path

		# For online paths (obtained through requests)
		else :
			font_request = requests.get(__BASE_FONT)
			font_file    = BytesIO(font_request.content)
		
		# Inits PIL font
		font = ImageFont.truetype(font_file, current_font_size)

		# Calculates the width taken by text with this font size
		text_w, _ = calculate_rendered_text_wh(text = text, font = font)
		
		# It's impossible for the text to fit into all the width 100% of the time
		# If the text occupies a % of the allocated width, font size is deemed good enough

		if text_w == width_allocated :
			print(f"With {current_font_size}px font size,\nText ({len(text)}) takes up {text_w}px out of {width_allocated}px ({round((text_w / width_allocated) * 100, 1)} %)\n")
			return font, current_font_size

		elif (text_w >= int(0.75 * width_allocated)) and (text_w <= width_allocated) :
			print(f"With {current_font_size}px font size,\nText ({len(text)}) takes up {text_w}px out of {width_allocated}px ({round((text_w / width_allocated) * 100, 1)} %)\n")
			return font, current_font_size

		# Too small
		elif text_w < width_allocated :
			current_font_size += 1

		# Too big
		elif text_w > width_allocated :
			current_font_size -= 1

		else :
			pass

def create_quote_img(width : int, quote_phrases : list[str], font_quote : ImageFont, quote_author : str, font_author : ImageFont, line_gap : int) -> Image :
	
	# Calculates the size of each phrase
	quote_phrases_wh : list[tuple[int]] = []

	for i in quote_phrases :
		quote_phrases_wh.append(calculate_rendered_text_wh(text = i, font = font_quote))

	# Calculates the size of the author's name
	if quote_author :
		quote_phrases_wh.append(calculate_rendered_text_wh(text = quote_author, font = font_author))

	# Calculates y gap to center quote afterwards
	height : int = sum([i[1] for i in quote_phrases_wh])
	height      += len(quote_phrases_wh) * line_gap

	# Creates image
	quote_img : Image = Image.new("RGBA", (width, height), (0, 0, 0, 0))

	# Pastes text
	draw_layer : ImageDraw = ImageDraw.Draw(quote_img)

	for i, phrase in enumerate(quote_phrases) :

		# Centers text
		text_x : int = (width - quote_phrases_wh[i][0]) // 2
		text_y : int = (i * line_gap) + sum([j[1] for j in quote_phrases_wh[:i]])

		# Draws text
		draw_layer.text(
			xy   = (text_x, text_y),
			text = phrase,
			font = font_quote,
			fill = __BASE_FONT_FILL
			)

	# Pastes author name
	if quote_author :

		# Centers text
		text_x : int = (width - quote_phrases_wh[-1][0]) // 2
		text_y : int = ((len(quote_phrases_wh) - 1) * line_gap) + sum([j[1] for j in quote_phrases_wh[:-1]])

		# Lowers opacity of text
		fill_author : tuple[int] = (__BASE_FONT_FILL[0], __BASE_FONT_FILL[1], __BASE_FONT_FILL[2], int(0.6 * __BASE_FONT_FILL[3]))

		# Draws text
		draw_layer.text(
			xy   = (text_x, text_y),
			text = quote_author,
			font = font_author,
			fill = fill_author
			)

	return quote_img

def make_quote() -> Image :
	
	# 📜🎲
	# Gets random quote from API
	quote_content, quote_author, quote_category = list(get_random_quote().values()) # -> dict[str, str]

	# 🖼🎲
	# Gets random photo from Google Images
	images_json : list[dict] = get_random_image(query = "Sunset aesthetic 16:9")

	# Filters images from requests
	filtered_images_json : list[dict] = filter_images(images_json = images_json, aspect_ratio = "16:9")

	if not filtered_images_json :
		print("\nNo valid Google Images found!")
		exit()

	# Chooses a random photo
	while True :

		try :
			google_image_url : str = random.choice(filtered_images_json)["original"]

			print(f"\n--- Selected Image --- \n\n{google_image_url}")
			google_image_img : Image = Image.open(requests.get(url = google_image_url, stream = True).raw)

			break

		# In case PIL cannot identify the chosen image
		except :
			pass

	# 👓👓👓
	# Create a subtle gradient to overlay/mask on top of photo
	# So that quote is seperated from photo for better readability

	# Gradient starts from 0 % height to (__GRADIENT_H_PERCENTAGE * 100) % height
	mask_wh           : tuple[int] = google_image_img.size[0], int(__GRADIENT_H_PERCENTAGE * google_image_img.size[1])
	gradient_mask_img : Image      = create_gradient_mask_img(mask_wh = mask_wh, base_gradient_rgba = __GRADIENT_BASE_RGBA)

	# Overlays gradient mask
	mask_y : int = google_image_img.size[1] - mask_wh[1]
	google_image_img.paste(gradient_mask_img, (0, mask_y), mask = gradient_mask_img)

	# Ideally, the quote should take up about 60% of the width
	# Ideally, one phrase takes one line
	quote_phrases : list[str] = breakdown_quote_into_phrases(quote_content = quote_content)

	# Determines font size based on longest phrase
	quote_phrases_lengths : list[int] = [len(i) for i in quote_phrases]
	longest_phrase        : str       = quote_phrases[quote_phrases_lengths.index(max(quote_phrases_lengths))]

	# Determines ideal font size
	font, font_size = fit_text_into_width(
		text               = longest_phrase,
		width_allocated    = int(google_image_img.size[0] * __LINE_TO_IMAGE_WIDTH_RATIO),
		font_path          = __BASE_FONT,
		starting_font_size = __BASE_FONT_SIZE
		)

	# 📜🖼
	# Creates an image of the quote to be pasted on photo

	# Author's name is written in a slightly smaller font
	# Hence, PIL font must be initialised again

	# For locally installed fonts
	if "\\" in __BASE_FONT :
		font_file = __BASE_FONT

	# For online paths (obtained through requests)
	else :
		font_request = requests.get(__BASE_FONT)
		font_file    = BytesIO(font_request.content)
	
	# Inits PIL font
	font_author : ImageFont = ImageFont.truetype(font_file, int(0.7 * font_size))

	quote_img = create_quote_img(
		width         = google_image_img.size[0],
		quote_phrases = quote_phrases,
		font_quote    = font,
		quote_author  = quote_author,
		font_author   = font_author,
		line_gap      = int(0.4 * font_size)
		)

	# Overlays quote onto photo
	quote_y : int = google_image_img.size[1] - int(quote_img.size[1] * 1.25)
	
	google_image_img.paste(quote_img, (0, quote_y), mask = quote_img)
	google_image_img.show()

if __name__ == "__main__" : make_quote()
