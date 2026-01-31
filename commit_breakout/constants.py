"""
Core constants for Commit Breakout game.
All values tuned for 40 FPS default frame rate.
"""

# Grid and Layout
NUM_WEEKS = 52          # Contribution graph weeks (columns)
NUM_DAYS = 7            # Days per week (rows)
GRID_OFFSET_WEEKS = 1   # Skip first week if incomplete

# Visual/Rendering Constants
CELL_SIZE = 14          # Brick size in pixels
CELL_SPACING = 3        # Gap between bricks in pixels
PADDING_TOP = 50        # Top margin in pixels
PADDING_BOTTOM = 120    # Bottom margin (space for paddle)
PADDING_LEFT = 50       # Left margin
PADDING_RIGHT = 50      # Right margin

# Calculated dimensions
CELL_BLOCK_SIZE = CELL_SIZE + CELL_SPACING  # 15px total per cell
IMAGE_WIDTH = PADDING_LEFT + (NUM_WEEKS * CELL_BLOCK_SIZE) + PADDING_RIGHT
IMAGE_HEIGHT = PADDING_TOP + (NUM_DAYS * CELL_BLOCK_SIZE) + PADDING_BOTTOM

# Game Entity Sizes (in pixels)
PADDLE_WIDTH = 60       # Paddle width
PADDLE_HEIGHT = 10      # Paddle height
BALL_RADIUS = 4         # Ball radius

# Physics (in pixels per frame)
BALL_SPEED = 3.0        # Ball movement speed
PADDLE_SPEED = 5.0      # Paddle horizontal speed
BOUNCE_ANGLE_MAX = 60   # Max bounce angle from vertical (degrees)
PADDLE_FOLLOW_LEAD_FRAMES = 6  # Predictive lead for follow strategy
PADDLE_FOLLOW_MAX_OFFSET = PADDLE_WIDTH * 0.35  # Max follow offset from ball x

# Game Positioning (in grid units)
PADDLE_ROW = NUM_DAYS + 3  # Paddle row position (below grid)
BALL_START_ROW = PADDLE_ROW - 1  # Ball starting row
BALL_START_COL = NUM_WEEKS / 2   # Ball starting column (center)

# Animation
DEFAULT_FPS = 40        # Frames per second
FRAME_DURATION_MS = int(1000 / DEFAULT_FPS)  # 25ms per frame
MAX_FRAMES = 5000       # Safety limit for frame generation
END_PAUSE_FRAMES = 60   # Frames to show after completion (1.5 sec)

# Contribution Level Mapping
CONTRIBUTION_LEVELS = {
    0: {"strength": 0, "color": None},                    # No contribution
    1: {"strength": 1, "color": (14, 68, 41)},           # 1-3 commits (dark green)
    2: {"strength": 2, "color": (0, 109, 50)},           # 4-9 commits
    3: {"strength": 3, "color": (38, 166, 65)},          # 10-19 commits
    4: {"strength": 4, "color": (57, 211, 83)},          # 20+ commits (bright green)
}

# Color Scheme (Dark Mode)
COLOR_BACKGROUND = (13, 17, 23)      # Dark background
COLOR_GRID = (22, 27, 34)            # Grid cells background
COLOR_PADDLE = (201, 209, 217)       # Light gray paddle
COLOR_BALL = (255, 223, 0)           # Bright yellow ball
COLOR_EXPLOSION = (255, 100, 100)    # Red explosion particles

# Collision Detection
COLLISION_EPSILON = 0.1  # Margin for floating point collision checks

# GitHub API
GITHUB_API_URL = "https://api.github.com/graphql"
GITHUB_TIMEOUT = 30  # seconds
