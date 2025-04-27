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
echo "Running the project..."
poetry run python main.py
