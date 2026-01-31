"""
Game loop and GIF generation.
"""
from typing import Generator, Optional
from PIL import Image
from .game_state import GameState
from .renderer import Renderer
from .strategies import BaseStrategy
from .models import ContributionData, RenderContext
from .constants import *


class Animator:
    """Orchestrates game simulation and GIF generation."""
    
    def __init__(
        self,
        contribution_data: ContributionData,
        strategy: BaseStrategy,
        fps: int = DEFAULT_FPS,
        watermark: Optional[str] = None
    ):
        """
        Initialize animator.
        
        Args:
            contribution_data: GitHub contribution data
            strategy: Paddle AI strategy
            fps: Frames per second
            watermark: Optional watermark text
        """
        self.contribution_data = contribution_data
        self.strategy = strategy
        self.fps = fps
        self.frame_duration = int(1000 / fps)
        self.watermark = watermark
        
        # Create render context
        self.render_context = RenderContext()
        
        # Initialize game state
        self.game_state = GameState(contribution_data, self.render_context)
        
        # Initialize renderer
        self.renderer = Renderer(self.render_context)
    
    def generate_frames(self) -> Generator[Image.Image, None, None]:
        """
        Generate frames for the game simulation.
        
        Yields:
            PIL Image objects for each frame
        """
        # Yield initial frame
        frame = self.renderer.render_frame(self.game_state)
        if self.watermark:
            frame = self.renderer.add_watermark(frame, self.watermark)
        yield frame
        
        # Execute strategy actions
        action_generator = self.strategy.generate_actions(self.game_state)
        
        for action in action_generator:
            # Set paddle target
            self.game_state.paddle.move_to(action.target_x)
            
            # Animate until paddle can take next action
            frames_since_action = 0
            while not self.game_state.can_take_action():
                events = self.game_state.animate()
                
                frame = self.renderer.render_frame(self.game_state)
                if self.watermark:
                    frame = self.renderer.add_watermark(frame, self.watermark)
                yield frame
                
                frames_since_action += 1
                
                # Safety: break if stuck
                if frames_since_action > 500:
                    break
            
            # Safety: check frame count
            if self.game_state.frame_count >= MAX_FRAMES:
                break
        
        # Continue animating until all bricks destroyed
        force_kill_countdown = 100
        while not self.game_state.is_complete() and force_kill_countdown > 0:
            self.game_state.animate()
            
            frame = self.renderer.render_frame(self.game_state)
            if self.watermark:
                frame = self.renderer.add_watermark(frame, self.watermark)
            yield frame
            
            force_kill_countdown -= 1
        
        # Yield pause frames at end
        for _ in range(END_PAUSE_FRAMES):
            frame = self.renderer.render_frame(self.game_state)
            if self.watermark:
                frame = self.renderer.add_watermark(frame, self.watermark)
            yield frame
    
    def generate_gif(self, output_path: str):
        """
        Generate and save animated GIF.
        
        Args:
            output_path: Path to save GIF file
        """
        print(f"Generating frames for {self.contribution_data.username}...")
        
        # Generate all frames
        frames = list(self.generate_frames())
        
        print(f"Generated {len(frames)} frames")
        
        # Convert frames to paletted mode for GIF
        paletted_frames = []
        for frame in frames:
            paletted = frame.convert('P', palette=Image.ADAPTIVE)
            paletted_frames.append(paletted)
        
        # Save as GIF
        print(f"Saving GIF to {output_path}...")
        paletted_frames[0].save(
            output_path,
            save_all=True,
            append_images=paletted_frames[1:],
            duration=self.frame_duration,
            loop=0,
            optimize=False
        )
        
        print(f"✓ GIF saved: {output_path}")
        print(f"  Total bricks: {self.game_state.total_bricks}")
        print(f"  Destroyed: {self.game_state.destroyed_bricks}")
        print(f"  Frames: {len(frames)}")
        print(f"  Duration: {len(frames) * self.frame_duration / 1000:.1f}s")
