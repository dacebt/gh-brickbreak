"""
Collision detection and physics calculations.
"""
import math
from typing import Optional, Tuple, List
from .game_entities import Ball, Paddle, Brick
from .models import RenderContext
from .constants import COLLISION_EPSILON, IMAGE_WIDTH, IMAGE_HEIGHT, PADDING_LEFT, PADDING_RIGHT, PADDING_TOP


def check_wall_collisions(ball: Ball) -> Tuple[bool, bool]:
    """
    Check and handle ball collisions with walls.
    
    Args:
        ball: Ball object
        
    Returns:
        (hit_horizontal, hit_vertical): Booleans indicating wall hits
    """
    hit_horizontal = False
    hit_vertical = False
    
    # Left wall
    if ball.x - ball.radius <= PADDING_LEFT:
        ball.x = PADDING_LEFT + ball.radius
        ball.vx = abs(ball.vx)
        hit_horizontal = True
    
    # Right wall
    if ball.x + ball.radius >= IMAGE_WIDTH - PADDING_RIGHT:
        ball.x = IMAGE_WIDTH - PADDING_RIGHT - ball.radius
        ball.vx = -abs(ball.vx)
        hit_horizontal = True
    
    # Top wall
    if ball.y - ball.radius <= PADDING_TOP:
        ball.y = PADDING_TOP + ball.radius
        ball.vy = abs(ball.vy)
        hit_vertical = True
    
    # Bottom wall (shouldn't happen with paddle, but safety)
    if ball.y + ball.radius >= IMAGE_HEIGHT - 10:
        ball.vy = -abs(ball.vy)
        hit_vertical = True
    
    return hit_horizontal, hit_vertical


def check_paddle_collision(ball: Ball, paddle: Paddle) -> bool:
    """
    Check and handle ball collision with paddle.
    
    Args:
        ball: Ball object
        paddle: Paddle object
        
    Returns:
        True if collision occurred
    """
    # Only check if ball is moving downward
    if ball.vy <= 0:
        return False
    
    ball_left, ball_top, ball_right, ball_bottom = ball.get_bounds()
    paddle_left, paddle_top, paddle_right, paddle_bottom = paddle.get_bounds()
    
    # Check if ball overlaps paddle horizontally
    if ball_right < paddle_left or ball_left > paddle_right:
        return False
    
    # Check if ball has reached paddle vertically
    if ball_bottom >= paddle_top and ball_top < paddle_bottom:
        # Collision! Calculate new velocity
        ball.vx, ball.vy = paddle.calculate_bounce_angle(ball.x)
        
        # Position ball just above paddle to prevent re-collision
        ball.y = paddle_top - ball.radius
        
        return True
    
    return False


def check_brick_collisions(ball: Ball, bricks: List[Brick], render_context: RenderContext) -> Optional[Brick]:
    """
    Check and handle ball collision with bricks.
    
    Args:
        ball: Ball object
        bricks: List of active bricks
        render_context: Rendering context for pixel coordinates
        
    Returns:
        Brick that was hit, or None
    """
    ball_left, ball_top, ball_right, ball_bottom = ball.get_bounds()
    
    for brick in bricks:
        if brick.is_destroyed():
            continue
        
        brick_left, brick_top, brick_right, brick_bottom = brick.get_pixel_bounds(render_context)
        
        # AABB collision detection
        if not (ball_right < brick_left or 
                ball_left > brick_right or
                ball_bottom < brick_top or
                ball_top > brick_bottom):
            
            # Collision detected - determine collision side
            collision_side = _determine_collision_side(
                ball, brick, 
                brick_left, brick_top, brick_right, brick_bottom
            )
            
            # Bounce ball appropriately
            if collision_side in ['top', 'bottom']:
                ball.vy = -ball.vy
            else:  # left or right
                ball.vx = -ball.vx
            
            return brick
    
    return None


def _determine_collision_side(ball: Ball, brick: Brick, 
                              brick_left: float, brick_top: float,
                              brick_right: float, brick_bottom: float) -> str:
    """
    Determine which side of the brick the ball hit.
    
    Returns:
        'top', 'bottom', 'left', or 'right'
    """
    # Calculate distances from ball center to each side
    brick_center_x = (brick_left + brick_right) / 2
    brick_center_y = (brick_top + brick_bottom) / 2
    
    dx = ball.x - brick_center_x
    dy = ball.y - brick_center_y
    
    brick_half_width = (brick_right - brick_left) / 2
    brick_half_height = (brick_bottom - brick_top) / 2
    
    # Determine collision based on angle of approach
    if abs(dx / brick_half_width) > abs(dy / brick_half_height):
        # Hit from left or right
        return 'left' if dx < 0 else 'right'
    else:
        # Hit from top or bottom
        return 'top' if dy < 0 else 'bottom'
