#!/bin/bash

# Bash script to fix quantum markers
# This script activates the virtual environment and runs the Python fixer

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to write status messages
function print_status() {
    echo -e "${GREEN}$1${NC}"
}

# Function to write warning messages
function print_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

# Function to write error messages
function print_error() {
    echo -e "${RED}ERROR: $1${NC}"
}

# Check for virtual environment
print_status "Checking for virtual environment..."
VENV_PATH=""
if [ -d "../.venv" ]; then
    VENV_PATH="../.venv"
    print_status "Found virtual environment at .venv"
elif [ -d "../venv" ]; then
    VENV_PATH="../venv"
    print_status "Found virtual environment at venv"
else
    print_error "No virtual environment found. Please create one first."
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
if [ "$VENV_PATH" = "../.venv" ]; then
    source ../.venv/bin/activate
else
    source ../venv/bin/activate
fi

# Run the Python fixer script
print_status "Running quantum marker fixer script..."
python fix_quantum_markers.py

# Check specific known problematic files
print_status "Checking specific problematic files..."

# Fix pip/__init__.py
PIP_INIT_PATH="$VENV_PATH/lib/python*/site-packages/pip/__init__.py"
for pip_file in $PIP_INIT_PATH; do
    if [ -f "$pip_file" ]; then
        print_status "Fixing $pip_file..."
        python fix_quantum_markers.py "$pip_file"
    fi
done

# Fix pip/_vendor/rich/console.py
RICH_CONSOLE_PATH="$VENV_PATH/lib/python*/site-packages/pip/_vendor/rich/console.py"
for rich_file in $RICH_CONSOLE_PATH; do
    if [ -f "$rich_file" ]; then
        print_status "Fixing $rich_file..."
        python fix_quantum_markers.py "$rich_file"
    fi
done

# Deactivate virtual environment
print_status "Deactivating virtual environment..."
deactivate

print_status "All quantum marker fixes completed. Try importing the modules again."

# Make the script executable
chmod +x fix_quantum_markers.sh 

    #
    # #
量子基因编码: QE-FIX-5F614222890D
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
    
    