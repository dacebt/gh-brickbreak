"""
AI strategies for autonomous paddle control.
"""
from abc import ABC, abstractmethod
from typing import Iterator, List
from .models import Action
from .game_state import GameState
from .game_entities import Brick


class BaseStrategy(ABC):
    """Base class for paddle control strategies."""
    
    @abstractmethod
    def generate_actions(self, game_state: GameState) -> Iterator[Action]:
        """
        Generate sequence of actions to clear all bricks.
        
        Args:
            game_state: Current game state
            
        Yields:
            Action objects telling paddle where to move
        """
        pass


class FollowBallStrategy(BaseStrategy):
    """
    Simple strategy: paddle always follows ball's x position.
    This ensures ball is always caught but creates predictable patterns.
    """
    
    def generate_actions(self, game_state: GameState) -> Iterator[Action]:
        """Follow ball position continuously."""
        while not game_state.is_complete():
            # Target paddle to ball's current x position
            # We don't really use this action because this strategy is reactive per frame in a real game,
            # but here we are simulating turns.
            # Actually, the animator loop consumes these actions.
            # If the strategy yields one action, the animator moves the paddle there.
            # Then it runs the game until paddle stops moving.
            
            # Wait, the FollowBallStrategy described in spec implies continuous movement.
            # But the animator loop structure is:
            # for action in action_generator:
            #   paddle.move_to(action.target_x)
            #   while not paddle.is_stopped(): animate()
            
            # This means FollowBallStrategy as implemented in spec:
            # yield Action(target_x=game_state.ball.x)
            # This yields ONE target based on ball position AT THAT MOMENT.
            # Then paddle moves there. Then it stops. Then next action.
            # This might be choppy if ball moves fast.
            # But let's follow the spec.
            
            yield Action(target_x=game_state.ball.x)


class ColumnStrategy(BaseStrategy):
    """
    Clear bricks column by column, left to right.
    Paddle positions to aim ball at specific columns.
    """
    
    def generate_actions(self, game_state: GameState) -> Iterator[Action]:
        """Clear columns systematically."""
        # Get all columns that have bricks
        active_columns = self._get_active_columns(game_state)
        
        for col in sorted(active_columns):
            # Target this column until all bricks in it are destroyed
            while self._column_has_bricks(game_state, col):
                # Convert grid column to pixel x
                target_x, _ = game_state.render_context.grid_to_pixel(col, 0)
                yield Action(target_x=target_x)
    
    def _get_active_columns(self, game_state: GameState) -> set:
        """Get set of columns that contain active bricks."""
        return {brick.col for brick in game_state.get_active_bricks()}
    
    def _column_has_bricks(self, game_state: GameState, col: int) -> bool:
        """Check if column still has bricks."""
        return any(brick.col == col for brick in game_state.get_active_bricks())


class RowStrategy(BaseStrategy):
    """
    Clear bricks row by row, bottom to top, with zigzag pattern.
    Alternates direction each row for visual variety.
    """
    
    def generate_actions(self, game_state: GameState) -> Iterator[Action]:
        """Clear rows with zigzag pattern."""
        from .constants import NUM_DAYS
        
        # Process rows from bottom to top (row 6 down to row 0)
        for row_idx in range(NUM_DAYS - 1, -1, -1):
            # Get all bricks in this row
            row_bricks = [
                brick for brick in game_state.get_active_bricks()
                if brick.row == row_idx
            ]
            
            if not row_bricks:
                continue
            
            # Sort bricks in zigzag pattern (alternate direction each row)
            # Odd rows go left-to-right, even rows go right-to-left
            reverse = (row_idx % 2 == 0)
            sorted_bricks = sorted(row_bricks, key=lambda b: b.col, reverse=reverse)
            
            # Target each brick position
            for brick in sorted_bricks:
                # Yield multiple actions for bricks with high strength
                for _ in range(brick.strength):
                    target_x, _ = game_state.render_context.grid_to_pixel(brick.col, 0)
                    yield Action(target_x=target_x)


# Strategy registry for CLI selection
STRATEGY_MAP = {
    'follow': FollowBallStrategy,
    'column': ColumnStrategy,
    'row': RowStrategy,
}
