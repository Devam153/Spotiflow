
import pytesseract
from PIL import Image
from django.conf import settings
import re
import os
from PIL import ImageOps

class OCRHandler:
    def __init__(self):
        # Set the tesseract path directly to match your working code
        tesseract_path = os.getenv("TESSERACT_CMD_PATH", "/usr/bin/tesseract")
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

    
    def process_image(self, image):
        """Process the uploaded image to extract songs"""
        img = Image.open(image)

        # Step 1: Convert to grayscale
        img = img.convert("L")
        
        # Step 2: Resize only if image is too large (preserve aspect ratio)
        MAX_PIXELS = 5_000_000  # ~5MP
        if img.width * img.height > MAX_PIXELS:
            scale_factor = (MAX_PIXELS / (img.width * img.height)) ** 0.5
            new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
            img = img.resize(new_size, Image.ANTIALIAS)

        # Step 3: Enhance contrast (makes OCR more accurate)
        img = ImageOps.autocontrast(img)

        # Step 4 (optional): For very tall images, split vertically into chunks
        if img.height > 2000:  # Tweak threshold as needed
            chunks = self._split_image_vertically(img)
            text = "\n".join(pytesseract.image_to_string(chunk) for chunk in chunks)
        else:
            text = pytesseract.image_to_string(img)

        return self._parse_songs(text)

    def _parse_songs(self, text):
        """Parse text to extract song-artist pairs"""
        songs = {}
        separators = [' - ', '-', '- ', ' -', ' ~ ', '~', ' ~', '~ ']
        
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
                
            # Skip entries that are likely not songs
            if self._is_not_song(line):
                continue
                
            for separator in separators:
                if separator in line:
                    try:
                        song, artist = line.split(separator, 1)
                        # Additional validation for song-artist pairs
                        if self._is_valid_song_artist_pair(song, artist):
                            songs[song.strip()] = artist.strip()
                    except ValueError:
                        # Handle case where splitting doesn't result in exactly 2 elements
                        continue
                    break
            else:
                # If no separator is found but it looks like a potential song title
                if self._could_be_song_title(line):
                    songs[line] = None
        
        return songs
    
    def _is_not_song(self, text):
        """Check if text is likely not a song"""
        # Check for patterns that suggest non-song entries
        patterns = [
            r'^[.]\s', # Lines starting with a dot and space
            r'@\s?\d+%', # Contains @ followed by percentage
            r'^\d+[:]?\d+\s', # Time format at the beginning
            r'^<\s*\w+', # Starts with < followed by text (like XML/HTML tags)
            r'^\w+\s*[®©]', # Contains copyright/registered symbols
            r'iCloud|Spotify', # Generic platform names without context
            r'^\w{1,3}$', # Very short text (3 chars or less) like "eee"
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        
        # Check if text is too short and doesn't have both letters and numbers
        if len(text) <= 3:
            return True
            
        return False
    
    def _is_valid_song_artist_pair(self, song, artist):
        """Validate if the song-artist pair looks legitimate"""
        song = song.strip()
        artist = artist.strip()
        
        # Check if either part is too short
        if len(song) < 2 or len(artist) < 2:
            return False
            
        # Check if song or artist contains weird patterns
        weird_patterns = [
            r'^\d+%', # Starts with percentage
            r'^\d+[:]?\d+$', # Just a time format
            r'^[<>@#]', # Starts with special characters
        ]
        
        for pattern in weird_patterns:
            if re.search(pattern, song) or re.search(pattern, artist):
                return False
                
        return True
    
    def _could_be_song_title(self, text):
        """Check if text could potentially be a song title without artist"""
        # Song titles typically have a reasonable length
        if len(text) < 4 or len(text) > 100:
            return False
            
        # Song titles typically include letters
        if not re.search(r'[a-zA-Z]', text):
            return False
            
        # Check for common patterns in song titles (words with capital letters)
        words = text.split()
        if len(words) >= 2 and any(word[0].isupper() for word in words if word):
            return True
            
        return False
    def _split_image_vertically(self, img, chunk_height=1000):
        """Split image into vertical chunks to avoid OCR timeouts"""
        width, height = img.size
        chunks = []
        for y in range(0, height, chunk_height):
            box = (0, y, width, min(y + chunk_height, height))
            chunks.append(img.crop(box))
        return chunks