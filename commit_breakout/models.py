"""
Data models and type definitions for Commit Breakout.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import date
from .constants import (
    CELL_SIZE,
    CELL_SPACING,
    PADDING_TOP,
    PADDING_BOTTOM,
    PADDING_LEFT,
    PADDING_RIGHT,
    COLOR_BACKGROUND,
    COLOR_GRID,
    COLOR_PADDLE,
    COLOR_BALL,
)


@dataclass
class ContributionDay:
    """Represents a single day's contribution data."""
    date: date
    count: int          # Number of commits
    level: int          # GitHub contribution level (0-4)
    
    
@dataclass
class ContributionWeek:
    """Represents a week of contribution data."""
    days: List[ContributionDay]
    
    
@dataclass
class ContributionData:
    """Full contribution graph data for a user."""
    username: str
    total_contributions: int
    weeks: List[ContributionWeek]
    start_date: date
    end_date: date
    
    def get_day(self, week_idx: int, day_idx: int) -> Optional[ContributionDay]:
        """Safely get a specific day's data."""
        if 0 <= week_idx < len(self.weeks):
            if 0 <= day_idx < len(self.weeks[week_idx].days):
                return self.weeks[week_idx].days[day_idx]
        return None


@dataclass
class Action:
    """Represents a paddle strategy action."""
    target_x: float     # Target column position (grid units)
    
    
@dataclass
class RenderContext:
    """Rendering configuration and helper methods."""
    cell_size: int = CELL_SIZE
    cell_spacing: int = CELL_SPACING
    padding_top: int = PADDING_TOP
    padding_bottom: int = PADDING_BOTTOM
    padding_left: int = PADDING_LEFT
    padding_right: int = PADDING_RIGHT
    
    background_color: tuple = COLOR_BACKGROUND
    grid_color: tuple = COLOR_GRID
    paddle_color: tuple = COLOR_PADDLE
    ball_color: tuple = COLOR_BALL
    
    brick_colors: Dict[int, tuple] = field(default_factory=lambda: {
        1: (14, 68, 41),
        2: (0, 109, 50),
        3: (38, 166, 65),
        4: (57, 211, 83),
    })
    
    def grid_to_pixel(self, col: float, row: float) -> tuple:
        """Convert grid coordinates to pixel coordinates (center of cell)."""
        cell_block = self.cell_size + self.cell_spacing
        x = self.padding_left + (col * cell_block) + (self.cell_size / 2)
        y = self.padding_top + (row * cell_block) + (self.cell_size / 2)
        return (x, y)
    
    def get_cell_rect(self, col: int, row: int) -> tuple:
        """Get pixel rectangle for a grid cell (left, top, right, bottom)."""
        cell_block = self.cell_size + self.cell_spacing
        left = self.padding_left + (col * cell_block)
        top = self.padding_top + (row * cell_block)
        right = left + self.cell_size
        bottom = top + self.cell_size
        return (left, top, right, bottom)
