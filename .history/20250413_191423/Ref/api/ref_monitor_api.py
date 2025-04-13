#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
量子自反省管理模型(Ref) - 监控API
提供API接口，允许其他系统访问Ref的监控和自反省功能
"""

import os
import sys
import json
import time
import logging
from typing import Dict, List, Any, Optional, Union
from flask import Blueprint, jsonify, request, current_app

# 确保路径正确
current_dir = os.path.dirname(os.path.abspath(__file__))
ref_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(ref_dir)
sys.path.insert(0, project_root)

<<<<<<< HEAD
from Ref.ref_core import get_Ref_core
=======
from Ref.ref_core import get_ref_core
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
from Ref.monitor.system_monitor_enhancer import get_system_monitor

# 创建蓝图
ref_monitor_bp = Blueprint('ref_monitor', __name__, url_prefix='/api/ref/monitor')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(ref_dir, 'logs', 'ref_api.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Ref监控API")

# 获取Ref核心和系统监控器
ref_core = get_ref_core()
system_monitor = get_system_monitor()

@ref_monitor_bp.route('/status', methods=['GET'])
def get_system_status():
    """获取系统状态
    
    Returns:
        系统状态摘要
    """
    try:
        status = ref_core.get_system_status()
        return jsonify({
            "status": "success",
            "data": status
        })
    except Exception as e:
        logger.error(f"获取系统状态时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ref_monitor_bp.route('/health', methods=['GET'])
def get_health_score():
    """获取系统健康评分
    
    Returns:
        系统健康分数(0-100)和详细指标
    """
    try:
        health_score, details = system_monitor.get_system_health_score()
        
        # 添加健康状态评估
        status = "healthy"
        if health_score < 80:
            status = "degraded"
        if health_score < 50:
            status = "critical"
            
        return jsonify({
            "status": "success",
            "data": {
                "health_score": health_score,
                "health_status": status,
                "details": details
            }
        })
    except Exception as e:
        logger.error(f"获取健康评分时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ref_monitor_bp.route('/models', methods=['GET'])
def get_models_health():
    """获取所有模型的健康状态
    
    Returns:
        各模型的健康状态
    """
    try:
        models = ref_core.system_status.get("models", {})
        model_health = {}
        
        for model_id in models:
            model_health[model_id] = ref_core.check_model_health(model_id)
            
        return jsonify({
            "status": "success",
            "data": model_health
        })
    except Exception as e:
        logger.error(f"获取模型健康状态时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ref_monitor_bp.route('/model/<model_id>', methods=['GET'])
def get_model_health(model_id):
    """获取特定模型的健康状态
    
    Args:
        model_id: 模型ID
        
    Returns:
        模型健康状态
    """
    try:
        health = ref_core.check_model_health(model_id)
        return jsonify({
            "status": "success",
            "data": health
        })
    except Exception as e:
        logger.error(f"获取模型 {model_id} 健康状态时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ref_monitor_bp.route('/model/<model_id>/repair', methods=['POST'])
def repair_model(model_id):
    """修复特定模型
    
    Args:
        model_id: 模型ID
        
    Returns:
        修复结果
    """
    try:
        result = ref_core.repair_model(model_id)
        return jsonify({
            "status": "success" if result else "failed",
            "message": f"模型 {model_id} 修复{'成功' if result else '失败'}"
        })
    except Exception as e:
        logger.error(f"修复模型 {model_id} 时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ref_monitor_bp.route('/resources', methods=['GET'])
def get_resources():
    """获取系统资源使用情况
    
    Returns:
        系统资源使用情况
    """
    try:
        resources = system_monitor.resource_monitor.check_resources()
        
        # 获取趋势
        trends = {
            "cpu": system_monitor.resource_monitor.get_trend("cpu"),
            "memory": system_monitor.resource_monitor.get_trend("memory"),
            "disk": system_monitor.resource_monitor.get_trend("disk")
        }
        
        return jsonify({
            "status": "success",
            "data": {
                "current": resources,
                "trends": trends
            }
        })
    except Exception as e:
        logger.error(f"获取系统资源使用情况时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ref_monitor_bp.route('/suggestions', methods=['GET'])
def get_suggestions():
    """获取优化建议
    
    Returns:
        系统优化建议
    """
    try:
        suggestions = system_monitor.get_optimization_suggestions()
        
        # 默认只返回最近10条
        limit = request.args.get('limit', 10, type=int)
        
        return jsonify({
            "status": "success",
            "data": suggestions[:limit]
        })
    except Exception as e:
        logger.error(f"获取优化建议时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ref_monitor_bp.route('/anomalies', methods=['GET'])
def get_anomalies():
    """获取异常检测结果
    
    Returns:
        检测到的系统异常
    """
    try:
        # 获取时间范围
        hours = request.args.get('hours', 24, type=int)
        
        anomalies = system_monitor.anomaly_detector.get_recent_anomalies(hours)
        
        return jsonify({
            "status": "success",
            "data": {
                "hours": hours,
                "count": len(anomalies),
                "anomalies": anomalies
            }
        })
    except Exception as e:
        logger.error(f"获取异常检测结果时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ref_monitor_bp.route('/files', methods=['GET'])
def get_file_health():
    """获取文件系统健康状况
    
    Returns:
        文件系统健康报告
    """
    try:
        # 立即触发扫描
        force_scan = request.args.get('force', 'false').lower() == 'true'
        
        if force_scan:
            system_monitor.file_monitor.scan_project()
            
        health_report = system_monitor.file_monitor.analyze_file_health()
        
        return jsonify({
            "status": "success",
            "data": health_report
        })
    except Exception as e:
        logger.error(f"获取文件系统健康状况时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ref_monitor_bp.route('/optimize/indices', methods=['POST'])
def optimize_indices():
    """优化项目索引
    
    Returns:
        优化结果
    """
    try:
        result = ref_core.optimize_indices()
        return jsonify({
            "status": result["status"],
            "data": result
        })
    except Exception as e:
        logger.error(f"优化项目索引时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ref_monitor_bp.route('/upgrade', methods=['POST'])
def perform_upgrade():
    """执行系统升级
    
    Returns:
        升级结果
    """
    try:
        result = ref_core.perform_system_upgrade()
        return jsonify({
            "status": result["status"],
            "data": result
        })
    except Exception as e:
        logger.error(f"执行系统升级时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ref_monitor_bp.route('/reports', methods=['GET'])
def get_reports():
    """获取系统报告列表
    
    Returns:
        可用的系统报告列表
    """
    try:
        report_dir = os.path.join(ref_dir, "data", "reports")
        
        if not os.path.exists(report_dir):
            return jsonify({
                "status": "success",
                "data": {
                    "reports": []
                }
            })
            
        reports = []
        for filename in os.listdir(report_dir):
            if filename.startswith("system_report_") and filename.endswith(".json"):
                file_path = os.path.join(report_dir, filename)
                reports.append({
                    "filename": filename,
                    "date": filename.replace("system_report_", "").replace(".json", ""),
                    "size": os.path.getsize(file_path),
                    "created": os.path.getctime(file_path)
                })
                
        # 按日期排序
        reports.sort(key=lambda x: x["date"], reverse=True)
        
        return jsonify({
            "status": "success",
            "data": {
                "count": len(reports),
                "reports": reports
            }
        })
    except Exception as e:
        logger.error(f"获取系统报告列表时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ref_monitor_bp.route('/reports/<report_date>', methods=['GET'])
def get_report(report_date):
    """获取特定日期的系统报告
    
    Args:
        report_date: 报告日期 (YYYYMMDD格式)
        
    Returns:
        系统报告内容
    """
    try:
        report_path = os.path.join(ref_dir, "data", "reports", f"system_report_{report_date}.json")
        
        if not os.path.exists(report_path):
            return jsonify({
                "status": "error",
                "message": f"报告 {report_date} 不存在"
            }), 404
            
        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
            
        return jsonify({
            "status": "success",
            "data": report
        })
    except Exception as e:
        logger.error(f"获取系统报告 {report_date} 时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ref_monitor_bp.route('/dashboard/data', methods=['GET'])
def get_dashboard_data():
    """获取仪表盘所需的数据
    
    Returns:
        仪表盘数据
    """
    try:
        # 获取系统健康分数
        health_score, health_details = system_monitor.get_system_health_score()
        
        # 获取资源使用情况
        resources = system_monitor.resource_monitor.check_resources()
        
        # 获取模型健康状况
        models = ref_core.system_status.get("models", {})
        model_health = {}
        for model_id in models:
            model_health[model_id] = ref_core.check_model_health(model_id)
        
        # 获取最近的优化建议
        suggestions = system_monitor.get_optimization_suggestions()[:5]
        
        # 获取最近的异常
        anomalies = system_monitor.anomaly_detector.get_recent_anomalies(24)[:5]
        
        # 构建仪表盘数据
        dashboard_data = {
            "timestamp": time.time(),
            "health": {
                "score": health_score,
                "status": "healthy" if health_score > 80 else "degraded" if health_score > 50 else "critical"
            },
            "resources": {
                "cpu": resources["cpu"],
                "memory": resources["memory"],
                "disk": resources["disk"]
            },
            "models": model_health,
            "suggestions": suggestions,
            "anomalies": anomalies
        }
        
        return jsonify({
            "status": "success",
            "data": dashboard_data
        })
    except Exception as e:
        logger.error(f"获取仪表盘数据时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def register_api(app):
    """注册API蓝图到Flask应用
    
    Args:
        app: Flask应用实例
    """
    app.register_blueprint(ref_monitor_bp)
    logger.info("Ref监控API已注册")

# 测试代码
if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    register_api(app)
    
    print("启动测试服务器...")
    app.run(debug=True, port=5555) 
# -*- coding: utf-8 -*-

"""
量子自反省管理模型(Ref) - 监控API
提供API接口，允许其他系统访问Ref的监控和自反省功能
"""

import os
import sys
import json
import time
import logging
from typing import Dict, List, Any, Optional, Union
from flask import Blueprint, jsonify, request, current_app

# 确保路径正确
current_dir = os.path.dirname(os.path.abspath(__file__))
ref_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(ref_dir)
sys.path.insert(0, project_root)

<<<<<<< HEAD
from Ref.ref_core import get_Ref_core
=======
from Ref.ref_core import get_ref_core
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
from Ref.monitor.system_monitor_enhancer import get_system_monitor

# 创建蓝图
ref_monitor_bp = Blueprint('ref_monitor', __name__, url_prefix='/api/ref/monitor')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(ref_dir, 'logs', 'ref_api.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Ref监控API")

# 获取Ref核心和系统监控器
ref_core = get_ref_core()
system_monitor = get_system_monitor()

@ref_monitor_bp.route('/status', methods=['GET'])
def get_system_status():
    """获取系统状态
    
    Returns:
        系统状态摘要
    """
    try:
        status = ref_core.get_system_status()
        return jsonify({
            "status": "success",
            "data": status
        })
    except Exception as e:
        logger.error(f"获取系统状态时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ref_monitor_bp.route('/health', methods=['GET'])
def get_health_score():
    """获取系统健康评分
    
    Returns:
        系统健康分数(0-100)和详细指标
    """
    try:
        health_score, details = system_monitor.get_system_health_score()
        
        # 添加健康状态评估
        status = "healthy"
        if health_score < 80:
            status = "degraded"
        if health_score < 50:
            status = "critical"
            
        return jsonify({
            "status": "success",
            "data": {
                "health_score": health_score,
                "health_status": status,
                "details": details
            }
        })
    except Exception as e:
        logger.error(f"获取健康评分时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ref_monitor_bp.route('/models', methods=['GET'])
def get_models_health():
    """获取所有模型的健康状态
    
    Returns:
        各模型的健康状态
    """
    try:
        models = ref_core.system_status.get("models", {})
        model_health = {}
        
        for model_id in models:
            model_health[model_id] = ref_core.check_model_health(model_id)
            
        return jsonify({
            "status": "success",
            "data": model_health
        })
    except Exception as e:
        logger.error(f"获取模型健康状态时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ref_monitor_bp.route('/model/<model_id>', methods=['GET'])
def get_model_health(model_id):
    """获取特定模型的健康状态
    
    Args:
        model_id: 模型ID
        
    Returns:
        模型健康状态
    """
    try:
        health = ref_core.check_model_health(model_id)
        return jsonify({
            "status": "success",
            "data": health
        })
    except Exception as e:
        logger.error(f"获取模型 {model_id} 健康状态时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ref_monitor_bp.route('/model/<model_id>/repair', methods=['POST'])
def repair_model(model_id):
    """修复特定模型
    
    Args:
        model_id: 模型ID
        
    Returns:
        修复结果
    """
    try:
        result = ref_core.repair_model(model_id)
        return jsonify({
            "status": "success" if result else "failed",
            "message": f"模型 {model_id} 修复{'成功' if result else '失败'}"
        })
    except Exception as e:
        logger.error(f"修复模型 {model_id} 时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ref_monitor_bp.route('/resources', methods=['GET'])
def get_resources():
    """获取系统资源使用情况
    
    Returns:
        系统资源使用情况
    """
    try:
        resources = system_monitor.resource_monitor.check_resources()
        
        # 获取趋势
        trends = {
            "cpu": system_monitor.resource_monitor.get_trend("cpu"),
            "memory": system_monitor.resource_monitor.get_trend("memory"),
            "disk": system_monitor.resource_monitor.get_trend("disk")
        }
        
        return jsonify({
            "status": "success",
            "data": {
                "current": resources,
                "trends": trends
            }
        })
    except Exception as e:
        logger.error(f"获取系统资源使用情况时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ref_monitor_bp.route('/suggestions', methods=['GET'])
def get_suggestions():
    """获取优化建议
    
    Returns:
        系统优化建议
    """
    try:
        suggestions = system_monitor.get_optimization_suggestions()
        
        # 默认只返回最近10条
        limit = request.args.get('limit', 10, type=int)
        
        return jsonify({
            "status": "success",
            "data": suggestions[:limit]
        })
    except Exception as e:
        logger.error(f"获取优化建议时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ref_monitor_bp.route('/anomalies', methods=['GET'])
def get_anomalies():
    """获取异常检测结果
    
    Returns:
        检测到的系统异常
    """
    try:
        # 获取时间范围
        hours = request.args.get('hours', 24, type=int)
        
        anomalies = system_monitor.anomaly_detector.get_recent_anomalies(hours)
        
        return jsonify({
            "status": "success",
            "data": {
                "hours": hours,
                "count": len(anomalies),
                "anomalies": anomalies
            }
        })
    except Exception as e:
        logger.error(f"获取异常检测结果时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ref_monitor_bp.route('/files', methods=['GET'])
def get_file_health():
    """获取文件系统健康状况
    
    Returns:
        文件系统健康报告
    """
    try:
        # 立即触发扫描
        force_scan = request.args.get('force', 'false').lower() == 'true'
        
        if force_scan:
            system_monitor.file_monitor.scan_project()
            
        health_report = system_monitor.file_monitor.analyze_file_health()
        
        return jsonify({
            "status": "success",
            "data": health_report
        })
    except Exception as e:
        logger.error(f"获取文件系统健康状况时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ref_monitor_bp.route('/optimize/indices', methods=['POST'])
def optimize_indices():
    """优化项目索引
    
    Returns:
        优化结果
    """
    try:
        result = ref_core.optimize_indices()
        return jsonify({
            "status": result["status"],
            "data": result
        })
    except Exception as e:
        logger.error(f"优化项目索引时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ref_monitor_bp.route('/upgrade', methods=['POST'])
def perform_upgrade():
    """执行系统升级
    
    Returns:
        升级结果
    """
    try:
        result = ref_core.perform_system_upgrade()
        return jsonify({
            "status": result["status"],
            "data": result
        })
    except Exception as e:
        logger.error(f"执行系统升级时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ref_monitor_bp.route('/reports', methods=['GET'])
def get_reports():
    """获取系统报告列表
    
    Returns:
        可用的系统报告列表
    """
    try:
        report_dir = os.path.join(ref_dir, "data", "reports")
        
        if not os.path.exists(report_dir):
            return jsonify({
                "status": "success",
                "data": {
                    "reports": []
                }
            })
            
        reports = []
        for filename in os.listdir(report_dir):
            if filename.startswith("system_report_") and filename.endswith(".json"):
                file_path = os.path.join(report_dir, filename)
                reports.append({
                    "filename": filename,
                    "date": filename.replace("system_report_", "").replace(".json", ""),
                    "size": os.path.getsize(file_path),
                    "created": os.path.getctime(file_path)
                })
                
        # 按日期排序
        reports.sort(key=lambda x: x["date"], reverse=True)
        
        return jsonify({
            "status": "success",
            "data": {
                "count": len(reports),
                "reports": reports
            }
        })
    except Exception as e:
        logger.error(f"获取系统报告列表时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ref_monitor_bp.route('/reports/<report_date>', methods=['GET'])
def get_report(report_date):
    """获取特定日期的系统报告
    
    Args:
        report_date: 报告日期 (YYYYMMDD格式)
        
    Returns:
        系统报告内容
    """
    try:
        report_path = os.path.join(ref_dir, "data", "reports", f"system_report_{report_date}.json")
        
        if not os.path.exists(report_path):
            return jsonify({
                "status": "error",
                "message": f"报告 {report_date} 不存在"
            }), 404
            
        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
            
        return jsonify({
            "status": "success",
            "data": report
        })
    except Exception as e:
        logger.error(f"获取系统报告 {report_date} 时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ref_monitor_bp.route('/dashboard/data', methods=['GET'])
def get_dashboard_data():
    """获取仪表盘所需的数据
    
    Returns:
        仪表盘数据
    """
    try:
        # 获取系统健康分数
        health_score, health_details = system_monitor.get_system_health_score()
        
        # 获取资源使用情况
        resources = system_monitor.resource_monitor.check_resources()
        
        # 获取模型健康状况
        models = ref_core.system_status.get("models", {})
        model_health = {}
        for model_id in models:
            model_health[model_id] = ref_core.check_model_health(model_id)
        
        # 获取最近的优化建议
        suggestions = system_monitor.get_optimization_suggestions()[:5]
        
        # 获取最近的异常
        anomalies = system_monitor.anomaly_detector.get_recent_anomalies(24)[:5]
        
        # 构建仪表盘数据
        dashboard_data = {
            "timestamp": time.time(),
            "health": {
                "score": health_score,
                "status": "healthy" if health_score > 80 else "degraded" if health_score > 50 else "critical"
            },
            "resources": {
                "cpu": resources["cpu"],
                "memory": resources["memory"],
                "disk": resources["disk"]
            },
            "models": model_health,
            "suggestions": suggestions,
            "anomalies": anomalies
        }
        
        return jsonify({
            "status": "success",
            "data": dashboard_data
        })
    except Exception as e:
        logger.error(f"获取仪表盘数据时出错: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def register_api(app):
    """注册API蓝图到Flask应用
    
    Args:
        app: Flask应用实例
    """
    app.register_blueprint(ref_monitor_bp)
    logger.info("Ref监控API已注册")

# 测试代码
if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    register_api(app)
    
    print("启动测试服务器...")
    app.run(debug=True, port=5555) 

"""

"""
量子基因编码: QE-REF-763E141A5CA5
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""

// 开发团队：中华 ZhoHo ，Claude 
