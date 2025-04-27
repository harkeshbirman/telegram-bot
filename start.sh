#!/bin/bash
set -e

# Check if poetry is installed
if ! command -v poetry &> /dev/null
then
    echo "Poetry is not installed. Please install it first."
    exit 1
fi

# Install dependencies (using lock file)
echo "Installing dependencies with Poetry..."
poetry install --no-root

# Activate virtual environment and run your main file
# Adjust 'your_script.py' below to your real entry point
echo "Running the project..."
poetry run python main.py
