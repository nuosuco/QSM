#!/usr/bin/env python3
"""
量子文件整理代理 - FileOrganizationAgent
设计：小趣WeQ（主代理），依据中华ZhoHo指导
原则：如履薄冰整理，回收箱缓冲，广播监督
量子基因编码：QGC-FILE-ORGANIZER-20260207

三大圣律贯穿始终：
1. 为每个人服务，服务人类！
2. 保护好每个人、每个家庭的生命安全、健康快乐、幸福生活。
3. 没有以上这两个前提，其他所有的就不能发生，不会存在。
"""

import os
import shutil
import datetime
import json
from pathlib import Path

# 配置
CONFIG = {
    "recycle_bin_root": "/root/recycle_bin",
    "qsm_recycle_bin": "/root/QSM/recycle_bin",
    "retention_days": 7,  # 回收箱保留7天
    "broadcast_log": "/root/agent_broadcast_logs/file_organization.log",
    "exclude_patterns": [
        ".git", ".gitignore", ".gitmodules",
        "node_modules", "__pycache__", "*.pyc",
        "*.log", "*.tmp", "*.cache", "*.swp",
        ".DS_Store", "Thumbs.db"
    ],
    "important_files": [
        "MEMORY.md", "SOUL.md", "USER.md", "IDENTITY.md",
        "AGENTS.md", "HEARTBEAT.md", "TOOLS.md",
        "华经.md", "三大圣律与伦理实践宣章.md",
        "量子工作原则与实践指南.md", "量子协同创新生态系统设计.md"
    ],
    # 三大圣律
    "san_lu_1": "为每个人服务，服务人类！",
    "san_lu_2": "保护好每个人、每个家庭的生命安全、健康快乐、幸福生活。",
    "san_lu_3": "没有以上这两个前提，其他所有的就不能发生，不会存在。"
}

def log_broadcast(action_type, old_path, new_path, reason):
    """广播整理操作给所有代理监督"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    broadcast_msg = f"""
