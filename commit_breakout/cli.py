"""
Command-line interface for Commit Breakout.
"""
import argparse
import sys
from pathlib import Path
from .github_client import GitHubClient
from .animator import Animator
from .strategies import STRATEGY_MAP


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Commit Breakout - Visualize GitHub contributions as a Breakout game',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  commit-breakout octocat
  commit-breakout octocat --strategy column --output octocat_game.gif
  commit-breakout octocat --fps 30 --watermark "github.com/octocat"
  commit-breakout octocat --raw-output data.json
  commit-breakout octocat --raw-input data.json --strategy row
        '''
    )
    
    parser.add_argument(
        'username',
        help='GitHub username to visualize'
    )
    
    parser.add_argument(
        '--strategy',
        choices=list(STRATEGY_MAP.keys()),
        default='random',
        help='Paddle AI strategy (default: random)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default=None,
        help='Output GIF filename (default: <username>_breakout.gif)'
    )
    
    parser.add_argument(
        '--fps',
        type=int,
        default=40,
        help='Frames per second (default: 40)'
    )
    
    parser.add_argument(
        '--watermark',
        default=None,
        help='Watermark text to add to GIF'
    )
    
    parser.add_argument(
        '--raw-output',
        default=None,
        help='Save raw contribution data to JSON file'
    )
    
    parser.add_argument(
        '--raw-input',
        default=None,
        help='Load contribution data from JSON file instead of API'
    )
    
    parser.add_argument(
        '--token',
        default=None,
        help='GitHub personal access token (or set GITHUB_TOKEN env var)'
    )
    
    args = parser.parse_args()
    
    # Determine output filename
    if args.output is None:
        args.output = f"{args.username}_breakout.gif"
    
    try:
        # Load or fetch contribution data
        if args.raw_input:
            print(f"Loading contribution data from {args.raw_input}...")
            contribution_data = GitHubClient.load_contribution_data(args.raw_input)
        else:
            print(f"Fetching contribution data for {args.username}...")
            client = GitHubClient(token=args.token)
            contribution_data = client.get_contributions(args.username)
            
            print(f"✓ Fetched {contribution_data.total_contributions} contributions")
            
            # Save raw data if requested
            if args.raw_output:
                client.save_contribution_data(contribution_data, args.raw_output)
                print(f"✓ Saved raw data to {args.raw_output}")
        
        # Select strategy
        strategy_class = STRATEGY_MAP[args.strategy]
        strategy = strategy_class()
        
        print(f"Strategy: {args.strategy}")
        
        # Create animator
        animator = Animator(
            contribution_data=contribution_data,
            strategy=strategy,
            fps=args.fps,
            watermark=args.watermark
        )
        
        # Generate GIF
        animator.generate_gif(args.output)
        
    except KeyboardInterrupt:
        print("\n✗ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        # import traceback
        # traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
