"""
Frame buffer handler for converting DOOM frames to ASCII art
"""
import numpy as np
from PIL import Image
from typing import List, Tuple

class FrameBuffer:
    # ASCII characters from darkest to lightest
    ASCII_CHARS = ' .:-=+*#%@'
    
    def __init__(self, width: int = 60, height: int = 40):
        self.width = width
        self.height = height
        
    def frame_to_ascii(self, frame: np.ndarray) -> str:
        """Convert a frame buffer to ASCII art"""
        # Resize the frame to our target dimensions
        image = Image.fromarray(frame)
        image = image.resize((self.width, self.height))
        
        # Convert to grayscale if not already
        if image.mode != 'L':
            image = image.convert('L')
            
        # Convert to numpy array
        pixels = np.array(image)
        
        # Normalize pixel values to ASCII character range
        normalized = (pixels / 255.0 * (len(self.ASCII_CHARS) - 1)).astype(int)
        
        # Convert to ASCII
        ascii_rows = []
        for row in normalized:
            ascii_row = ''.join(self.ASCII_CHARS[pixel] for pixel in row)
            ascii_rows.append(ascii_row)
            
        return '\n'.join(ascii_rows)
        
    def add_status_bar(self, ascii_frame: str, health: int, ammo: int, 
                      armor: int = 0, weapon: int = 2) -> str:
        """Add status bar to the ASCII frame"""
        # Create health bar
        health_bar = self._create_bar(health, 100, 10)
        ammo_text = f"Ammo: {ammo}"
        armor_text = f"Armor: {armor}"
        weapon_text = f"Weapon: {self._weapon_name(weapon)}"
        
        # Create status bar
        status_line = f"Health: [{health_bar}] {health}% | {ammo_text} | {armor_text} | {weapon_text}"
        
        # Add border and status
        width = max(len(line) for line in ascii_frame.split('\n'))
        border_top = '╔' + '═' * width + '╗\n'
        border_bottom = '╚' + '═' * width + '╝\n'
        
        # Center status line
        status_line = status_line.center(width)
        
        return f"{border_top}{ascii_frame}\n{border_bottom}{status_line}"
        
    def _create_bar(self, value: int, max_value: int, length: int) -> str:
        """Create a visual bar representation"""
        filled = int((value / max_value) * length)
        return '█' * filled + '░' * (length - filled)
        
    def _weapon_name(self, weapon_id: int) -> str:
        """Convert weapon ID to name"""
        weapons = {
            1: "Fist",
            2: "Pistol",
            3: "Shotgun",
            4: "Chaingun",
            5: "Rocket",
            6: "Plasma",
            7: "BFG9000"
        }
        return weapons.get(weapon_id, "Unknown")
