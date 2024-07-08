from base64 import b64encode, b64decode
from io     import BytesIO

from PIL import Image

def embed(img_fpath : str, output_in_txt : bool = False) -> bytes :
	
	# Opens image
	img : Image = Image.open(img_fpath)

	# Bytes from image will be saved in here
	bytes_array : BytesIO = BytesIO()
	img.save(bytes_array, format = 'PNG')

	# Embedding...
	bstring : bytes = b64encode(bytes_array.getvalue())

	# It is easier to copy the byte string from a .txt
	if output_in_txt :
		with open('embed.txt', 'w') as f :
			f.write(f'{bstring}')

	return bstring

def load_embedded(bstring : bytes) -> Image :
	
	# Decodes embedded image
	bytes_array : bytes = b64decode(bstring)

	# Reads image from bytes
	return Image.open(BytesIO(bytes_array))

def main() -> None :
	
	# Encoding
	bstring : bytes = embed(img_fpath = 'Path to Image')

	# Decoding
	img : Image = load_embedded(bstring = bstring)

if __name__ == '__main__' : main()
