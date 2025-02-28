#!/usr/bin/env python3

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the main function from the main module
from src.main import main

if __name__ == "__main__":
    # Run the main function
    exit_code = main()
    sys.exit(exit_code)
