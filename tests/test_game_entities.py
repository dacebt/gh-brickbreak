"""
Unit tests for game entities.
"""
import pytest
from commit_breakout.game_entities import Ball, Paddle, Brick
from commit_breakout.models import RenderContext


def test_ball_initialization():
    """Test ball is initialized correctly."""
    ball = Ball(100, 100, 2.0, -2.0)
    assert ball.x == 100
    assert ball.y == 100
    assert ball.vx == 2.0
    assert ball.vy == -2.0


def test_ball_movement():
    """Test ball moves according to velocity."""
    ball = Ball(100, 100, 2.0, -2.0)
    ball.animate()
    assert ball.x == 102
    assert ball.y == 98


def test_paddle_movement():
    """Test paddle moves toward target."""
    paddle = Paddle(100, 200, 60)
    
    # Initially target_x = x, so not moving
    assert not paddle.is_moving()
    
    paddle.move_to(150)
    
    # Now target_x != x, so moving
    assert paddle.is_moving()
    
    paddle.animate()
    assert paddle.x > 100  # Should move toward 150
    assert paddle.is_moving()


def test_brick_damage():
    """Test brick takes damage correctly."""
    brick = Brick(0, 0, strength=3, color=(0, 255, 0), contribution_count=10)
    
    assert brick.strength == 3
    assert not brick.is_destroyed()
    
    brick.take_damage()
    assert brick.strength == 2
    assert not brick.is_destroyed()
    
    brick.take_damage()
    brick.take_damage()
    assert brick.is_destroyed()


def test_paddle_bounce_angle():
    """Test paddle calculates bounce angles correctly."""
    paddle = Paddle(100, 200, 60)
    
    # Hit center of paddle
    vx, vy = paddle.calculate_bounce_angle(100)
    assert abs(vx) < 0.1  # Should be nearly straight up
    assert vy < 0  # Should be upward
    
    # Hit edge of paddle
    vx_edge, vy_edge = paddle.calculate_bounce_angle(130)  # Right edge
    assert vx_edge > 0  # Should angle right
    assert vy_edge < 0  # Should be upward
