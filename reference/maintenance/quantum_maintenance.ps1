
# # 量子基因编码: QE-QUA-E1B2B1514B32
# # 纠缠状态: 活跃
# # 纠缠对象: []
# # 纠缠强度: 0.98
# PowerShell script for quantum system maintenance
# This script runs all the quantum fix and analysis tools in sequence

# Colors for output
$GREEN = [System.ConsoleColor]::Green
$YELLOW = [System.ConsoleColor]::Yellow
$RED = [System.ConsoleColor]::Red
$CYAN = [System.ConsoleColor]::Cyan

# Functions for output
function Print-Title {
    param([string]$message)
    Write-Host "`n===== $message =====" -ForegroundColor $CYAN
}

function Print-Status {
    param([string]$message)
    Write-Host "[STATUS] " -ForegroundColor $GREEN -NoNewline
    Write-Host $message
}

function Print-Warning {
    param([string]$message)
    Write-Host "[WARNING] " -ForegroundColor $YELLOW -NoNewline
    Write-Host $message
}

function Print-Error {
    param([string]$message)
    Write-Host "[ERROR] " -ForegroundColor $RED -NoNewline
    Write-Host $message
}

function Check-Venv {
    if (Test-Path "..\\.venv") {
        $script:venvPath = "..\\.venv"
        Print-Status "Found virtual environment at .venv"
        return $true
    }
    elseif (Test-Path "..\\venv") {
        $script:venvPath = "..\\venv"
        Print-Status "Found virtual environment at venv"
        return $true
    }
    else {
        Print-Error "Virtual environment not found. Please make sure either .venv or venv directory exists."
        return $false
    }
}

function Activate-Venv {
    if ($venvPath -eq "..\\.venv") {
        & "..\\.venv\Scripts\Activate.ps1"
    }
    else {
        & "..\\venv\Scripts\Activate.ps1"
    }
    Print-Status "Virtual environment activated."
}

function Deactivate-Venv {
    deactivate
    Print-Status "Virtual environment deactivated."
}

function Run-QuantumMarkerFixes {
    Print-Title "Running Quantum Marker Fixes"
    
    # Run fix_quantum_markers.ps1
    Print-Status "Running fix_quantum_markers.ps1..."
    & .\fix_quantum_markers.ps1
    
    # Run fix_env_files.ps1
    Print-Status "Running fix_env_files.ps1..."
    & .\fix_env_files.ps1
    
    Print-Status "All quantum marker fixes completed."
}

function Run-QuantumGeneAnalysis {
    Print-Title "Running Quantum Gene Analysis"
    
    # Activate virtual environment
    Activate-Venv
    
    # Run quantum gene statistics
    Print-Status "Analyzing quantum gene statistics..."
    & python quantum_gene_stats.py -o "..\.logs\quantum_stats.json" -r "..\.logs\quantum_stats_report.txt"
    
    # Deactivate virtual environment
    Deactivate-Venv
    
    Print-Status "Quantum gene analysis completed."
    Print-Status "Report saved to ..\.logs\quantum_stats_report.txt"
    Print-Status "Raw data saved to ..\.logs\quantum_stats.json"
}

function Main {
    Print-Title "Quantum System Maintenance"
    
    $startTime = Get-Date
    Print-Status "Starting maintenance at $($startTime.ToString('yyyy-MM-dd HH:mm:ss'))"
    
    # Change to parent directory to find project files
    $originalPath = Get-Location
    Set-Location ..
    
    # Check for virtual environment
    if (-not (Check-Venv)) {
        Print-Error "Cannot proceed without a virtual environment."
        Set-Location $originalPath
        exit 1
    }
    
    # Create logs directory if it doesn't exist
    if (-not (Test-Path ".logs")) {
        New-Item -Path ".logs" -ItemType Directory -Force | Out-Null
        Print-Status "Created .logs directory for log files"
    }
    
    # Change back to maintenance directory
    Set-Location $originalPath
    
    # Run quantum marker fixes
    Run-QuantumMarkerFixes
    
    # Run quantum gene analysis
    Run-QuantumGeneAnalysis
    
    $endTime = Get-Date
    $duration = $endTime - $startTime
    Print-Title "Maintenance Complete"
    Print-Status "Maintenance completed in $($duration.TotalMinutes.ToString('0.00')) minutes."
    Print-Status "Started: $($startTime.ToString('yyyy-MM-dd HH:mm:ss'))"
    Print-Status "Finished: $($endTime.ToString('yyyy-MM-dd HH:mm:ss'))"
}

# Run the main function
Main 