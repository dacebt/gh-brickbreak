# Commit Breakout

Commit Breakout is a Python application that transforms a user's GitHub contribution graph into an animated Breakout-style brick-breaking game. Each day of contributions becomes a brick in a wall, with brick strength determined by commit count. An AI-controlled paddle follows various strategies to break all bricks. The output is an animated GIF generated using Python and Pillow (PIL).

## Features

- Fetches GitHub contribution data via API
- Maps contributions to game bricks (strength = commit intensity)
- Autonomous paddle AI with multiple strategies
- Physics-based ball and collision system
- Generates animated GIF visualization
- No external game engine - pure Python + PIL

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/commit-breakout.git
   cd commit-breakout
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Set up environment variables:
   Copy `.env.example` to `.env` and add your GitHub Personal Access Token (scope: `read:user`).
   ```bash
   cp .env.example .env
   # Edit .env with your token
   ```

## Usage

### Basic Usage

```bash
# Generate game for a user (requires GITHUB_TOKEN env var)
commit-breakout octocat
```

### Advanced Usage

```bash
# Specify strategy
commit-breakout octocat --strategy column

# Custom output filename
commit-breakout octocat --output my_game.gif

# Adjust frame rate
commit-breakout octocat --fps 30

# Add watermark
commit-breakout octocat --watermark "github.com/octocat"

# Save contribution data for reuse
commit-breakout octocat --raw-output octocat_data.json

# Load from saved data (no API call)
commit-breakout octocat --raw-input octocat_data.json --strategy row
```

## Strategies

- **follow**: Simple strategy where the paddle always follows the ball's horizontal position.
- **column**: Clears bricks column by column, from left to right.
- **row**: Clears bricks row by row, from bottom to top, alternating direction.
- **random**: Randomly targets columns with remaining bricks.

## License

MIT
