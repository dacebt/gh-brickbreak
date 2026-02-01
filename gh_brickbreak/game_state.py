"""
Main game state management and orchestration.
"""
from typing import List, Optional
from .game_entities import Ball, Paddle, Brick, Explosion
from .physics import check_wall_collisions, check_paddle_collision, check_brick_collisions
from .models import ContributionData, RenderContext
from .constants import *


class GameState:
    """Manages all game entities and simulation state."""
    
    def __init__(self, contribution_data: ContributionData, render_context: RenderContext):
        """
        Initialize game state from contribution data.
        
        Args:
            contribution_data: GitHub contribution data
            render_context: Rendering configuration
        """
        self.contribution_data = contribution_data
        self.render_context = render_context
        
        # Initialize entities
        self.bricks: List[Brick] = self._initialize_bricks()
        self.ball: Ball = self._initialize_ball()
        self.paddle: Paddle = self._initialize_paddle()
        self.explosions: List[Explosion] = []
        
        # Game state
        self.frame_count = 0
        self.total_bricks = len(self.bricks)
        self.destroyed_bricks = 0
    
    def _initialize_bricks(self) -> List[Brick]:
        """Create brick objects from contribution data."""
        bricks = []
        
        for week_idx, week in enumerate(self.contribution_data.weeks):
            for day_idx, day in enumerate(week.days):
                if day.level == 0:
                    # No contribution = no brick
                    continue
                
                # Get brick properties from contribution level
                brick_config = CONTRIBUTION_LEVELS[day.level]
                
                brick = Brick(
                    col=week_idx,
                    row=day_idx,
                    strength=brick_config['strength'],
                    color=brick_config['color'],
                    contribution_count=day.count
                )
                bricks.append(brick)
        
        return bricks
    
    def _initialize_ball(self) -> Ball:
        """Create initial ball."""
        # Start ball at center-bottom, moving upward at slight angle
        start_x, start_y = self.render_context.grid_to_pixel(
            BALL_START_COL, 
            BALL_START_ROW
        )
        
        # Initial velocity: slightly angled upward-right
        import math
        angle = math.radians(-75)  # 15 degrees from vertical
        vx = BALL_SPEED * math.sin(angle)
        vy = BALL_SPEED * math.cos(angle)
        
        return Ball(start_x, start_y, vx, vy)
    
    def _initialize_paddle(self) -> Paddle:
        """Create initial paddle."""
        start_x, start_y = self.render_context.grid_to_pixel(
            NUM_WEEKS / 2,  # Center column
            PADDLE_ROW
        )
        
        return Paddle(start_x, start_y, PADDLE_WIDTH)
    
    def animate(self) -> dict:
        """
        Update all entities for one frame.
        
        Returns:
            Dictionary with frame events: {
                'wall_hit': bool,
                'paddle_hit': bool,
                'brick_hit': Brick or None,
                'brick_destroyed': bool
            }
        """
        events = {
            'wall_hit': False,
            'paddle_hit': False,
            'brick_hit': None,
            'brick_destroyed': False
        }
        
        # Update paddle position
        self.paddle.animate()
        
        # Update ball position
        self.ball.animate()
        
        # Check collisions
        h_wall, v_wall = check_wall_collisions(self.ball)
        events['wall_hit'] = h_wall or v_wall
        
        if check_paddle_collision(self.ball, self.paddle):
            events['paddle_hit'] = True
        
        hit_brick = check_brick_collisions(self.ball, self.bricks, self.render_context)
        if hit_brick:
            events['brick_hit'] = hit_brick
            was_destroyed = hit_brick.take_damage()
            
            if was_destroyed:
                events['brick_destroyed'] = True
                self.destroyed_bricks += 1
                
                # Create explosion effect
                brick_x, brick_y = self.render_context.grid_to_pixel(
                    hit_brick.col, 
                    hit_brick.row
                )
                self.explosions.append(Explosion(brick_x, brick_y))
        
        # Update explosions
        for explosion in self.explosions[:]:
            explosion.animate()
            if explosion.is_finished():
                self.explosions.remove(explosion)
        
        self.frame_count += 1
        
        return events
    
    def can_take_action(self) -> bool:
        """
        Check if game is ready for next strategy action.
        
        Paddle must be stationary before next action.
        """
        return not self.paddle.is_moving()
    
    def is_complete(self) -> bool:
        """Check if all bricks are destroyed."""
        return all(brick.is_destroyed() for brick in self.bricks)
    
    def get_active_bricks(self) -> List[Brick]:
        """Get list of bricks that are not destroyed."""
        return [brick for brick in self.bricks if not brick.is_destroyed()]
    
    def draw(self, draw_context, render_context: RenderContext):
        """Draw all game entities."""
        # Draw grid background
        self._draw_grid(draw_context, render_context)
        
        # Draw bricks
        for brick in self.bricks:
            brick.draw(draw_context, render_context)
        
        # Draw explosions
        for explosion in self.explosions:
            explosion.draw(draw_context, render_context)
        
        # Draw paddle
        self.paddle.draw(draw_context, render_context)
        
        # Draw ball
        self.ball.draw(draw_context, render_context)
    
    def _draw_grid(self, draw_context, render_context: RenderContext):
        """Draw background grid cells."""
        for week in range(NUM_WEEKS):
            for day in range(NUM_DAYS):
                rect = render_context.get_cell_rect(week, day)
                draw_context.rectangle(
                    rect,
                    fill=render_context.grid_color,
                    outline=render_context.grid_color
                )
