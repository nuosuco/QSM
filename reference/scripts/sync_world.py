#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Auto Sync Script

This script is used to automatically sync the world directory from the root to each model's world directory
"""

import os
import sys
import shutil
import subprocess
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("world_sync.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("WorldSync")

# Project root directory
ROOT_DIR = Path(__file__).parent.absolute()

# Model directories
MODELS = ["QSM", "SOM", "WeQ", "Ref"]

def sync_world_to_models():
    """Sync world directory to each model"""
    source_dir = ROOT_DIR / "world"
    
    if not source_dir.exists():
        logger.error(f"Source directory {source_dir} does not exist")
        return False
    
    success = True
    
    for model in MODELS:
        target_dir = ROOT_DIR / model / "world"
        
        if not target_dir.exists():
            logger.info(f"Creating target directory {target_dir}")
            target_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Syncing {source_dir} to {target_dir}")
        
        try:
            # Use robocopy command to sync directories
            result = subprocess.run(
                ["robocopy", str(source_dir), str(target_dir), "/E", "/XO", "/S", "/NFL", "/NDL"],
                capture_output=True,
                text=True
            )
            
            if result.returncode in [0, 1]:  # robocopy returns 0 for no files copied, 1 for files copied
                logger.info(f"Successfully synced to {model}")
            else:
                logger.error(f"Failed to sync to {model}: {result.stderr}")
                success = False
                
        except Exception as e:
            logger.error(f"Error syncing to {model}: {str(e)}")
            success = False
    
    return success

def watch_and_sync():
    """Watch world directory changes and auto sync"""
    logger.info("Starting to watch world directory changes...")
    
    # Initial sync
    sync_world_to_models()
    
    # Get initial file state
    initial_state = {}
    for root, _, files in os.walk(ROOT_DIR / "world"):
        for file in files:
            file_path = Path(root) / file
            relative_path = file_path.relative_to(ROOT_DIR / "world")
            initial_state[str(relative_path)] = file_path.stat().st_mtime
    
    while True:
        time.sleep(5)  # Check every 5 seconds
        
        # Check file changes
        current_state = {}
        for root, _, files in os.walk(ROOT_DIR / "world"):
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(ROOT_DIR / "world")
                current_state[str(relative_path)] = file_path.stat().st_mtime
        
        # Check if there are changes
        if current_state != initial_state:
            logger.info("Detected world directory changes, starting sync...")
            sync_world_to_models()
            initial_state = current_state

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--watch":
        # Watch mode
        watch_and_sync()
    else:
        # Single sync
        if sync_world_to_models():
            logger.info("Sync completed")
        else:
            logger.error("Sync failed")
            sys.exit(1) 

"""
"""
量子基因编码: QE-SYN-462D2AF47F3B
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
