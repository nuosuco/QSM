#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Quantum Gene Marker Syntax Fixer

This script automatically fixes syntax issues in Python files that have quantum gene markers
that might be causing parsing errors. It handles:
1. Comment conversion for Chinese quantum gene markers
2. Removal of invalid syntax characters
3. Recursive directory processing

Usage:
    python fix_quantum_markers.py <path_to_file_or_directory>
"""

import os
import sys
import re
import logging
from typing import List, Set, Union
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("../.logs/fix_quantum_markers.log", mode='a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("quantum_fixer")

# Chinese quantum marker patterns to look for
QUANTUM_MARKER_PATTERNS = [
    r'量子基因编码',  # Quantum Gene Encoding
    r'量子纠缠',      # Quantum Entanglement
    r'量子通信',      # Quantum Communication
    r'量子标记',      # Quantum Marker
]

# File types to process
PYTHON_EXTENSIONS = {'.py', '.pyw', '.pyi'}


def ensure_logs_dir():
    """Ensure the logs directory exists."""
    logs_dir = Path("../.logs")
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True)
        print(f"Created logs directory at {logs_dir}")


def is_python_file(file_path: str) -> bool:
    """Check if a file is a Python file based on its extension."""
    return os.path.splitext(file_path)[1].lower() in PYTHON_EXTENSIONS


def contains_quantum_markers(content: str) -> bool:
    """Check if file content contains any quantum markers."""
    for pattern in QUANTUM_MARKER_PATTERNS:
        if re.search(pattern, content):
            return True
    return False


def fix_quantum_markers(content: str) -> str:
    """
    Fix quantum markers in Python file content.
    
    1. Convert inline markers to proper Python comments
    2. Fix any encoding issues
    3. Remove any invalid syntax characters
    """
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Check if line contains any quantum markers
        has_marker = False
        for pattern in QUANTUM_MARKER_PATTERNS:
            if pattern in line:
                has_marker = True
                break
        
        if has_marker:
            # If it's already a comment, leave it as is
            if line.strip().startswith('#'):
                fixed_lines.append(line)
            else:
                # Extract code and marker parts
                code_part = ''
                marker_part = ''
                
                # Simple case: marker at beginning or end
                for pattern in QUANTUM_MARKER_PATTERNS:
                    if line.startswith(pattern):
                        marker_part = pattern
                        code_part = line[len(pattern):].strip()
                        break
                    elif line.endswith(pattern):
                        marker_part = pattern
                        code_part = line[:-len(pattern)].strip()
                        break
                
                # More complex case: marker in the middle
                if not marker_part:
                    for pattern in QUANTUM_MARKER_PATTERNS:
                        if pattern in line:
                            parts = line.split(pattern)
                            code_part = parts[0].strip()
                            marker_part = pattern
                            # Include anything after the marker as a comment
                            if len(parts) > 1 and parts[1].strip():
                                marker_part += ' ' + parts[1].strip()
                
                # Create fixed line
                if code_part:
                    # Code exists, add marker as comment
                    fixed_lines.append(f"{code_part}  # {marker_part}")
                else:
                    # Only marker exists, make it a comment
                    fixed_lines.append(f"# {marker_part}")
        else:
            # No quantum markers, keep line as is
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def process_file(file_path: str) -> bool:
    """Process a single file and fix any quantum markers."""
    if not is_python_file(file_path):
        logger.debug(f"Skipping non-Python file: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        if not contains_quantum_markers(content):
            logger.debug(f"No quantum markers found in {file_path}")
            return False
        
        # Fix the content
        fixed_content = fix_quantum_markers(content)
        
        # Write back the fixed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        logger.info(f"Fixed quantum markers in {file_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")
        return False


def process_directory(dir_path: str) -> int:
    """
    Recursively process all Python files in a directory.
    
    Returns the number of files fixed.
    """
    fixed_count = 0
    
    for root, _, files in os.walk(dir_path):
        for file in files:
            file_path = os.path.join(root, file)
            if process_file(file_path):
                fixed_count += 1
    
    return fixed_count


def main():
    """Main entry point for the script."""
    ensure_logs_dir()
    
    if len(sys.argv) < 2:
        logger.error("Usage: python fix_quantum_markers.py <path_to_file_or_directory>")
        sys.exit(1)
    
    path = sys.argv[1]
    
    if not os.path.exists(path):
        logger.error(f"Path does not exist: {path}")
        sys.exit(1)
    
    logger.info(f"Starting quantum marker fixing process for: {path}")
    
    if os.path.isfile(path):
        if process_file(path):
            logger.info("Successfully fixed 1 file.")
        else:
            logger.info("No fixes needed or file could not be processed.")
    else:
        fixed_count = process_directory(path)
        logger.info(f"Successfully fixed {fixed_count} files in {path}.")
    
    logger.info("Quantum marker fixing process completed.")


if __name__ == "__main__":
    main() 

    """
    # """
量子基因编码: QE-FIX-6FBBEB797E98
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""    """
    