from PIL import Image, ImageDraw, ImageFont
from io  import BytesIO

# For video manipulation
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

import requests, random, time, os

# Already includes GET request endpoint
__QUOTABLE_API_URL = "https://api.quotable.io/quotes/random"

# Already includes GET request endpoint
__PEXELS_API_KEY       = "YOUR API KEY HERE"
__PEXELS_API_VIDEO_URL = "https://api.pexels.com/videos/search"

__GRADIENT_BASE_RGBA    = (16, 16, 16, 24)
__GRADIENT_H_PERCENTAGE = 1

__BASE_FONT                 = "https://github.com/dotping-me/fonts/blob/main/HelveticaMediumItalic.ttf?raw=true"
__BASE_FONT_SIZE            = 96
__BASE_FONT_FILL            = (253, 234, 122, 255)
__LINE_TO_IMAGE_WIDTH_RATIO = 0.75
__MAX_CHARACTERS_PER_LINE   = 80

def get_random_quote() :
	print(f"\n--- Random Quote ---\n")

	try :

		# 📜📜📜 
		# GET request
		print(f"GET | Quote from [{__QUOTABLE_API_URL}]")
		
		quote_request = (requests.get(__QUOTABLE_API_URL).json())[0]
		print(f"√√√ | Successful!\n\nQuote :\n{quote_request['content']}")


		# 😐😐😐
		# Sometimes, quote doesn't have a '.' at the end
		# Tsk...
		if "." not in quote_request["content"] :
			return f"{quote_request['content']}.", quote_request["author"]

		else :
			return quote_request["content"], quote_request["author"]

	except Exception as E :

		print(f"!!! | {E.__class__.__name__}")
		exit()

def get_random_video(query = "Random", page = 1, per_page = 15) :
	print(f"\n--- Random Videos ---\n\nSearch term :\n{query}")

	try :

		# 🖼🖼🖼
		# GET request

		# 🖼➕➕
		# Requests multiple pages for more videos!!!
		pexels_request = []

		pexels_request.append(
			requests.get(
				url     = __PEXELS_API_VIDEO_URL,
				headers = {"Authorization" : __PEXELS_API_KEY},
				params  = {"query" : query, "orientation" : "landscape", "page" : page, "per_page" : per_page}
				).json()
			)

		print(f"√√√ | Successful!")

		# 🗃 👉 📂📂📂
		# Creates a list of urls (for videos from GET request)
		pexels_videos_json = []

		for i in pexels_request :
			for j in i["videos"] :
				pexels_videos_json.append(j)

		# Extracts highest quality videos
		high_quality_url = []

		for json in pexels_videos_json :
			video_variants_sizes = [i["size"] for i in json["video_files"]]
			
			# Appends link to video with greatest size
			high_quality_url.append(json["video_files"][video_variants_sizes.index(max(video_variants_sizes))]["link"])

		# Chooses random landscape video 🖼🎲
		random_video_json_i = random.randrange(len(pexels_videos_json))
		random_video_url    = high_quality_url[random_video_json_i]
		random_video_alt    = pexels_videos_json[random_video_json_i]["url"]
		random_video_length = pexels_videos_json[random_video_json_i]["duration"]

		# Finds the file extension of the video
		extension = pexels_videos_json[random_video_json_i]["video_files"][0]["file_type"]
		extension = extension[extension.find("/") + 1:]
		filename  = f"video.{extension}"

		print(f"\n--- Selected Video ---\n\nWriting '{filename}' :\n{random_video_url}")

		# Loads video from url
		pexels_videos_vid = (requests.get(random_video_url)).content

		# Saves video to local storage
		with open(filename, "wb") as f :
			f.write(pexels_videos_vid)

		return filename, random_video_length, VideoFileClip(filename)

	except Exception as E :

		print(f"!!! | {E}")
		exit()

