"""Main entry point for Geological Interpretation Agent."""

import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    from cli.main import cli
    cli()
