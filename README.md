# gh-brickbreak

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
   git clone https://github.com/dacebt/gh-brickbreak.git
   cd gh-brickbreak
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
gh-brickbreak octocat
```

This creates `octocat_breakout.gif` in the current directory.

### Options

```bash
# Custom output filename
gh-brickbreak octocat --output my_game.gif
gh-brickbreak octocat -o my_game.gif

# Choose paddle AI strategy
gh-brickbreak octocat --strategy follow     # Paddle follows ball (default)
gh-brickbreak octocat --strategy column     # Clear column by column
gh-brickbreak octocat --strategy row        # Clear row by row

# Adjust frame rate
gh-brickbreak octocat --fps 30              # Lower FPS = smaller file
gh-brickbreak octocat --fps 40              # Higher FPS = smoother animation

# Add watermark
gh-brickbreak octocat --watermark "github.com/octocat"

# Save contribution data to JSON (for reuse)
gh-brickbreak octocat --raw-output data.json

# Load from saved JSON (avoids API call)
gh-brickbreak octocat --raw-input data.json --output game.gif

# Pass token directly instead of using .env
gh-brickbreak octocat --token ghp_xxxxx
```

### Strategies

- **follow**: Paddle follows the ball's horizontal position (default)
- **column**: Clears bricks column by column, left to right
- **row**: Clears bricks row by row, bottom to top, alternating direction

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

      - name: Install gh-brickbreak
        run: pip install git+https://github.com/dacebt/gh-brickbreak.git

      - name: Generate game
        run: |
          gh-brickbreak ${{ github.repository_owner }} \
            --token ${{ secrets.GITHUB_TOKEN }} \
            --output game.gif \
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

### Keeping your main branch history clean

If you run this action in a **profile or portfolio repo**, committing the GIF to `main` every time it changes will clutter your git history. Here are alternatives that avoid daily commits on `main`:

| Approach | How it works | Pros | Cons |
|----------|---------------|------|------|
| **Separate output branch** | Push the GIF to a branch like `breakout-output` and force-push so that branch has at most one “latest” commit. | Main stays clean; GIF still hosted on GitHub; stable raw URL. | One extra branch. |
| **GitHub Pages** | Deploy only the GIF (e.g. to `gh-pages`). | Main untouched; optional custom domain. | Requires Pages setup; URL is `https://user.github.io/repo/game.gif`. |
| **Gist** | Script updates a Gist with the GIF; README embeds the Gist’s raw URL. | No commits in your repo at all. | Gist history grows; need to create/manage Gist. |
| **External hosting** | Upload GIF to S3, R2, imgur, etc.; store only the URL in the repo (or in a small file). | No binary commits; full control over caching/URL. | Extra service and (maybe) cost. |
| **Commit only when changed** | Keep the workflow above; it already runs `git diff` and only commits when `game.gif` changes. | Simple; fewer commits than “every day” when contributions are unchanged. | When contributions change, you still get a commit on `main`. |

**Recommended for portfolios:** use the **separate output branch** so the GIF is still in the same repo and your profile README can reference it, without touching `main`. Example workflow:

1. Create `.github/workflows/update-game.yml`:

```yaml
name: Update Breakout Game (output branch only)

on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:

permissions:
  contents: write

jobs:
  update-game:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: breakout-output
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install gh-brickbreak
        run: pip install git+https://github.com/dacebt/gh-brickbreak.git

      - name: Generate game
        run: |
          gh-brickbreak ${{ github.repository_owner }} \
            --token ${{ secrets.GITHUB_TOKEN }} \
            --output game.gif \
            --fps 40

      - name: Push to output branch (no history on main)
        run: |
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git config user.name "github-actions[bot]"
          git add game.gif
          git diff --staged --quiet && exit 0
          git commit -m "Update breakout game [skip ci]"
          git push --force origin HEAD:breakout-output
```

2. Ensure the `breakout-output` branch exists (create it once from the repo’s default branch with an empty commit or a placeholder, or the first run will create it when pushing).

3. In your profile README, point the image at the file on that branch (replace `USER` and `REPO`):

```markdown
![My GitHub Breakout Game](https://raw.githubusercontent.com/USER/REPO/breakout-output/game.gif)
```

Your `main` (or default) branch never gets these updates; only `breakout-output` does, and you can force-push so that branch stays at a single tip.

### Customization

Modify the action to customize your game:

- Change `--strategy` to `follow`, `column`, or `row`
- Adjust `--fps` (default: 40)
- Change `--output` filename
- Add `--watermark "your text"` for custom watermark

## Special Thanks
Randomly came across [gh-space-shooter](https://github.com/czl9707/gh-space-shooter) and got inspired to see how it worked and create my own version.

## License

MIT
