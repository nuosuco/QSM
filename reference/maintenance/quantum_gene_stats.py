#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Quantum Gene Statistics Analyzer

This script analyzes the project for quantum gene markers and generates statistics
about their distribution, types, and entanglement relationships.

Usage:
    python quantum_gene_stats.py [directory]
"""

import os
import sys
import re
import json
import logging
from typing import Dict, List, Tuple, Set
from collections import defaultdict, Counter
from pathlib import Path
import argparse
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(".logs/quantum_stats.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("quantum_stats")

# Quantum marker patterns to search for
QUANTUM_PATTERNS = {
    "量子基因编码": "Quantum Gene Encoding",
    "量子基因标记": "Quantum Gene Marker",
    "量子基因模板": "Quantum Gene Template",
    "量子纠缠": "Quantum Entanglement",
    "量子通信": "Quantum Communication",
    "量子标记": "Quantum Marker",
    "QE-": "Quantum Entity Identifier",
    "QV-": "Quantum Value Identifier",
    "QP-": "Quantum Process Identifier"
}

# File extensions to analyze
FILE_EXTENSIONS = [
    '.py', '.pyw', '.pyi',  # Python
    '.js', '.jsx', '.ts', '.tsx',  # JavaScript/TypeScript
    '.html', '.htm', '.css',  # Web
    '.c', '.cpp', '.h', '.hpp',  # C/C++
    '.java', '.go', '.rs',  # Other languages
    '.json', '.yaml', '.yml',  # Data formats
    '.md', '.txt'  # Documentation
]

def ensure_logs_dir():
    """Ensure logs directory exists"""
    logs_dir = Path(".logs")
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True)
        logger.info(f"Created logs directory at {logs_dir}")


class QuantumGeneAnalyzer:
    def __init__(self, root_dir: str = '.'):
        self.root_dir = os.path.abspath(root_dir)
        self.total_files = 0
        self.files_with_markers = 0
        self.marker_counts = Counter()
        self.markers_by_file_type = defaultdict(Counter)
        self.entanglement_map = defaultdict(set)
        self.gene_ids = set()
        
        # Statistics storage
        self.stats = {
            "total_files": 0,
            "files_with_markers": 0,
            "total_markers": 0,
            "marker_types": {},
            "file_types": {},
            "entanglement_count": 0,
            "unique_gene_ids": 0,
            "top_files": []
        }
    
    def should_process_file(self, file_path: str) -> bool:
        """Determine if a file should be processed based on extension and ignore patterns"""
        # Skip directories that are likely not relevant
        ignore_dirs = ['.git', '.venv', 'venv', '__pycache__', 'node_modules', '.idea']
        for dir_name in ignore_dirs:
            if f'/{dir_name}/' in file_path or file_path.endswith(f'/{dir_name}'):
                return False
        
        # Check file extension
        _, ext = os.path.splitext(file_path)
        return ext.lower() in FILE_EXTENSIONS
    
    def extract_gene_ids(self, content: str) -> Set[str]:
        """Extract quantum gene IDs from content"""
        ids = set()
        
        # Pattern for QE-XXXXX-XXXXX format
        id_pattern = r'(QE-[A-Z0-9]+-[A-Z0-9]+)'
        matches = re.findall(id_pattern, content)
        ids.update(matches)
        
        return ids
    
    def find_entanglements(self, content: str, file_path: str, gene_ids: Set[str]):
        """Find entanglement relationships between quantum genes"""
        for gene_id in gene_ids:
            self.entanglement_map[gene_id].add(file_path)
    
    def analyze_file(self, file_path: str):
        """Analyze a single file for quantum markers"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                
            self.total_files += 1
            file_type = os.path.splitext(file_path)[1].lower()
            
            file_markers = Counter()
            has_markers = False
            
            # Count markers
            for pattern, description in QUANTUM_PATTERNS.items():
                count = len(re.findall(pattern, content))
                if count > 0:
                    file_markers[description] += count
                    self.marker_counts[description] += count
                    self.markers_by_file_type[file_type][description] += count
                    has_markers = True
            
            if has_markers:
                self.files_with_markers += 1
                
                # Extract gene IDs
                gene_ids = self.extract_gene_ids(content)
                self.gene_ids.update(gene_ids)
                
                # Map entanglements
                self.find_entanglements(content, file_path, gene_ids)
                
                # Store file info for reporting
                rel_path = os.path.relpath(file_path, self.root_dir)
                return {
                    "path": rel_path,
                    "markers": dict(file_markers),
                    "total": sum(file_markers.values()),
                    "gene_ids": list(gene_ids)
                }
                
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
        
        return None
    
    def analyze_directory(self):
        """Analyze the entire directory structure"""
        logger.info(f"Starting analysis of {self.root_dir}")
        
        files_info = []
        
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                file_path = os.path.join(root, file)
                
                if self.should_process_file(file_path):
                    file_info = self.analyze_file(file_path)
                    if file_info and file_info["total"] > 0:
                        files_info.append(file_info)
        
        # Sort files by marker count
        files_info.sort(key=lambda x: x["total"], reverse=True)
        
        # Calculate entanglement stats
        entangled_genes = [gene_id for gene_id, files in self.entanglement_map.items() 
                          if len(files) > 1]
        
        # Compile stats
        self.stats["total_files"] = self.total_files
        self.stats["files_with_markers"] = self.files_with_markers
        self.stats["total_markers"] = sum(self.marker_counts.values())
        self.stats["marker_types"] = dict(self.marker_counts)
        self.stats["file_types"] = {ext: dict(counts) for ext, counts in self.markers_by_file_type.items()}
        self.stats["entanglement_count"] = len(entangled_genes)
        self.stats["unique_gene_ids"] = len(self.gene_ids)
        self.stats["top_files"] = files_info[:20]  # Top 20 files with most markers
        
        return self.stats
    
    def generate_report(self):
        """Generate a human-readable report"""
        stats = self.stats
        
        report = []
        report.append("=== Quantum Gene Statistics Report ===")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Project directory: {self.root_dir}")
        report.append("")
        
        report.append("--- Summary ---")
        report.append(f"Total files analyzed: {stats['total_files']}")
        report.append(f"Files with quantum markers: {stats['files_with_markers']} ({stats['files_with_markers']/max(1, stats['total_files'])*100:.1f}%)")
        report.append(f"Total markers found: {stats['total_markers']}")
        report.append(f"Unique quantum gene IDs: {stats['unique_gene_ids']}")
        report.append(f"Entangled gene relationships: {stats['entanglement_count']}")
        report.append("")
        
        report.append("--- Marker Types ---")
        for marker_type, count in sorted(stats['marker_types'].items(), key=lambda x: x[1], reverse=True):
            report.append(f"{marker_type}: {count} ({count/max(1, stats['total_markers'])*100:.1f}%)")
        report.append("")
        
        report.append("--- Top Files with Quantum Markers ---")
        for i, file_info in enumerate(stats['top_files'][:10], 1):
            report.append(f"{i}. {file_info['path']} - {file_info['total']} markers")
            if file_info.get('gene_ids'):
                report.append(f"   Quantum IDs: {', '.join(file_info['gene_ids'][:3])}{' ...' if len(file_info['gene_ids']) > 3 else ''}")
        
        return "\n".join(report)


def main():
    """Main entry point for the script"""
    ensure_logs_dir()
    
    parser = argparse.ArgumentParser(description="Analyze quantum gene markers in project files")
    parser.add_argument("directory", nargs="?", default=".", 
                        help="Directory to analyze (default: current directory)")
    parser.add_argument("-o", "--output", help="Output file for JSON results")
    parser.add_argument("-r", "--report", help="Output file for human-readable report")
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = QuantumGeneAnalyzer(args.directory)
    
    # Analyze files
    stats = analyzer.analyze_directory()
    
    # Generate report
    report = analyzer.generate_report()
    print(report)
    
    # Save JSON results if requested
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        logger.info(f"JSON statistics saved to {args.output}")
    
    # Save report if requested
    if args.report:
        with open(args.report, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to {args.report}")


if __name__ == "__main__":
    main() 

    """
    # """
量子基因编码: QE-QUA-38E8A4BB7187
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""    """
    