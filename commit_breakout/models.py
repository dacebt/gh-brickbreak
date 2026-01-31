"""
Data models and type definitions for Commit Breakout.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import date


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
    cell_size: int = 12
    cell_spacing: int = 3
    padding_top: int = 40
    padding_bottom: int = 80
    padding_left: int = 40
    padding_right: int = 40
    
    background_color: tuple = (13, 17, 23)
    grid_color: tuple = (22, 27, 34)
    paddle_color: tuple = (201, 209, 217)
    ball_color: tuple = (255, 223, 0)
    
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
