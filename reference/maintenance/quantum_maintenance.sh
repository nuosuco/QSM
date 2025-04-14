#!/bin/bash

# Bash script for quantum system maintenance
# This script runs all the quantum fix and analysis tools in sequence

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Functions for output
print_title() {
    echo -e "\n${CYAN}===== $1 =====${NC}"
}

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

# Activate virtual environment
activate_venv() {
    if [ "$VENV_PATH" = "../.venv" ]; then
        source ../.venv/bin/activate
    else
        source ../venv/bin/activate
    fi
    print_status "Virtual environment activated."
}

# Deactivate virtual environment
deactivate_venv() {
    deactivate
    print_status "Virtual environment deactivated."
}

# Run quantum marker fixes
run_quantum_marker_fixes() {
    print_title "Running Quantum Marker Fixes"
    
    # Run fix_quantum_markers.sh
    print_status "Running fix_quantum_markers.sh..."
    bash ./fix_quantum_markers.sh
    
    # Run fix_env_files.sh
    print_status "Running fix_env_files.sh..."
    bash ./fix_env_files.sh
    
    print_status "All quantum marker fixes completed."
}

# Run quantum gene analysis
run_quantum_gene_analysis() {
    print_title "Running Quantum Gene Analysis"
    
    # Activate virtual environment
    activate_venv
    
    # Run quantum gene statistics
    print_status "Analyzing quantum gene statistics..."
    python quantum_gene_stats.py -o "../.logs/quantum_stats.json" -r "../.logs/quantum_stats_report.txt"
    
    # Deactivate virtual environment
    deactivate_venv
    
    print_status "Quantum gene analysis completed."
    print_status "Report saved to ../.logs/quantum_stats_report.txt"
    print_status "Raw data saved to ../.logs/quantum_stats.json"
}

# Main function
main() {
    print_title "Quantum System Maintenance"
    
    START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
    START_SECONDS=$(date +%s)
    print_status "Starting maintenance at $START_TIME"
    
    # Save original path and navigate to parent directory
    ORIGINAL_PATH=$(pwd)
    cd ..
    
    # Check for virtual environment
    check_venv || { print_error "Cannot proceed without a virtual environment."; cd "$ORIGINAL_PATH"; exit 1; }
    
    # Create logs directory if it doesn't exist
    if [ ! -d ".logs" ]; then
        mkdir -p .logs
        print_status "Created .logs directory for log files"
    fi
    
    # Navigate back to maintenance directory
    cd "$ORIGINAL_PATH"
    
    # Run quantum marker fixes
    run_quantum_marker_fixes
    
    # Run quantum gene analysis
    run_quantum_gene_analysis
    
    END_TIME=$(date +"%Y-%m-%d %H:%M:%S")
    END_SECONDS=$(date +%s)
    DURATION=$((END_SECONDS - START_SECONDS))
    DURATION_MINUTES=$(echo "scale=2; $DURATION / 60" | bc)
    
    print_title "Maintenance Complete"
    print_status "Maintenance completed in $DURATION_MINUTES minutes."
    print_status "Started: $START_TIME"
    print_status "Finished: $END_TIME"
}

# Run the main function
main

# Make the script executable
chmod +x quantum_maintenance.sh 

    #
    # #
量子基因编码: QE-QUA-D9F466F9BEB7
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
    
    