def create_gradient_mask_img(mask_wh, base_gradient_rgba) :
	
	# 🎭
	# Creates mask
	gradient_mask_img = Image.new("RGBA", mask_wh, __GRADIENT_BASE_RGBA)

	# Iterates through each row of pixels
	# Reduces alpha channel value of pixels
	# Depending on their y-value past a certain threshold
	pixel_map = gradient_mask_img.load()

	for y in range(mask_wh[1]) :

		# Changes alpha channel value
		alpha_value            = int((y / mask_wh[1]) * __GRADIENT_BASE_RGBA[3])
		new_pixel_rgba_for_row = (pixel_map[0, y][0], pixel_map[0, y][1], pixel_map[0, y][2], alpha_value)

		# Changes rgba of each pixel in this row
		for x in range(mask_wh[0]) :
			pixel_map[x, y] = new_pixel_rgba_for_row

	return gradient_mask_img

def breakdown_quote_into_phrases(quote_content) :
	print(f"\n--- Parsing Quote ---\n\nQuote :\n{quote_content}\n\nPhrases :")

	# Characters that indicates the end of a phrase
	seperators = [".", ",", "!", "?", ":", ";", "—"]

	quote_phrases    = []
	this_phrase_start = 0

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

	# Processes phrases
	print(f"\n--- Processing Phrases ---")
	
	i = 0
	while i < len(quote_phrases) :
		phrase                 = quote_phrases[i]
		n_chars_in_this_phrase = len(phrase)

		if phrase != "" :
			print(f"\nProcessing ({n_chars_in_this_phrase} chars):\n>>> {phrase}")

			if i < (len(quote_phrases) - 1) :
				
				# New phrase doesn't exceed max words per line if joined with next phrase
				n_chars_in_next_phrase = len(quote_phrases[i + 1])

			else :

				# Disables ability to join phrases
				n_chars_in_next_phrase = 99999

			# Specific case scenario
			# Quote is only one phrase that exceeds max words per line

			# Or 

			# Too long
			if ((len(quote_phrases) == 1) and (n_chars_in_this_phrase > __MAX_CHARACTERS_PER_LINE)) or (n_chars_in_this_phrase > __MAX_CHARACTERS_PER_LINE) :

				# Split phrase into 2
				print(f">>> Too long!\n>>> Splitting phrase in 2!")
				median = (len(phrase.split(" ")) + 1) // 2
				
				phrase_half_1 = " ".join(phrase.split(" ")[:median + 1])
				phrase_half_2 = " ".join(phrase.split(" ")[median + 1:])

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

def calculate_rendered_text_wh(text, font) :
	
	# This is a temporary/buffer image
	render_text_on = Image.new("RGBA", (0, 0), (255, 255, 255, 255))

	draw_layer          = ImageDraw.Draw(render_text_on)
	space_taken_by_text = draw_layer.textbbox(xy = (0, 0), text = text, font = font)

	text_w = space_taken_by_text[2] - space_taken_by_text[0]
	text_h = space_taken_by_text[3] - space_taken_by_text[1]

	return (text_w, text_h)

def create_quote_img(width, quote_phrases, font_quote, quote_author, font_author, line_gap) :
	
	# Calculates the size of each phrase
	quote_phrases_wh = []

	for i in quote_phrases :
		quote_phrases_wh.append(calculate_rendered_text_wh(text = i, font = font_quote))

	# Calculates the size of the author's name
	if quote_author :
		quote_phrases_wh.append(calculate_rendered_text_wh(text = quote_author, font = font_author))

	# Calculates y gap to center quote afterwards
	height  = sum([i[1] for i in quote_phrases_wh])
	height += len(quote_phrases_wh) * line_gap

	# Creates image
	quote_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

	# Pastes text
	draw_layer = ImageDraw.Draw(quote_img)

	for i, phrase in enumerate(quote_phrases) :

		# Centers text
		text_x = (width - quote_phrases_wh[i][0]) // 2
		text_y = (i * line_gap) + sum([j[1] for j in quote_phrases_wh[:i]])

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
		text_x = (width - quote_phrases_wh[-1][0]) // 2
		text_y = ((len(quote_phrases_wh) - 1) * line_gap) + sum([j[1] for j in quote_phrases_wh[:-1]])

		# Lowers opacity of text
		fill_author = (__BASE_FONT_FILL[0], __BASE_FONT_FILL[1], __BASE_FONT_FILL[2], int(0.6 * __BASE_FONT_FILL[3]))

		# Draws text
		draw_layer.text(
			xy   = (text_x, text_y),
			text = quote_author,
			font = font_author,
			fill = fill_author
			)

	return quote_img

