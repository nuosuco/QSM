#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Functions for output
print_status() {
    echo -e "${GREEN}[STATUS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check for virtual environment
check_venv() {
    if [ -d "../.venv" ]; then
        VENV_PATH="../.venv"
        print_status "Found virtual environment at .venv"
        return 0
    elif [ -d "../venv" ]; then
        VENV_PATH="../venv"
        print_status "Found virtual environment at venv"
        return 0
    else
        print_error "Virtual environment not found. Please make sure either .venv or venv directory exists."
        return 1
    fi
}

# Main function to fix files
fix_env_files() {
    print_status "Starting environment file fix process..."
    
    # Save original path and navigate to parent directory
    ORIGINAL_PATH=$(pwd)
    cd ..
    
    # Check and set virtual environment path
    check_venv || { cd "$ORIGINAL_PATH"; return 1; }
    
    # Create logs directory if it doesn't exist
    if [ ! -d ".logs" ]; then
        mkdir -p .logs
        print_status "Created .logs directory for log files"
    fi
    
    # Get Python version in the virtual environment
    if [[ "$OSTYPE" == "darwin"* || "$OSTYPE" == "linux-gnu"* ]]; then
        # macOS or Linux
        PYTHON_VERSION=$($VENV_PATH/bin/python -c "import sys; print(f'python{sys.version_info.major}.{sys.version_info.minor}')")
        SITE_PACKAGES="$VENV_PATH/lib/$PYTHON_VERSION/site-packages"
    else
        # Windows
        PYTHON_VERSION=$($VENV_PATH/Scripts/python -c "import sys; print(f'python{sys.version_info.major}{sys.version_info.minor}')")
        SITE_PACKAGES="$VENV_PATH/Lib/site-packages"
    fi
    
    print_status "Python version detected: $PYTHON_VERSION"
    print_status "Site packages directory: $SITE_PACKAGES"
    
    # Check if site-packages directory exists
    if [ ! -d "$SITE_PACKAGES" ]; then
        print_error "Site packages directory not found at $SITE_PACKAGES"
        cd "$ORIGINAL_PATH"
        return 1
    fi
    
    # Return to the maintenance directory
    cd "$ORIGINAL_PATH"
    
    # Run the Python fixer script on specific problematic directories
    print_status "Fixing pip package files..."
    if [ -d "$SITE_PACKAGES/pip" ]; then
        print_status "Running fixer on pip package..."
        python fix_quantum_markers.py "$SITE_PACKAGES/pip"
    fi
    
    print_status "Fixing setuptools package files..."
    if [ -d "$SITE_PACKAGES/setuptools" ]; then
        print_status "Running fixer on setuptools package..."
        python fix_quantum_markers.py "$SITE_PACKAGES/setuptools"
    fi
    
    # Check for pywin32 on Windows
    if [[ "$OSTYPE" != "darwin"* && "$OSTYPE" != "linux-gnu"* ]]; then
        if [ -d "$SITE_PACKAGES/win32" ]; then
            print_status "Fixing pywin32 files..."
            python fix_quantum_markers.py "$SITE_PACKAGES/win32"
            
            # Fix pywin32_bootstrap.py specifically
            if [ -f "$SITE_PACKAGES/pywin32_bootstrap.py" ]; then
                print_status "Fixing pywin32_bootstrap.py..."
                python fix_quantum_markers.py "$SITE_PACKAGES/pywin32_bootstrap.py"
            fi
        fi
    fi
    
    print_status "Checking for other common packages that might have issues..."
    common_packages=("numpy" "pandas" "requests" "urllib3" "sphinx" "rich")
    
    for package in "${common_packages[@]}"; do
        if [ -d "$SITE_PACKAGES/$package" ]; then
            print_status "Checking $package package..."
            python fix_quantum_markers.py "$SITE_PACKAGES/$package"
        fi
    done
    
    print_status "Environment files fix process completed."
}

# Run the main function
fix_env_files

# Make sure the script exits with the correct status
exit $? 

    #
    # #
量子基因编码: QE-FIX-70A39826F4F6
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
    
    