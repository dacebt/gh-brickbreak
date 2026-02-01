# Commit Breakout

Transform your GitHub contribution graph into an animated Breakout-style brick-breaking game. Each day of contributions becomes a brick, with brick strength determined by commit count. Watch an AI-controlled paddle break through your coding history!

## Features

- Fetches GitHub contribution data via the GitHub API
- Maps contributions to game bricks (strength based on commit intensity)
- Autonomous paddle AI with multiple strategies
- Physics-based ball and collision system
- Generates animated GIF visualization
- Built with pure Python and Pillow (no game engine required)

## Local Setup

### Prerequisites

- Python 3.10 or higher
- GitHub Personal Access Token with `read:user` scope

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dacebt/commit-breakout.git
   cd commit-breakout
   ```

2. Install the package:
   ```bash
   pip install -e .
   ```

3. Create a GitHub Personal Access Token:
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scope: `read:user`
   - Copy the generated token

4. Set up your environment:
   ```bash
   touch .env
   echo "GITHUB_TOKEN=your_token_here" >> .env
   ```

## Usage

### Basic Usage

```bash
# Generate game for a GitHub user
commit-breakout octocat
```

This creates `octocat_breakout.gif` in the current directory.

### Options

```bash
# Custom output filename
commit-breakout octocat --output my_game.gif
commit-breakout octocat -o my_game.gif

# Choose paddle AI strategy
commit-breakout octocat --strategy follow     # Paddle follows ball (default)
commit-breakout octocat --strategy column     # Clear column by column
commit-breakout octocat --strategy row        # Clear row by row
commit-breakout octocat --strategy random     # Random column targeting

# Adjust frame rate
commit-breakout octocat --fps 30              # Lower FPS = smaller file
commit-breakout octocat --fps 40              # Higher FPS = smoother animation

# Add watermark
commit-breakout octocat --watermark "github.com/octocat"

# Save contribution data to JSON (for reuse)
commit-breakout octocat --raw-output data.json

# Load from saved JSON (avoids API call)
commit-breakout octocat --raw-input data.json --output game.gif

# Pass token directly instead of using .env
commit-breakout octocat --token ghp_xxxxx
```

### Strategies

- **follow**: Paddle follows the ball's horizontal position
- **column**: Clears bricks column by column, left to right
- **row**: Clears bricks row by row, bottom to top, alternating direction
- **random**: Randomly targets columns with remaining bricks

## GitHub Action (Automated Daily Updates)

Set up a GitHub Action to automatically generate and update your game GIF daily.

### Setup

1. Create `.github/workflows/update-game.yml` in your repository:

```yaml
name: Update Breakout Game

on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight UTC
  workflow_dispatch:  # Allow manual trigger

permissions:
  contents: write

jobs:
  update-game:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install commit-breakout
        run: pip install git+https://github.com/dacebt/commit-breakout.git

      - name: Generate game
        run: |
          commit-breakout ${{ github.repository_owner }} \
            --token ${{ secrets.GITHUB_TOKEN }} \
            --output game.gif \
            --strategy random \
            --fps 40

      - name: Commit and push if changed
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add game.gif
          git diff --quiet && git diff --staged --quiet || \
            (git commit -m "Update breakout game [skip ci]" && git push)
```

2. Add the GIF to your profile README:

```markdown
![My GitHub Breakout Game](game.gif)
```

The action will run daily and commit the updated GIF to your repository.

### Customization

Modify the action to customize your game:

- Change `--strategy` to `follow`, `column`, `row`, or `random`
- Adjust `--fps` (default: 40)
- Change `--output` filename
- Add `--watermark "your text"` for custom watermark

## Special Thanks
Randomly came across [gh-space-shooter](https://github.com/czl9707/gh-space-shooter) and got inspired to see how it worked and create my own version.

## License

MIT
