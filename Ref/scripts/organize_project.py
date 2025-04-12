#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
项目结构优化脚本
用于创建标准目录结构、分析项目结构并组织文件
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(project_root, 'Ref/logs/project_organizer.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('ProjectOrganizer')

class ProjectOrganizer:
    """项目结构组织器，封装目录结构优化和文件组织功能"""
    
    def __init__(self):
        """初始化项目组织器"""
        self.project_root = project_root
        self.logs_dir = os.path.join(self.project_root, 'Ref/logs')
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # 尝试导入目录结构优化器
        try:
            from Ref.utils.directory_structure_optimizer import get_directory_optimizer
            self.optimizer = get_directory_optimizer()
            self.optimizer_available = True
        except ImportError as e:
            logger.error(f"无法导入目录结构优化器: {str(e)}")
            self.optimizer_available = False
        
        # 尝试导入文件组织监护器
        try:
            from Ref.utils.file_organization_guardian import get_guardian
            self.guardian = get_guardian()
            self.guardian_available = True
        except ImportError as e:
            logger.error(f"无法导入文件组织监护器: {str(e)}")
            self.guardian_available = False
        
        # 主要模块列表
        self.main_modules = ['QSM', 'WeQ', 'SOM', 'Ref', 'QEntL']
        
        logger.info(f"项目组织器初始化完成，项目根目录: {self.project_root}")
    
    def create_standard_structure(self):
        """创建标准目录结构"""
        if not self.optimizer_available:
            logger.error("目录结构优化器不可用，无法创建标准目录结构")
            return {"error": "目录结构优化器不可用"}
        
        logger.info("开始创建标准目录结构...")
        results = self.optimizer.create_standard_directory_structure()
        
        logger.info(f"标准目录结构创建完成: 创建 {len(results['created_dirs'])} 个目录, "
                   f"已存在 {len(results['existing_dirs'])} 个目录, "
                   f"发生 {len(results['errors'])} 个错误")
        
        return results
    
    def analyze_project(self, output_file=None):
        """分析项目结构"""
        if not self.optimizer_available:
            logger.error("目录结构优化器不可用，无法分析项目结构")
            return {"error": "目录结构优化器不可用"}
        
        logger.info("开始分析项目结构...")
        report = self.optimizer.analyze_project_structure()
        
        # 保存报告到文件
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                logger.info(f"分析报告已保存至: {output_file}")
            except Exception as e:
                logger.error(f"保存分析报告失败: {str(e)}")
        
        # 打印简要报告
        print(f"\n项目根目录: {report['project_root']}")
        print(f"总文件数: {report['file_counts']['total']}")
        print(f"总目录数: {report['directory_counts']['total']}")
        
        print("\n模块概况:")
        for module, module_info in report['modules'].items():
            print(f"- {module}: {module_info['file_count']} 文件, {module_info['directory_count']} 目录")
            if module_info['missing_standard_dirs']:
                print(f"  缺失目录: {', '.join(module_info['missing_standard_dirs'])}")
        
        print("\n建议:")
        if report['recommendations']:
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"{i}. {rec}")
        else:
            print("无优化建议")
        
        return report
    
    def register_files(self):
        """注册现有文件到监控系统"""
        if not self.guardian_available:
            logger.error("文件组织监护器不可用，无法注册文件")
            return {"error": "文件组织监护器不可用"}
        
        logger.info("开始注册现有文件...")
        stats = self.guardian.register_existing_files()
        
        print("\n注册完成:")
        print(f"- 扫描文件数: {stats['scanned']}")
        print(f"- 成功注册数: {stats['registered']}")
        print(f"- 跳过文件数: {stats['skipped']}")
        print(f"- 失败文件数: {stats['failed']}")
        
        return stats
    
    def organize_module(self, module_name, apply=False):
        """组织模块文件"""
        if not self.optimizer_available:
            logger.error("目录结构优化器不可用，无法组织文件")
            return {"error": "目录结构优化器不可用"}
        
        if module_name not in self.main_modules:
            logger.warning(f"未知模块: {module_name}")
            print(f"警告: {module_name} 不是主要模块。有效的模块有: {', '.join(self.main_modules)}")
        
        dry_run = not apply
        action = "模拟组织" if dry_run else "组织"
        logger.info(f"开始{action} {module_name} 模块的文件...")
        
        results = self.optimizer.organize_files(module_name, dry_run=dry_run)
        
        if 'error' in results:
            logger.error(f"组织模块文件失败: {results['error']}")
            print(f"错误: {results['error']}")
            return results
        
        print(f"\n{action}完成:")
        print(f"- 移动文件数: {len(results['moved_files'])}")
        print(f"- 保持不变文件数: {len(results['unchanged_files'])}")
        print(f"- 错误数: {len(results['errors'])}")
        
        if results['errors']:
            print("\n错误:")
            for error in results['errors']:
                print(f"- {error}")
        
        if dry_run:
            print("\n注意: 这是一个模拟操作，未实际移动文件。使用 --apply 参数执行实际移动。")
        
        return results
    
    def check_project(self, auto_fix=False):
        """检查项目是否符合标准"""
        if not self.guardian_available:
            logger.error("文件组织监护器不可用，无法检查项目标准")
            return {"error": "文件组织监护器不可用"}
        
        logger.info(f"开始检查项目标准{' (自动修复)' if auto_fix else ''}...")
        results = self.guardian.enforce_project_standards(auto_fix=auto_fix)
        
        print("\n检查完成:")
        print(f"- 检查项数: {len(results['checks'])}")
        print(f"- 通过数: {len([c for c in results['checks'] if c['status'] == 'pass'])}")
        print(f"- 失败数: {len([c for c in results['checks'] if c['status'] == 'fail'])}")
        print(f"- 修复数: {len([c for c in results['checks'] if c.get('fixed', False)])}")
        
        # 显示失败项
        failed_checks = [c for c in results['checks'] if c['status'] == 'fail']
        if failed_checks:
            print("\n失败项:")
            for i, check in enumerate(failed_checks, 1):
                print(f"{i}. {check['description']}: {check.get('message', '无详细信息')}")
        
        return results
    
    def run_organize_workflow(self, module=None, apply=False, create_dirs=True, register=True):
        """运行完整的组织工作流"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "steps": [],
            "errors": []
        }
        
        # 步骤1：创建标准目录结构
        if create_dirs:
            print("\n===== 步骤1：创建标准目录结构 =====")
            try:
                dirs_result = self.create_standard_structure()
                results["steps"].append({
                    "name": "create_structure",
                    "success": "error" not in dirs_result,
                    "details": dirs_result
                })
            except Exception as e:
                error_msg = f"创建标准目录结构失败: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        # 步骤2：注册现有文件
        if register:
            print("\n===== 步骤2：注册现有文件 =====")
            try:
                register_result = self.register_files()
                results["steps"].append({
                    "name": "register_files",
                    "success": "error" not in register_result,
                    "details": register_result
                })
            except Exception as e:
                error_msg = f"注册文件失败: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        # 步骤3：分析项目结构
        print("\n===== 步骤3：分析项目结构 =====")
        try:
            analysis_result = self.analyze_project()
            results["steps"].append({
                "name": "analyze_project",
                "success": "error" not in analysis_result,
                "details": {
                    "file_count": analysis_result.get("file_counts", {}).get("total", 0),
                    "dir_count": analysis_result.get("directory_counts", {}).get("total", 0),
                    "recommendations_count": len(analysis_result.get("recommendations", []))
                }
            })
        except Exception as e:
            error_msg = f"分析项目结构失败: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
        
        # 步骤4：组织模块文件
        if module:
            print(f"\n===== 步骤4：组织{module}模块文件 =====")
            try:
                organize_result = self.organize_module(module, apply=apply)
                results["steps"].append({
                    "name": "organize_module",
                    "module": module,
                    "success": "error" not in organize_result,
                    "details": organize_result
                })
            except Exception as e:
                error_msg = f"组织模块 {module} 的文件失败: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        else:
            # 如果没有指定模块，尝试组织所有主要模块
            print("\n===== 步骤4：组织所有模块文件 =====")
            for module_name in self.main_modules:
                print(f"\n--- 组织{module_name}模块 ---")
                try:
                    organize_result = self.organize_module(module_name, apply=apply)
                    results["steps"].append({
                        "name": "organize_module",
                        "module": module_name,
                        "success": "error" not in organize_result,
                        "details": organize_result
                    })
                except Exception as e:
                    error_msg = f"组织模块 {module_name} 的文件失败: {str(e)}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
        
        # 步骤5：检查项目标准
        print("\n===== 步骤5：检查项目标准 =====")
        try:
            check_result = self.check_project(auto_fix=apply)
            results["steps"].append({
                "name": "check_project",
                "success": "error" not in check_result,
                "details": check_result
            })
        except Exception as e:
            error_msg = f"检查项目标准失败: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
        
        # 输出总结
        print("\n===== 执行完成 =====")
        print(f"总步骤数: {len(results['steps'])}")
        print(f"成功步骤: {len([s for s in results['steps'] if s['success']])}")
        print(f"错误数: {len(results['errors'])}")
        
        if results["errors"]:
            print("\n发生的错误:")
            for i, error in enumerate(results["errors"], 1):
                print(f"{i}. {error}")
        
        return results


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="QSM项目结构优化工具")
    parser.add_argument('--structure', action='store_true', help='创建标准目录结构')
    parser.add_argument('--analyze', action='store_true', help='分析当前项目结构')
    parser.add_argument('--register', action='store_true', help='注册现有文件到监控系统')
    parser.add_argument('--organize', type=str, metavar='MODULE', help='组织指定模块的文件')
    parser.add_argument('--check', action='store_true', help='检查项目是否符合标准')
    parser.add_argument('--workflow', action='store_true', help='运行完整的组织工作流')
    parser.add_argument('--apply', action='store_true', help='实际执行文件移动和修复（默认为模拟模式）')
    parser.add_argument('--output', type=str, help='输出报告到指定文件')
    
    args = parser.parse_args()
    
    # 创建项目组织器
    organizer = ProjectOrganizer()
    
    # 根据命令行参数执行相应操作
    if args.workflow:
        organizer.run_organize_workflow(
            module=args.organize,
            apply=args.apply,
            create_dirs=True,
            register=True
        )
    elif args.structure:
        organizer.create_standard_structure()
    elif args.analyze:
        organizer.analyze_project(output_file=args.output)
    elif args.register:
        organizer.register_files()
    elif args.organize:
        organizer.organize_module(args.organize, apply=args.apply)
    elif args.check:
        organizer.check_project(auto_fix=args.apply)
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 