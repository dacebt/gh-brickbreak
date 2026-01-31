"""
PIL-based rendering engine.
"""
from PIL import Image, ImageDraw, ImageFont
from typing import Generator
from .models import RenderContext
from .game_state import GameState
from .constants import IMAGE_WIDTH, IMAGE_HEIGHT


class Renderer:
    """Handles frame rendering using Pillow."""
    
    def __init__(self, render_context: RenderContext):
        """
        Initialize renderer.
        
        Args:
            render_context: Rendering configuration
        """
        self.context = render_context
        self.width = int(IMAGE_WIDTH)
        self.height = int(IMAGE_HEIGHT)
    
    def render_frame(self, game_state: GameState) -> Image.Image:
        """
        Render current game state to PIL Image.
        
        Args:
            game_state: Current game state
            
        Returns:
            PIL Image object
        """
        # Create base image with background color
        img = Image.new(
            'RGB',
            (self.width, self.height),
            self.context.background_color
        )
        
        # Create transparent overlay for drawing
        overlay = Image.new(
            'RGBA',
            (self.width, self.height),
            (0, 0, 0, 0)
        )
        
        draw = ImageDraw.Draw(overlay)
        
        # Draw all game entities
        game_state.draw(draw, self.context)
        
        # Composite overlay onto base image
        img = img.convert('RGBA')
        img = Image.alpha_composite(img, overlay)
        
        # Convert to RGB for GIF
        img = img.convert('RGB')
        
        return img
    
    def add_watermark(self, img: Image.Image, text: str) -> Image.Image:
        """
        Add watermark text to image.
        
        Args:
            img: PIL Image
            text: Watermark text
            
        Returns:
            Modified PIL Image
        """
        draw = ImageDraw.Draw(img)
        
        # Load font if possible, else use default
        try:
            font = ImageFont.load_default()
        except IOError:
            font = None
            
        # Position in bottom-right corner
        if hasattr(draw, 'textbbox'): # Pillow >= 9.2.0
            text_bbox = draw.textbbox((0, 0), text, font=font)
        else: # Older Pillow
             text_bbox = draw.textsize(text, font=font)
             text_bbox = (0, 0, text_bbox[0], text_bbox[1])

        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = self.width - text_width - 10
        y = self.height - text_height - 10
        
        # Draw text with slight shadow for visibility
        shadow_color = (0, 0, 0)
        text_color = (150, 150, 150)
        
        draw.text((x + 1, y + 1), text, fill=shadow_color, font=font)
        draw.text((x, y), text, fill=text_color, font=font)
        
        return img
