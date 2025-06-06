#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cursor性能优化工具
用于优化Cursor编辑器在大型项目中的性能，防止卡顿崩溃
"""

import os
import json
import shutil
import sys
import platform
import subprocess
from pathlib import Path
import tempfile
import time

# 脚本配置
CONFIG = {
    "vscode_settings_path": ".vscode/settings.json",
    "cursorignore_path": ".cursorignore",
    "cursor_app_data": {
        "win32": os.path.expandvars("%APPDATA%\\Cursor"),
        "darwin": os.path.expanduser("~/Library/Application Support/Cursor"),
        "linux": os.path.expanduser("~/.config/Cursor"),
    },
    "exclude_dirs": [
        ".git",
        "__pycache__",
        ".venv",
        "node_modules",
        "backups",
        "quantum_backups",
        "logs",
        "test_logs",
        "quantum_data",
        "processed_data",
        "crawler_data",
        "training_data",
        "models"
    ],
    "exclude_files": [
        "*.log",
        "*.pkl",
        "*.bin",
        "*.dat",
        "*.h5",
        "*.jpg",
        "*.png",
        "*.json"
    ],
    "include_files": [
        "package.json",
        "config/project_config_quantum.json"
    ],
    "cursor_cache_dirs": [
        "Code Cache",
        "GPUCache",
        "CachedData"
    ]
}

# VSCode优化设置
VSCODE_SETTINGS = {
    "files.exclude": {
        "**/__pycache__": True,
        "**/node_modules": True,
        "**/env": True,
        "**/*.log": True,
        "**/*.pkl": True,
        "**/*.bin": True,
        "**/*.dat": True,
        "**/*.h5": True
    },
    "search.exclude": {
        "**/node_modules": True,
        "**/env": True,
        "**/*.log": True,
        "**/*.pkl": True,
        "**/*.bin": True,
        "**/*.dat": True,
        "**/*.h5": True,
        "**/quantum_data": True,
        "**/processed_data": True,
        "**/crawler_data": True,
        "**/training_data": True,
        "**/models": True,
        "**/logs": True,
        "**/test_logs": True,
        "**/quantum_backups": True,
        "**/backups": True
    },
    "editor.formatOnSave": True,
    "python.linting.enabled": False,
    "python.analysis.diagnosticMode": "openFilesOnly",
    "python.analysis.indexing": False,
    "files.watcherExclude": {
        "**/.git/objects/**": True,
        "**/.git/subtree-cache/**": True,
        "**/node_modules/**": True,
        "**/env/**": True,
        "**/quantum_data/**": True,
        "**/processed_data/**": True,
        "**/crawler_data/**": True,
        "**/training_data/**": True,
        "**/models/**": True,
        "**/logs/**": True,
        "**/test_logs/**": True,
        "**/quantum_backups/**": True,
        "**/backups/**": True
    },
    "editor.quickSuggestions": {
        "other": False,
        "comments": False,
        "strings": False
    },
    "editor.suggest.showSnippets": False,
    "editor.suggest.preview": False,
    "editor.hover.delay": 1000,
    "workbench.editor.enablePreview": False,
    "workbench.editor.highlightModifiedTabs": False,
    "explorer.autoReveal": False
}

class CursorOptimizer:
    def __init__(self):
        self.project_root = Path.cwd().absolute()
        self.system = platform.system().lower()
        if self.system == "windows":
            self.system = "win32"
        elif self.system == "darwin":
            self.system = "darwin"
        else:
            self.system = "linux"
            
    def optimize_all(self):
        """执行所有优化"""
        print("开始执行Cursor性能优化...")
        
        # 1. 创建.vscode设置
        self.create_vscode_settings()
        
        # 2. 创建.cursorignore文件
        self.create_cursorignore()
        
        # 3. 清理Cursor缓存
        self.clean_cursor_cache()
        
        # 4. 关闭不必要的后台进程
        self.kill_unnecessary_processes()
        
        print("优化完成！")
        print("\n使用建议:")
        print("1. 重启Cursor编辑器")
        print("2. 启动时使用命令行参数: cursor.exe --max-old-space-size=8192 --js-flags=\"--expose-gc\"")
        print("3. 在编辑器中避免同时打开过多大型文件")
<<<<<<< HEAD
        print("/n如需恢复默认设置，请删除.vscode/settings.json和.cursorignore文件")
=======
        print("\n如需恢复默认设置，请删除.vscode/settings.json和.cursorignore文件")
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
        
    def create_vscode_settings(self):
        """创建VSCode/Cursor优化设置"""
        vscode_dir = self.project_root / ".vscode"
        vscode_dir.mkdir(exist_ok=True)
        
        settings_file = vscode_dir / "settings.json"
        
        # 如果文件已存在，备份它
        if settings_file.exists():
            backup_file = vscode_dir / "settings.json.bak"
            shutil.copy2(settings_file, backup_file)
            print(f"已备份现有设置到 {backup_file}")
        
        # 写入新设置
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(VSCODE_SETTINGS, f, indent=4)
        
        print(f"已创建优化的VSCode/Cursor设置: {settings_file}")
    
    def create_cursorignore(self):
        """创建.cursorignore文件"""
        cursorignore_file = self.project_root / CONFIG["cursorignore_path"]
        
        # 如果文件已存在，备份它
        if cursorignore_file.exists():
            backup_file = self.project_root / f"{CONFIG['cursorignore_path']}.bak"
            shutil.copy2(cursorignore_file, backup_file)
            print(f"已备份现有.cursorignore到 {backup_file}")
        
        # 构建忽略内容
        ignore_content = "# Cursor忽略配置文件\n# 排除大型数据目录和生成文件，减轻Cursor负担\n\n"
        
        # 添加目录
        ignore_content += "# 数据目录\n"
        for dir_name in CONFIG["exclude_dirs"]:
<<<<<<< HEAD
            ignore_content += f"{dir_name}//n"
=======
            ignore_content += f"{dir_name}/\n"
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
        
        # 添加文件
        ignore_content += "\n# 生成的文件\n"
        for file_pattern in CONFIG["exclude_files"]:
            ignore_content += f"{file_pattern}\n"
        
        # 添加例外
        ignore_content += "\n# 例外（不忽略这些文件）\n"
        for file_pattern in CONFIG["include_files"]:
            ignore_content += f"!{file_pattern}\n"
        
        # 写入文件
        with open(cursorignore_file, "w", encoding="utf-8") as f:
            f.write(ignore_content)
        
        print(f"已创建优化的.cursorignore: {cursorignore_file}")
    
    def clean_cursor_cache(self):
        """清理Cursor缓存"""
        cursor_data_dir = CONFIG["cursor_app_data"].get(self.system)
        if not cursor_data_dir or not os.path.exists(cursor_data_dir):
            print(f"找不到Cursor数据目录: {cursor_data_dir}")
            return
        
        for cache_dir in CONFIG["cursor_cache_dirs"]:
            cache_path = os.path.join(cursor_data_dir, cache_dir)
            if os.path.exists(cache_path):
                try:
                    if os.path.isdir(cache_path):
                        shutil.rmtree(cache_path)
                    else:
                        os.remove(cache_path)
                    print(f"已清理Cursor缓存: {cache_path}")
                except Exception as e:
                    print(f"清理缓存失败 {cache_path}: {e}")
        
        print("已清理Cursor缓存")
    
    def kill_unnecessary_processes(self):
        """关闭不必要的后台进程"""
        processes_to_kill = ["node.exe", "python.exe"]
        
        try:
            if self.system == "win32":
                for proc in processes_to_kill:
                    os.system(f"taskkill /f /im \"{proc}\" /t 2>nul")
            else:
                for proc in processes_to_kill:
                    os.system(f"pkill -f {proc} 2>/dev/null")
            
            print("已关闭可能影响性能的后台进程")
        except Exception as e:
            print(f"关闭后台进程时出错: {e}")
    
    def create_cursor_shortcut(self):
        """创建优化的Cursor快捷方式（仅Windows）"""
        if self.system != "win32":
            print("创建快捷方式功能仅支持Windows")
            return
        
        try:
            # 查找Cursor安装路径
            cursor_path = ""
            possible_paths = [
                os.path.expandvars("%LOCALAPPDATA%\\Programs\\Cursor\\Cursor.exe"),
                os.path.expandvars("%PROGRAMFILES%\\Cursor\\Cursor.exe"),
                os.path.expandvars("%PROGRAMFILES(X86)%\\Cursor\\Cursor.exe")
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    cursor_path = path
                    break
            
            if not cursor_path:
                print("找不到Cursor安装路径")
                return
            
            # 创建VBS脚本来生成快捷方式
            desktop = os.path.expandvars("%USERPROFILE%\\Desktop")
            shortcut_path = os.path.join(desktop, "Cursor (优化).lnk")
            
            vbs_script = f'''
Set WshShell = WScript.CreateObject("WScript.Shell")
Set shortcut = WshShell.CreateShortcut("{shortcut_path}")
shortcut.TargetPath = "{cursor_path}"
shortcut.Arguments = "--max-old-space-size=8192 --js-flags=""--expose-gc"""
shortcut.Description = "优化的Cursor启动方式"
shortcut.Save
'''
            
            # 写入临时VBS文件
            fd, vbs_path = tempfile.mkstemp(suffix=".vbs")
            os.close(fd)
            
            with open(vbs_path, "w", encoding="utf-8") as f:
                f.write(vbs_script)
            
            # 执行VBS脚本
            os.system(f'cscript //NoLogo "{vbs_path}"')
            
            # 删除临时文件
            os.unlink(vbs_path)
            
            print(f"已创建优化的Cursor快捷方式: {shortcut_path}")
        except Exception as e:
            print(f"创建快捷方式失败: {e}")

if __name__ == "__main__":
    optimizer = CursorOptimizer()
    optimizer.optimize_all()
    
    # 如果是Windows，也创建快捷方式
    if platform.system().lower() == "windows":
<<<<<<< HEAD
        answer = input("/n是否创建优化的Cursor快捷方式？(y/n): ")
=======
        answer = input("\n是否创建优化的Cursor快捷方式？(y/n): ")
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
        if answer.lower() == "y":
            optimizer.create_cursor_shortcut()

"""

"""
量子基因编码: QE-CUR-59AF8CF03F28
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""

<<<<<<< HEAD
// 开发团队：中华 ZhoHo ，Claude

=======
// 开发团队：中华 ZhoHo ，Claude 
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
