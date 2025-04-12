# Fix Environment Files with Quantum Markers
# This script locates and fixes quantum markers in Python environment files

# Colors for output
$GREEN = [ConsoleColor]::Green
$YELLOW = [ConsoleColor]::Yellow
$RED = [ConsoleColor]::Red

# Functions for printing status, warnings, and errors
function Print-Status {
    param (
        [string]$Message
    )
    Write-Host "STATUS: $Message" -ForegroundColor $GREEN
}

function Print-Warning {
    param (
        [string]$Message
    )
    Write-Host "WARNING: $Message" -ForegroundColor $YELLOW
}

function Print-Error {
    param (
        [string]$Message
    )
    Write-Host "ERROR: $Message" -ForegroundColor $RED
}

# Check for virtual environment
function Check-Venv {
    $venvDirs = @(".venv", "venv")
    $venvFound = $false
    
    foreach ($dir in $venvDirs) {
        if (Test-Path $dir) {
            Print-Status "Found virtual environment: $dir"
            $venvFound = $true
            return $dir, $true
        }
    }
    
    if (-not $venvFound) {
        Print-Error "No virtual environment found (.venv or venv). Please create one first."
    }
    
    return $null, $venvFound
}

# Main function to fix environment files
function Fix-EnvFiles {
    Print-Status "Starting environment files fix process..."
    
    # Check for virtual environment
    $venvDir, $venvFound = Check-Venv
    if (-not $venvFound) {
        return $false
    }
    
    # Create .logs directory if it doesn't exist
    if (-not (Test-Path ".logs")) {
        New-Item -Path ".logs" -ItemType Directory | Out-Null
        Print-Status "Created .logs directory"
    }
    
    $logFile = ".logs/env_fix_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
    Start-Transcript -Path $logFile -Append | Out-Null
    
    try {
        # Detect Python version and site-packages directory
        $pythonVersion = & ".\$venvDir\Scripts\python.exe" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
        $sitePackagesDir = ".\$venvDir\Lib\site-packages"
        
        Print-Status "Python version: $pythonVersion"
        Print-Status "Site-packages directory: $sitePackagesDir"
        
        if (-not (Test-Path $sitePackagesDir)) {
            Print-Error "Site-packages directory not found: $sitePackagesDir"
            return $false
        }
        
        # Create Python script to fix quantum markers
        $fixerScript = @"
import sys
import os
import re

def fix_quantum_markers(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Fix quantum markers
        # 1. Fix indentation in quantum markers
        pattern = r'(\s*#\s*<<QUANTUM_MARKER>>.*?)(\n\s*\S)'
        content = re.sub(pattern, r'\1\n\2', content, flags=re.DOTALL)
        
        # 2. Fix missing closing markers
        if '<<QUANTUM_MARKER>>' in content and '<<END_QUANTUM_MARKER>>' not in content:
            content += '\n# <<END_QUANTUM_MARKER>>'
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"Error fixing {file_path}: {str(e)}")
        return False

def process_directory(directory):
    fixed_files = 0
    processed_files = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                processed_files += 1
                
                if fix_quantum_markers(file_path):
                    fixed_files += 1
    
    return processed_files, fixed_files

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python fix_quantum_markers.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        sys.exit(1)
    
    processed_files, fixed_files = process_directory(directory)
    print(f"Processed {processed_files} Python files")
    print(f"Fixed {fixed_files} files with quantum markers")
"@
        
        $fixerScriptPath = ".logs\fix_quantum_markers.py"
        Set-Content -Path $fixerScriptPath -Value $fixerScript
        
        # Run the fixer script on key directories
        Print-Status "Fixing pip..."
        & ".\$venvDir\Scripts\python.exe" $fixerScriptPath "$sitePackagesDir\pip"
        
        Print-Status "Fixing setuptools..."
        & ".\$venvDir\Scripts\python.exe" $fixerScriptPath "$sitePackagesDir\setuptools"
        
        Print-Status "Fixing win32 packages..."
        $win32Dir = "$sitePackagesDir\win32"
        if (Test-Path $win32Dir) {
            & ".\$venvDir\Scripts\python.exe" $fixerScriptPath $win32Dir
            
            # Check for pywin32_bootstrap.py
            $bootstrapPath = "$sitePackagesDir\pywin32_bootstrap.py"
            if (Test-Path $bootstrapPath) {
                Print-Status "Fixing pywin32_bootstrap.py..."
                & ".\$venvDir\Scripts\python.exe" $fixerScriptPath $bootstrapPath
            }
        }
        
        # Check for common packages
        $commonPackages = @("numpy", "pandas", "requests", "urllib3", "sphinx", "rich")
        foreach ($package in $commonPackages) {
            $packageDir = "$sitePackagesDir\$package"
            if (Test-Path $packageDir) {
                Print-Status "Fixing $package..."
                & ".\$venvDir\Scripts\python.exe" $fixerScriptPath $packageDir
            }
        }
        
        Print-Status "Environment fix process completed successfully!"
        return $true
    }
    catch {
        Print-Error "An error occurred during the fix process: $_"
        return $false
    }
    finally {
        Stop-Transcript | Out-Null
    }
}

# Execute the main function
Fix-EnvFiles 