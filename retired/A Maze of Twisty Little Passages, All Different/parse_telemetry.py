"""
Telemetry Path Parser and Visualizer
Author: Claude
Purpose: Parse drone telemetry data and visualize the path to reveal hidden message
Created: 2025-11-10
Updated: 2025-11-10
Expected Result: Visualize each sector's path as ASCII art to identify letters
Produced Result: Successfully visualized 30 sectors spelling "ITS ALWAYS SUNNY ON TELEVISION"
                  Generated sectors_visualization.png showing all paths
                  Flag: poctf{uwsp_175_4lw4y5_5unny_0n_73l3v1510n}
"""

import re
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

# Direction mappings: NORTH=0, EAST=1, SOUTH=2, WEST=3
DIRECTIONS = ['NORTH', 'EAST', 'SOUTH', 'WEST']
# Movement deltas for each direction: (dx, dy)
MOVES = {
    'NORTH': (0, 1),
    'EAST': (1, 0),
    'SOUTH': (0, -1),
    'WEST': (-1, 0)
}

def parse_sectors(filename):
    """Parse the README file and extract all sectors with their movements."""
    with open(filename, 'r') as f:
        content = f.read()

    sectors = []
    # Split by sector headers
    sector_blocks = re.findall(r'\[SECTOR \d+\](.*?)(?=\[SECTOR \d+\]|$)', content, re.DOTALL)

    for i, block in enumerate(sector_blocks, 1):
        moves = []
        lines = block.strip().split('\n')

        for line in lines:
            if 'Step forward' in line:
                moves.append('FORWARD')
            elif 'Turning left' in line:
                moves.append('LEFT')
            elif 'Turning right' in line:
                moves.append('RIGHT')
            elif 'Turning 180 degrees' in line:
                moves.append('U_TURN')

        sectors.append({
            'number': i,
            'moves': moves
        })

    return sectors

def simulate_path(moves):
    """Simulate the drone's path given a list of moves."""
    x, y = 0, 0
    facing = 0  # Start facing NORTH
    path = [(x, y)]

    for move in moves:
        if move == 'FORWARD':
            direction = DIRECTIONS[facing]
            dx, dy = MOVES[direction]
            x += dx
            y += dy
            path.append((x, y))
        elif move == 'LEFT':
            facing = (facing - 1) % 4
        elif move == 'RIGHT':
            facing = (facing + 1) % 4
        elif move == 'U_TURN':
            facing = (facing + 2) % 4

    return path

def visualize_path(path, sector_num):
    """Visualize a path as ASCII art."""
    if not path:
        return ""

    xs = [p[0] for p in path]
    ys = [p[1] for p in path]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    # Create grid
    width = max_x - min_x + 1
    height = max_y - min_y + 1
    grid = [[' ' for _ in range(width)] for _ in range(height)]

    # Mark path
    for x, y in path:
        grid_y = max_y - y  # Flip y-axis for display
        grid_x = x - min_x
        grid[grid_y][grid_x] = '#'

    # Convert to string
    result = f"Sector {sector_num}:\n"
    result += '\n'.join([''.join(row) for row in grid])
    return result

def plot_all_sectors(sectors):
    """Create a matplotlib visualization of all sectors."""
    # Calculate grid layout
    n_sectors = len(sectors)
    cols = 6
    rows = (n_sectors + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(20, rows * 3))
    if rows == 1:
        axes = [axes]
    axes = [ax for row in axes for ax in row] if rows > 1 else axes

    for i, sector in enumerate(sectors):
        path = simulate_path(sector['moves'])
        ax = axes[i]

        if path:
            xs = [p[0] for p in path]
            ys = [p[1] for p in path]

            # Plot path with line
            ax.plot(xs, ys, 'b-', linewidth=2)
            # Mark start point
            ax.plot(xs[0], ys[0], 'go', markersize=10, label='Start')
            # Mark end point
            ax.plot(xs[-1], ys[-1], 'ro', markersize=10, label='End')

            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
            ax.set_title(f'Sector {sector["number"]}')
            ax.legend()
        else:
            ax.text(0.5, 0.5, 'No path', ha='center', va='center', transform=ax.transAxes)

    # Hide unused subplots
    for i in range(n_sectors, len(axes)):
        axes[i].axis('off')

    plt.tight_layout()
    plt.savefig('sectors_visualization.png', dpi=150, bbox_inches='tight')
    print("Saved visualization to sectors_visualization.png")
    plt.close()

def main():
    filename = '/home/sean/ctf/HackTheBox/active/A Maze of Twisty Little Passages, All Different/README.md'

    print("Parsing telemetry data...")
    sectors = parse_sectors(filename)
    print(f"Found {len(sectors)} sectors\n")

    # Print ASCII visualizations
    message = []
    for sector in sectors:
        path = simulate_path(sector['moves'])
        ascii_art = visualize_path(path, sector['number'])
        print(ascii_art)
        print()

    # Create matplotlib visualization
    print("\nCreating detailed visualization...")
    plot_all_sectors(sectors)

    print("\nAnalyze the visualization to identify letters in each sector.")
    print("The hidden message is formed by reading the letters in order.")

if __name__ == '__main__':
    main()
