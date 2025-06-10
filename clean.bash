#!/usr/bin/env bash
# Remove Python bytecode and cache directories
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} +
