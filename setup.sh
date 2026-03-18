#!/bin/bash

# Agent Workflow Builder - Quick Setup Script
# Usage: ./setup.sh

set -e

echo "======================================"
echo "  Agent Workflow Builder - Setup"
echo "======================================"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "[+] Python version: $PYTHON_VERSION"

# Check pip
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo "[!] pip not found. Please install pip first."
    exit 1
fi
echo "[+] Found pip: $PIP_CMD"

# Create virtual environment (optional)
read -p "Create a virtual environment? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "[+] Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Upgrade pip
echo "[+] Upgrading pip..."
$PIP_CMD install --upgrade pip

# Install project dependencies
echo "[+] Installing dependencies..."
$PIP_CMD install -r requirements.txt

# Install the package in development mode
echo "[+] Installing package in development mode..."
$PIP_CMD install -e .

# Verify installation
echo "[+] Verifying installation..."
if command -v awb &> /dev/null || python3 -c "import sys; sys.path.insert(0, 'src'); import agent_workflow_builder" &> /dev/null; then
    echo "[+] Installation successful!"
else
    echo "[!] Installation verification failed."
    exit 1
fi

echo ""
echo "======================================"
echo "  Setup Complete!"
echo "======================================"
echo ""
echo "Quick Start:"
echo "  awb init my_project"
echo "  awb generate examples/web_scraper_pipeline.yaml --output ./my_project"
echo "  awb validate examples/web_scraper_pipeline.yaml"
echo ""
echo "See README.md for more usage examples."
echo "======================================"
