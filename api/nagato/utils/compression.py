import io
import zipfile

def inMemoryZip(files) :
	buffer = io.BytesIO()
	with zipfile.ZipFile(buffer, 'w') as zip_file:
		for filename, data in files.items() :
			zip_file.writestr(filename, io.BytesIO(data).getvalue())
	return buffer.getvalue()

def makeCbz(images, description=None) :
	files = {classifyImage(image, i+1): image for i, image in enumerate(images)}
	if description is not None :
		pass # TODO description
	return inMemoryZip(files)


binary_patterns = {
	b'\x89PNG\r\n\x1a\n': 'png',
	b'\xff\xd8\xff': 'jpg',
	b'GIF89a': 'gif',
	b'GIF87a': 'gif',
	b'RIFF': 'webp',
	b'II*\x00': 'tiff',
	b'MM\x00*': 'tiff'
}

def classifyImage(image: bytes, name) :
	for pattern, extension in binary_patterns.items() :
		if image.startswith(pattern) :
			return f"{name}.{extension}"
	return f"{name}.png"