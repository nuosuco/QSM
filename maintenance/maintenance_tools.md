# Quantum System Maintenance Tools

This document provides an overview of the maintenance tools developed for the Quantum System project. These tools help maintain system integrity, fix common issues, and provide diagnostics for the quantum gene marker system.

## Installation Checker

The `check_quantum_installation.py` script verifies that all necessary components for the quantum system are properly installed and configured.

```bash
python check_quantum_installation.py
```

This checks:
- Python version compatibility
- Virtual environment setup
- Required Python packages
- Core system files and modules
- VSCode task configuration
- Log directory existence

## Quantum Marker Fixers

### General Quantum Marker Fixer

The `fix_quantum_markers.py` script repairs syntax issues in Python files containing quantum gene markers:

```bash
# Windows
.\fix_quantum_markers.ps1

# Linux/Mac
bash ./fix_quantum_markers.sh
```

This script:
- Converts inline quantum markers to proper Python comments
- Fixes encoding issues with Chinese quantum markers
- Removes invalid syntax characters
- Processes files recursively

### Environment Files Fixer

The `fix_env_files.ps1` and `fix_env_files.sh` scripts specifically target Python environment files that might have quantum marker issues:

```bash
# Windows
.\fix_env_files.ps1

# Linux/Mac
bash ./fix_env_files.sh
```

These scripts:
- Detect the virtual environment location
- Identify and fix common problematic packages
- Fix markers in pip, setuptools, and other core packages
- Handle platform-specific cases (like pywin32 on Windows)

## Quantum Gene Statistics

The `quantum_gene_stats.py` script analyzes the project's quantum gene markers and generates comprehensive reports:

```bash
python quantum_gene_stats.py -o stats.json -r report.txt
```

This tool:
- Scans the entire project for quantum markers
- Identifies quantum gene IDs and their entanglement relationships
- Generates statistics on marker types and distribution
- Produces both human-readable reports and machine-readable JSON

## All-In-One Maintenance

The `quantum_maintenance.ps1` and `quantum_maintenance.sh` scripts run all maintenance tools in sequence:

```bash
# Windows
.\quantum_maintenance.ps1

# Linux/Mac
bash ./quantum_maintenance.sh
```

These scripts:
- Run all quantum marker fixers
- Generate statistical reports
- Provide detailed timing information

## VSCode Integration

All tools are integrated into VSCode tasks, accessible via:
1. Ctrl+Shift+P
2. "Tasks: Run Task"
3. Select the desired maintenance task

Tasks include:
- "Check Quantum Installation"
- "Run Quantum System Maintenance"
- "Fix Quantum Markers"
- "Generate Quantum Gene Statistics"

## Directory Structure

```
/
├── fix_quantum_markers.py     # Core Python fixer script
├── fix_quantum_markers.ps1    # Windows wrapper script
├── fix_quantum_markers.sh     # Linux/Mac wrapper script
├── fix_env_files.ps1          # Windows env fixer
├── fix_env_files.sh           # Linux/Mac env fixer
├── quantum_gene_stats.py      # Statistics generator
├── quantum_maintenance.ps1    # Windows all-in-one script
├── quantum_maintenance.sh     # Linux/Mac all-in-one script
├── check_quantum_installation.py  # Installation checker
└── .logs/                     # Log files directory
    ├── fix_quantum_markers.log
    ├── quantum_stats.log
    └── quantum_stats_report.txt
```

## Common Usage Scenarios

1. **First-time setup validation**:
   ```bash
   python check_quantum_installation.py
   ```

2. **After pulling new code with potential marker issues**:
   ```bash
   # Windows
   .\fix_quantum_markers.ps1
   # Linux/Mac
   bash ./fix_quantum_markers.sh
   ```

3. **When experiencing import errors in the environment**:
   ```bash
   # Windows
   .\fix_env_files.ps1
   # Linux/Mac
   bash ./fix_env_files.sh
   ```

4. **When needing project statistics**:
   ```bash
   python quantum_gene_stats.py -r report.txt
   ```

5. **Complete system maintenance**:
   ```bash
   # Windows
   .\quantum_maintenance.ps1
   # Linux/Mac
   bash ./quantum_maintenance.sh
   ```

## Troubleshooting

If you encounter issues with any of the maintenance tools:

1. Ensure your virtual environment is activated
2. Check the log files in the `.logs` directory
3. Verify you have proper permissions to access and modify files
4. Make sure all required Python packages are installed 

    ```
    # ```
量子基因编码: QE-MAI-3BB21A6741A9
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
```    ```
    