def paste_image_onto_video(img, vid, start_time, last_for) : 

	# img is an Image object and vid is a VideoFileClip object
	
	# Saves image to local storage
	img.save(
		f"img_to_paste_onto_vid.png",
		quality  = 100,
		optimize = True
		)

	# Pastes image onto video
	img_clip  = ImageClip(f"img_to_paste_onto_vid.png").set_start(start_time).set_duration(start_time + last_for)
	composite = CompositeVideoClip([vid, img_clip])

	# Deletes image
	os.remove(f"img_to_paste_onto_vid.png")

	return composite

if __name__ == "__main__" :

	# 📜🖼🎲
	# Random resources

	# Gets random quote from API
	quote_content, quote_author = get_random_quote()

	# Gets random video from pexels API
	filename, duration, pexels_videos_vid = get_random_video(query = "Nature Aesthetic", page = random.randrange(10))

	# 👓👓👓
	# Create a subtle gradient to overlay/mask on top of photo
	# So that quote is seperated from photo for better readability

	# Gradient starts at 80% down the photo (80% y value)
	mask_wh           = pexels_videos_vid.size[0], int(__GRADIENT_H_PERCENTAGE * pexels_videos_vid.size[1])
	gradient_mask_img = create_gradient_mask_img(mask_wh = mask_wh, base_gradient_rgba = __GRADIENT_BASE_RGBA)

	# Ideally, the quote should take up about 60% of the width
	# Ideally, one phrase takes one line
	quote_phrases = breakdown_quote_into_phrases(quote_content = quote_content)

	# Determines font size based on longest phrase
	quote_phrases_lengths = [len(i) for i in quote_phrases]
	longest_phrase        = quote_phrases[quote_phrases_lengths.index(max(quote_phrases_lengths))]

	# Load font from url
	# Font could have been loaded locally but I wanted to do this way
	# 😃😃😃

	font_request = requests.get(__BASE_FONT)

	font_size = __BASE_FONT_SIZE
	font      = ImageFont.truetype(BytesIO(font_request.content), font_size)

	# Determines ideal font size
	text_w, _ = calculate_rendered_text_wh(
		text  = longest_phrase,
		font  = font
		)

	while (text_w > int(__LINE_TO_IMAGE_WIDTH_RATIO * pexels_videos_vid.size[0])) and (font_size >= 1) :
		
		# Modify font
		font_size -= 1
		font       = ImageFont.truetype(BytesIO(font_request.content), font_size)

		text_w, _ = calculate_rendered_text_wh(
			text  = longest_phrase,
			font  = font
			)

	# 📜🖼
	# Creates an image of the quote to be pasted on photo
	quote_img = create_quote_img(
		width         = pexels_videos_vid.size[0],
		quote_phrases = quote_phrases,
		font_quote    = font,
		quote_author  = quote_author,
		font_author   = ImageFont.truetype(BytesIO(font_request.content), int(0.75 * font_size)),
		line_gap      = int(0.4 * font_size)
		)

	# Overlays quote onto gradient mask
	quote_y = gradient_mask_img.size[1] - int(quote_img.size[1] * 1.25)
	gradient_mask_img.paste(quote_img, (0, quote_y), mask = quote_img)

	# Overlays image of gradient and quote onto video
	pexels_videos_vid = paste_image_onto_video(
		img        = gradient_mask_img,
		vid        = pexels_videos_vid,
		start_time = 0,
		last_for   = duration
		)

	# Saving generated video
	extension = filename[filename.find('.') + 1:]
	
	print(f"\n--- Compiling 'quote.{extension}' ---\n")
	pexels_videos_vid.write_videofile(f"quote.{extension}")

	# Deletes plain video
	os.remove(filename)