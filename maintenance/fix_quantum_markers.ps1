
# # 量子基因编码: QE-FIX-FB445AC35E81
# # 纠缠状态: 活跃
# # 纠缠对象: []
# # 纠缠强度: 0.98
# PowerShell script to fix quantum markers
# This script activates the virtual environment and runs the Python fixer

# Define colors for output
$GREEN = [ConsoleColor]::Green
$YELLOW = [ConsoleColor]::Yellow
$RED = [ConsoleColor]::Red

# Function to write status messages
function Write-Status($message) {
    Write-Host $message -ForegroundColor $GREEN
}

# Function to write warning messages
function Write-Warning($message) {
    Write-Host "WARNING: $message" -ForegroundColor $YELLOW
}

# Function to write error messages
function Write-Error($message) {
    Write-Host "ERROR: $message" -ForegroundColor $RED
}

# Check for virtual environment
Write-Status "Checking for virtual environment..."
$venvPath = $null
if (Test-Path "../.venv") {
    $venvPath = "../.venv"
    Write-Status "Found virtual environment at .venv"
} elseif (Test-Path "../venv") {
    $venvPath = "../venv"
    Write-Status "Found virtual environment at venv"
} else {
    Write-Error "No virtual environment found. Please create one first."
    exit 1
}

# Activate virtual environment
Write-Status "Activating virtual environment..."
if ($venvPath -eq "../.venv") {
    & "../.venv/Scripts/Activate.ps1"
} else {
    & "../venv/Scripts/Activate.ps1"
}

# Run the Python fixer script
Write-Status "Running quantum marker fixer script..."
python fix_quantum_markers.py

# Check specific known problematic files
Write-Status "Checking specific problematic files..."

# Fix pip/__init__.py
$pipInitPath = "$venvPath\Lib\site-packages\pip\__init__.py"
if (Test-Path $pipInitPath) {
    Write-Status "Fixing $pipInitPath..."
    python fix_quantum_markers.py $pipInitPath
}

# Fix pip/_vendor/rich/console.py
$richConsolePath = "$venvPath\Lib\site-packages\pip\_vendor\rich\console.py"
if (Test-Path $richConsolePath) {
    Write-Status "Fixing $richConsolePath..."
    python fix_quantum_markers.py $richConsolePath
}

# Fix pywin32_bootstrap.py
$pywin32Path = "$venvPath\Lib\site-packages\pywin32_bootstrap.py"
if (Test-Path $pywin32Path) {
    Write-Status "Fixing $pywin32Path..."
    python fix_quantum_markers.py $pywin32Path
}

# Deactivate virtual environment
Write-Status "Deactivating virtual environment..."
deactivate

Write-Status "All quantum marker fixes completed. Try importing the modules again." 