import pytesseract
from PIL import Image
from django.conf import settings

class OCRHandler:
    def __init__(self):
        # Use getattr to provide a default value if the setting is not defined
        tesseract_path = getattr(settings, 'TESSERACT_CMD_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def process_image(self, image):
        img = Image.open(image)
        text = pytesseract.image_to_string(img)
        return self._parse_songs(text)

    def _parse_songs(self, text):
        songs = {}
        separators = [' - ', '-', '- ', ' -', ' ~ ', '~', ' ~', '~ ']
        for line in text.splitlines():
            for separator in separators:
                if separator in line:
                    song, artist = line.split(separator)
                    songs[song.strip()] = artist.strip()
                    break
        return songs