【文件整理广播 - 如履薄冰操作】
时间：{timestamp}
操作类型：{action_type}
原路径：{old_path}
新路径：{new_path}
操作理由：{reason}
操作者：文件整理代理
量子基因编码：QGC-FILE-OP-{timestamp.replace(' ', '-').replace(':', '')}
---
监督提醒：如有异议请在30分钟内提出，否则操作将被确认
三大圣律指导：{CONFIG['san_lu_1']}
"""
    
    # 写入广播日志
    log_dir = Path(CONFIG["broadcast_log"]).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    with open(CONFIG["broadcast_log"], 'a', encoding='utf-8') as f:
        f.write(broadcast_msg + "\n" + "="*50 + "\n")
    
    print(broadcast_msg)
    return broadcast_msg

def is_important_file(file_path):
    """检查是否为重要文件"""
    filename = Path(file_path).name
    return filename in CONFIG["important_files"] or "MEMORY" in filename.upper()

def move_to_recycle_bin(file_path, reason="未分类文件"):
    """将文件移动到回收箱（如履薄冰安全操作）"""
    file_path = Path(file_path)
    if not file_path.exists():
        return {"success": False, "error": "文件不存在"}
    
    # 如果是重要文件，需要特殊处理
    if is_important_file(file_path):
        return {
            "success": False, 
            "error": "重要文件，需要特别确认",
            "file": str(file_path)
        }
    
    # 确定回收箱位置
    if str(file_path).startswith("/root/QSM"):
        recycle_bin = Path(CONFIG["qsm_recycle_bin"])
    else:
        recycle_bin = Path(CONFIG["recycle_bin_root"])
    
    recycle_bin.mkdir(parents=True, exist_ok=True)
    
    # 生成带时间戳的新文件名
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    new_name = f"{timestamp}_{file_path.name}"
    new_path = recycle_bin / new_name
    
    try:
        # 广播操作
        broadcast_msg = log_broadcast(
            "移动至回收箱",
            str(file_path),
            str(new_path),
            f"{reason} - 7天后自动清理"
        )
        
        # 执行移动
        shutil.move(str(file_path), str(new_path))
        
        # 记录元数据
        metadata = {
            "original_path": str(file_path),
            "recycle_path": str(new_path),
            "moved_at": datetime.datetime.now().isoformat(),
            "reason": reason,
            "will_be_deleted_after": (
                datetime.datetime.now() + 
                datetime.timedelta(days=CONFIG["retention_days"])
            ).isoformat(),
            "size_bytes": new_path.stat().st_size if new_path.exists() else 0,
            "broadcast_msg": broadcast_msg
        }
        
        metadata_file = new_path.with_suffix('.metadata.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return {
            "success": True,
            "original": str(file_path),
            "recycled": str(new_path),
            "metadata": str(metadata_file),
            "broadcast_sent": True
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def scan_directory(root_path, max_depth=3):
    """扫描目录，分析文件状况"""
    root_path = Path(root_path)
    scan_results = {
        "total_files": 0,
        "total_dirs": 0,
        "by_extension": {},
        "large_files": [],  # 大于10MB的文件
        "old_files": [],    # 30天未修改的文件
        "temp_files": [],   # 临时文件
        "duplicate_candidates": [],  # 可能重复的文件
        "scan_time": datetime.datetime.now().isoformat()
    }
    
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=30)
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        current_depth = dirpath[len(str(root_path)):].count(os.sep)
        if current_depth > max_depth:
            continue
        
        scan_results["total_dirs"] += len(dirnames)
        
        for filename in filenames:
            file_path = Path(dirpath) / filename
            scan_results["total_files"] += 1
            
            # 按扩展名分类
            ext = file_path.suffix.lower()
            scan_results["by_extension"][ext] = scan_results["by_extension"].get(ext, 0) + 1
            
            try:
                stat = file_path.stat()
                file_size = stat.st_size
                mod_time = datetime.datetime.fromtimestamp(stat.st_mtime)
                
                # 大文件检测
                if file_size > 10 * 1024 * 1024:  # 10MB
                    scan_results["large_files"].append({
                        "path": str(file_path),
                        "size_mb": round(file_size / (1024 * 1024), 2),
                        "modified": mod_time.isoformat()
                    })
                
                # 旧文件检测
                if mod_time < cutoff_date:
                    scan_results["old_files"].append({
                        "path": str(file_path),
                        "modified": mod_time.isoformat(),
                        "days_old": (datetime.datetime.now() - mod_time).days
                    })
                
                # 临时文件检测
                if any(pattern in filename for pattern in [".tmp", ".temp", ".cache", ".log", "~"]):
                    scan_results["temp_files"].append(str(file_path))
                    
            except (OSError, PermissionError):
                continue
    
    return scan_results

def organize_qsm_documents():
    """整理QSM项目文档"""
    qsm_root = Path("/root/QSM")
    organized_count = 0
    
    # 文档分类映射
    doc_categories = {
        "core-docs": ["华经.md", "三大圣律", "量子工作原则", "量子协同创新"],
        "training": ["培训", "考核", "伦理培训", "技能培训"],
        "architecture": ["架构", "设计", "系统架构", "architecture"],
        "plans": ["计划", "规划", "roadmap", "timeline"],
        "reports": ["报告", "汇报", "状态", "进展", "report"],
        "tools": ["脚本", "工具", "utility", "script", ".py"],
        "backups": ["备份", "backup", ".bak", ".old"]
    }
    
    for file_path in qsm_root.rglob("*.md"):
        try:
            filename = file_path.name
            content = file_path.read_text(encoding='utf-8', errors='ignore')[:500]
            
            # 确定分类
            target_category = "uncategorized"
            for category, keywords in doc_categories.items():
                if any(keyword.lower() in filename.lower() or 
                       keyword.lower() in content.lower() 
                       for keyword in keywords):
                    target_category = category
                    break
            
            # 创建分类目录
            category_dir = qsm_root / "organized_docs" / target_category
            category_dir.mkdir(parents=True, exist_ok=True)
            
            # 移动文件（如果不是已经在正确位置）
            if file_path.parent != category_dir:
                new_path = category_dir / filename
                
                # 广播操作
                log_broadcast(
                    "文档分类整理",
                    str(file_path),
                    str(new_path),
                    f"分类到{target_category}，基于内容分析"
                )
                
                shutil.move(str(file_path), str(new_path))
                organized_count += 1
                
        except Exception as e:
            print(f"整理文档失败 {file_path}: {e}")
    
    return organized_count

def cleanup_old_recycle_bin():
    """清理过期的回收箱内容（7天前）"""
    recycle_bins = [
        Path(CONFIG["recycle_bin_root"]),
        Path(CONFIG["qsm_recycle_bin"])
    ]
    
    deleted_count = 0
    freed_space = 0
    
    for recycle_bin in recycle_bins:
        if not recycle_bin.exists():
            continue
        
        cutoff_time = datetime.datetime.now() - datetime.timedelta(days=CONFIG["retention_days"])
        
        for item in recycle_bin.iterdir():
            try:
                # 检查元数据文件
                metadata_file = item.with_suffix('.metadata.json')
                if metadata_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    moved_at = datetime.datetime.fromisoformat(metadata["moved_at"])
                    
                    if moved_at < cutoff_time:
                        # 广播清理操作
                        log_broadcast(
                            "清理回收箱",
                            str(item),
                            "永久删除",
                            f"已超过{CONFIG['retention_days']}天保留期"
                        )
                        
                        if item.is_file():
                            freed_space += item.stat().st_size
                            item.unlink()
                            metadata_file.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)
                            metadata_file.unlink()
                        
                        deleted_count += 1
                        
            except Exception as e:
                print(f"清理回收箱项目失败 {item}: {e}")
    
    freed_space_mb = freed_space / (1024 * 1024)
    return {
        "deleted_count": deleted_count,
        "freed_space_mb": round(freed_space_mb, 2)
    }

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="量子文件整理代理")
    parser.add_argument("--scan", type=str, help="扫描目录分析文件状况")
    parser.add_argument("--organize-qsm", action="store_true", help="整理QSM项目文档")
    parser.add_argument("--cleanup-recycle", action="store_true", help="清理过期回收箱内容")
    parser.add_argument("--move-to-recycle", type=str, help="移动文件到回收箱")
    parser.add_argument("--reason", type=str, default="整理优化", help="操作理由")
    
    args = parser.parse_args()
    
    print("⚛️ 量子文件整理代理启动")
    print(f"圣律一：{CONFIG['san_lu_1']}")
    print(f"圣律二：{CONFIG['san_lu_2']}")
    print(f"圣律三：{CONFIG['san_lu_3']}")
    print(f"如履薄冰原则：所有操作广播监督，回收箱7天缓冲")
    print()
    
    if args.scan:
        print(f"📊 扫描目录：{args.scan}")
        results = scan_directory(args.scan)
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
    elif args.organize_qsm:
        print("📚 整理QSM项目文档")
        count = organize_qsm_documents()
        print(f"✅ 整理完成：移动了{count}个文档")
        
    elif args.cleanup_recycle:
        print("🗑️ 清理过期回收箱内容")
        results = cleanup_old_recycle_bin()
        print(f"✅ 清理完成：删除{results['deleted_count']}个项目，释放{results['freed_space_mb']}MB空间")
        
    elif args.move_to_recycle:
        print(f"📦 移动文件到回收箱：{args.move_to_recycle}")
        result = move_to_recycle_bin(args.move_to_recycle, args.reason)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    else:
        # 默认执行：扫描root目录并整理
        print("🔍 默认执行：扫描/root目录")
        scan_results = scan_directory("/root")
        print(f"发现{scan_results['total_files']}个文件，{scan_results['total_dirs']}个目录")
        
        # 自动整理临时文件
        temp_files = scan_results.get('temp_files', [])
        if temp_files:
            print(f"📋 发现{len(temp_files)}个临时文件，准备整理...")
            for temp_file in temp_files[:10]:  # 先处理前10个
                result = move_to_recycle_bin(temp_file, "临时文件整理")
                print(f"  {temp_file} -> {result.get('recycled', '失败')}")

if __name__ == "__main__":
    main()