
# # 量子基因编码: QE-FIX-440940228176
# # 纠缠状态: 活跃
# # 纠缠对象: []
# # 纠缠强度: 0.98
# PowerShell script to fix environment files with quantum markers

# Colors for output
$GREEN = [System.ConsoleColor]::Green
$YELLOW = [System.ConsoleColor]::Yellow
$RED = [System.ConsoleColor]::Red

# Functions for output
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

# Check for virtual environment
function Check-Venv {
    if (Test-Path "../.venv") {
        $script:venvPath = "../.venv"
        Print-Status "Found virtual environment at ../.venv"
        return $true
    }
    elseif (Test-Path "../venv") {
        $script:venvPath = "../venv"
        Print-Status "Found virtual environment at ../venv"
        return $true
    }
    elseif (Test-Path ".venv") {
        $script:venvPath = ".venv"
        Print-Status "Found virtual environment at .venv"
        return $true
    }
    elseif (Test-Path "venv") {
        $script:venvPath = "venv"
        Print-Status "Found virtual environment at venv"
        return $true
    }
    else {
        Print-Error "Virtual environment not found. Please make sure either .venv or venv directory exists."
        return $false
    }
}

# Main function to fix files
function Fix-EnvFiles {
    Print-Status "Starting environment file fix process..."
    
    # Save original path and navigate to parent directory
    $originalPath = Get-Location
    
    # Check and set virtual environment path
    if (-not (Check-Venv)) {
        return
    }
    
    # Create logs directory if it doesn't exist
    if (-not (Test-Path "../.logs") -and -not (Test-Path ".logs")) {
        New-Item -Path "../.logs" -ItemType Directory -Force | Out-Null
        Print-Status "Created ../.logs directory for log files"
    }
    
    # Get Python version in the virtual environment
    $pythonExe = Join-Path $venvPath "Scripts\python.exe"
    $pythonCommand = "$pythonExe -c `"import sys; print(f'python{sys.version_info.major}{sys.version_info.minor}')`""
    $pythonVersion = Invoke-Expression $pythonCommand
    $sitePackages = Join-Path $venvPath "Lib\site-packages"
    
    Print-Status "Python version detected: $pythonVersion"
    Print-Status "Site packages directory: $sitePackages"
    
    # Check if site-packages directory exists
    if (-not (Test-Path $sitePackages)) {
        Print-Error "Site packages directory not found at $sitePackages"
        return
    }
    
    # Run the Python fixer script on specific problematic directories
    Print-Status "Fixing pip package files..."
    $pipDir = Join-Path $sitePackages "pip"
    if (Test-Path $pipDir) {
        Print-Status "Running fixer on pip package..."
        & python fix_quantum_markers.py $pipDir
    }
    
    Print-Status "Fixing setuptools package files..."
    $setupDir = Join-Path $sitePackages "setuptools"
    if (Test-Path $setupDir) {
        Print-Status "Running fixer on setuptools package..."
        & python fix_quantum_markers.py $setupDir
    }
    
    # Fix pywin32 files on Windows
    $win32Dir = Join-Path $sitePackages "win32"
    if (Test-Path $win32Dir) {
        Print-Status "Fixing pywin32 files..."
        & python fix_quantum_markers.py $win32Dir
        
        # Fix pywin32_bootstrap.py specifically
        $bootstrapFile = Join-Path $sitePackages "pywin32_bootstrap.py"
        if (Test-Path $bootstrapFile) {
            Print-Status "Fixing pywin32_bootstrap.py..."
            & python fix_quantum_markers.py $bootstrapFile
        }
    }
    
    Print-Status "Checking for other common packages that might have issues..."
    $commonPackages = @("numpy", "pandas", "requests", "urllib3", "sphinx", "rich")
    
    foreach ($package in $commonPackages) {
        $packageDir = Join-Path $sitePackages $package
        if (Test-Path $packageDir) {
            Print-Status "Checking $package package..."
            & python fix_quantum_markers.py $packageDir
        }
    }
    
    Print-Status "Environment files fix process completed."
}

# Run the main function
Fix-EnvFiles 