#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件路径管理模块
提供文件路径解析和管理功能
"""

from .file_path_manager import FilePathManager, resolve_path, get_all_files, move_file
from .file_path_helpers import path_manager_available, patch_import_system

__all__ = [
    'FilePathManager',
    'resolve_path',
    'get_all_files',
    'move_file',
    'path_manager_available',
    'patch_import_system'
] 