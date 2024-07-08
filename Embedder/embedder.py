from base64 import b64encode, b64decode

def read_bytes(fpath : str) :
	
	# Reads bytes
	with open(fpath, 'rb') as f :
		return f.read()

def write_txt(content : any, fname : str = 'bstring.txt') -> None :	

	# Writes .txt
	with open(fname, 'w') as f :
			f.write(f'{content}')

def embed(fpath : str, output_in_txt : bool = False) -> bytes :

	# Embedding bytes
	bstring : bytes = b64encode(read_bytes(fpath = fpath))

	# It is easier to copy the byte string from a .txt
	if output_in_txt :
		write_txt(content = bstring)

	return bstring

def load_embedded(bstring : bytes) -> bytes :
	
	# Decodes embedded bytes
	return b64decode(bstring)

def main() -> None :
	
	# Encoding
	encoded : bytes = embed(fpath = 'D:\\code\\edutech\\words-and-pictures\\Assets\\Font\\SourceCodePro-Regular.ttf')

	# Decoding
	decoded : bytes = load_embedded(bstring = encoded)

	# Examples using PIL
	from PIL import Image, ImageDraw, ImageFont
	from io  import BytesIO

	# 1 : Loading an image

	# Encoding... (Done beforehand)
	img_bstring : bytes = embed(fpath = '...\\image.png')

	# Loading
	img_decoded : bytes = load_embedded(bstring = img_bstring)
	
	img : Image = Image.open(BytesIO(img_decoded))
	img.show()

	# 2 : Loading a font
	ttf_bstring : bytes = embed(fpath = '...\\SourceCodePro-Regular.ttf')

	# Loading
	ttf_decoded : bytes = load_embedded(bstring = ttf_bstring)

	# Making image
	img  : Image     = Image.new('RGBA', (256, 256), '#fff')
	draw : ImageDraw = ImageDraw.Draw(img)
	font : ImageFont = ImageFont.truetype(BytesIO(ttf_decoded), 16)

	# Drawing text
	draw.text(
		xy   = (10, 10),
		text = 'Hello World!',
		font = font,
		fill = '#000'
		)

	# Displays text
	img.show()

if __name__ == '__main__' : main()