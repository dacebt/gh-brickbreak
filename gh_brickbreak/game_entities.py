"""
Game entities: Ball, Paddle, Brick, Explosion.
"""
import math
from typing import List, Tuple
from .constants import *
from .models import RenderContext


class Ball:
    """Represents the game ball with physics."""
    
    def __init__(self, x: float, y: float, vx: float, vy: float):
        """
        Initialize ball.
        
        Args:
            x, y: Position in pixel coordinates
            vx, vy: Velocity in pixels per frame
        """
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = BALL_RADIUS
    
    def animate(self):
        """Update ball position based on velocity."""
        self.x += self.vx
        self.y += self.vy
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Get ball bounding box (left, top, right, bottom)."""
        return (
            self.x - self.radius,
            self.y - self.radius,
            self.x + self.radius,
            self.y + self.radius
        )
    
    def draw(self, draw_context, render_context: RenderContext):
        """Draw ball on PIL image."""
        left, top, right, bottom = self.get_bounds()
        draw_context.ellipse(
            [left, top, right, bottom],
            fill=render_context.ball_color,
            outline=render_context.ball_color
        )


class Paddle:
    """Represents the player paddle (AI-controlled)."""
    
    def __init__(self, x: float, y: float, width: float):
        """
        Initialize paddle.
        
        Args:
            x: Center x position in pixels
            y: Top y position in pixels
            width: Paddle width in pixels
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = PADDLE_HEIGHT
        self.target_x = x
        self.speed = PADDLE_SPEED
    
    def move_to(self, target_x: float):
        """Set target position for paddle to move toward."""
        self.target_x = target_x
    
    def animate(self):
        """Update paddle position (smooth movement toward target)."""
        if abs(self.x - self.target_x) > self.speed:
            # Move toward target
            direction = 1 if self.target_x > self.x else -1
            self.x += self.speed * direction
        else:
            # Snap to target if close enough
            self.x = self.target_x
    
    def is_moving(self) -> bool:
        """Check if paddle is currently moving."""
        return abs(self.x - self.target_x) > COLLISION_EPSILON
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Get paddle bounding box (left, top, right, bottom)."""
        half_width = self.width / 2
        return (
            self.x - half_width,
            self.y,
            self.x + half_width,
            self.y + self.height
        )
    
    def calculate_bounce_angle(self, ball_x: float) -> Tuple[float, float]:
        """
        Calculate ball velocity after bouncing off paddle.
        
        Args:
            ball_x: Ball's x position at collision
            
        Returns:
            (vx, vy): New velocity components
        """
        # Calculate offset from paddle center (-1.0 to 1.0)
        offset = ball_x - self.x
        max_offset = self.width / 2
        normalized_offset = max(min(offset / max_offset, 1.0), -1.0)
        
        # Calculate bounce angle (max BOUNCE_ANGLE_MAX degrees from vertical)
        angle_degrees = normalized_offset * BOUNCE_ANGLE_MAX
        angle_radians = math.radians(angle_degrees)
        
        # Convert to velocity components
        vx = BALL_SPEED * math.sin(angle_radians)
        vy = -abs(BALL_SPEED * math.cos(angle_radians))  # Always upward
        
        return vx, vy
    
    def draw(self, draw_context, render_context: RenderContext):
        """Draw paddle on PIL image."""
        left, top, right, bottom = self.get_bounds()
        
        # Draw rounded rectangle for paddle
        draw_context.rounded_rectangle(
            [left, top, right, bottom],
            radius=3,
            fill=render_context.paddle_color,
            outline=render_context.paddle_color
        )


class Brick:
    """Represents a contribution brick."""
    
    def __init__(self, col: int, row: int, strength: int, color: tuple, contribution_count: int):
        """
        Initialize brick.
        
        Args:
            col, row: Grid position
            strength: Hit points before destruction (from contribution level)
            color: RGB color tuple
            contribution_count: Original commit count for this day
        """
        self.col = col
        self.row = row
        self.strength = strength
        self.max_strength = strength
        self.color = color
        self.contribution_count = contribution_count
        self.destroyed = False
    
    def take_damage(self, amount: int = 1) -> bool:
        """
        Reduce brick strength.
        
        Args:
            amount: Damage amount
            
        Returns:
            True if brick was destroyed by this hit
        """
        if self.destroyed:
            return False
        
        self.strength -= amount
        
        if self.strength <= 0:
            self.destroyed = True
            return True
        
        return False
    
    def is_destroyed(self) -> bool:
        """Check if brick is destroyed."""
        return self.destroyed
    
    def get_pixel_bounds(self, render_context: RenderContext) -> Tuple[float, float, float, float]:
        """Get brick bounding box in pixels (left, top, right, bottom)."""
        return render_context.get_cell_rect(self.col, self.row)
    
    def draw(self, draw_context, render_context: RenderContext):
        """Draw brick on PIL image."""
        if self.destroyed:
            return
        
        left, top, right, bottom = self.get_pixel_bounds(render_context)
        
        # Calculate color intensity based on remaining strength
        # (Optionally fade color as brick takes damage)
        color = self.color
        if self.strength < self.max_strength:
            # Darken slightly when damaged
            fade_factor = 0.7 + (0.3 * self.strength / self.max_strength)
            color = tuple(int(c * fade_factor) for c in color)
        
        draw_context.rectangle(
            [left, top, right, bottom],
            fill=color,
            outline=color
        )


class Explosion:
    """Visual effect when brick is destroyed."""
    
    def __init__(self, x: float, y: float, duration_frames: int = 10):
        """
        Initialize explosion.
        
        Args:
            x, y: Center position in pixels
            duration_frames: How many frames the explosion lasts
        """
        self.x = x
        self.y = y
        self.duration = duration_frames
        self.current_frame = 0
        self.max_radius = 15
        self.particles = self._generate_particles()
    
    def _generate_particles(self) -> List[Tuple[float, float, float]]:
        """Generate particle positions and angles."""
        import random
        particles = []
        num_particles = 12
        
        for i in range(num_particles):
            angle = (i / num_particles) * 2 * math.pi
            speed = random.uniform(0.5, 1.5)
            particles.append((angle, speed, random.uniform(0.7, 1.0)))  # angle, speed, brightness
        
        return particles
    
    def animate(self):
        """Update explosion animation."""
        self.current_frame += 1
    
    def is_finished(self) -> bool:
        """Check if explosion animation is complete."""
        return self.current_frame >= self.duration
    
    def draw(self, draw_context, render_context: RenderContext):
        """Draw explosion particles."""
        if self.is_finished():
            return
        
        # Calculate expansion and fade
        progress = self.current_frame / self.duration
        radius = self.max_radius * progress
        alpha = int(255 * (1 - progress)) # alpha not used directly in RGB tuple unless we use RGBA
        
        # Draw expanding particles
        for angle, speed, brightness in self.particles:
            particle_radius = radius * speed
            px = self.x + particle_radius * math.cos(angle)
            py = self.y + particle_radius * math.sin(angle)
            
            particle_size = 3
            # Simple fade by darkening
            color_intensity = brightness * (1 - progress)
            color = tuple(int(c * color_intensity) for c in COLOR_EXPLOSION)
            
            # Ensure color values are valid
            color = tuple(max(0, min(255, c)) for c in color)
            
            draw_context.ellipse(
                [px - particle_size, py - particle_size, 
                 px + particle_size, py + particle_size],
                fill=color
            )
        
        # Draw center flash
        if self.current_frame < self.duration / 2:
            flash_size = 5 * (1 - progress * 2)
            draw_context.ellipse(
                [self.x - flash_size, self.y - flash_size,
                 self.x + flash_size, self.y + flash_size],
                fill=(255, 255, 255)
            )
