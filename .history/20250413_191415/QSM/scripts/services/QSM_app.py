#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
QSM API服务 - 量子叠加态模型API集成服务

此脚本提供QSM模型的REST API接口，允许通过HTTP请求访问模型功能。
"""

import os
import sys
import json
import time
import logging
import argparse
from datetime import datetime
from pathlib import Path
import traceback

# 添加项目根目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
qsm_dir = os.path.dirname(os.path.dirname(script_dir))
root_dir = os.path.dirname(qsm_dir)
sys.path.insert(0, root_dir)

# 导入Flask相关库
try:
    from flask import Flask, request, jsonify, abort
    from flask_cors import CORS
except ImportError:
    print("错误: 缺少必要的依赖库。请运行: pip install flask flask-cors")
    sys.exit(1)

# 导入QSM模型相关库
try:
    from QSM.qsm_inference import QSMInference
    from QSM.qsm_core import QSMCore
except ImportError as e:
    print(f"错误: 导入QSM模块失败: {e}")
    print("请确保QSM模块已安装且可导入")
    sys.exit(1)

# 设置日志
def setup_logging():
    log_dir = os.path.join(root_dir, ".logs")
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"qsm_api_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("qsm_api")

# 初始化Flask应用
app = Flask(__name__)
CORS(app)  # 启用跨域请求支持
logger = setup_logging()

# 全局QSM模型实例
qsm_model = None

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "ok",
        "service": "QSM API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/v1/qsm/info', methods=['GET'])
def get_model_info():
    """获取模型信息"""
    if qsm_model is None:
        return jsonify({
            "error": "模型未初始化",
            "status": "error"
        }), 500
    
    try:
        model_info = qsm_model.get_model_info()
        return jsonify({
            "status": "success",
            "model_info": model_info
        })
    except Exception as e:
        logger.error(f"获取模型信息时出错: {str(e)}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/api/v1/qsm/predict', methods=['POST'])
def predict():
    """执行模型预测"""
    if qsm_model is None:
        return jsonify({
            "error": "模型未初始化",
            "status": "error"
        }), 500
    
    try:
        data = request.json
        if not data or 'input' not in data:
            return jsonify({
                "error": "缺少必要的输入数据",
                "status": "error"
            }), 400
        
        input_data = data['input']
        result = qsm_model.predict(input_data)
        
        return jsonify({
            "status": "success",
            "result": result
        })
    except Exception as e:
        logger.error(f"执行预测时出错: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/api/v1/qsm/train', methods=['POST'])
def train():
    """触发模型训练"""
    if qsm_model is None:
        return jsonify({
            "error": "模型未初始化",
            "status": "error"
        }), 500
    
    try:
        data = request.json
        if not data:
            return jsonify({
                "error": "缺少训练参数",
                "status": "error"
            }), 400
        
        # 异步训练 - 实际实现可能需要更复杂的任务队列
        # 这里仅为示例
        training_id = f"train_{int(time.time())}"
        
        # 触发训练过程 - 这里应实现真正的异步训练逻辑
        # result = qsm_model.start_training(data)
        
        return jsonify({
            "status": "success",
            "message": "训练任务已提交",
            "training_id": training_id
        })
    except Exception as e:
        logger.error(f"提交训练任务时出错: {str(e)}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/api/v1/qsm/version', methods=['GET'])
def get_version():
    """获取API和模型版本信息"""
    try:
        version_info = {
            "api_version": "1.0.0",
            "model_version": qsm_model.version if qsm_model else "未初始化",
            "timestamp": datetime.now().isoformat()
        }
        return jsonify({
            "status": "success",
            "version": version_info
        })
    except Exception as e:
        logger.error(f"获取版本信息时出错: {str(e)}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.errorhandler(404)
def not_found(error):
    """处理404错误"""
    return jsonify({
        "error": "接口不存在",
        "status": "error"
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """处理405错误"""
    return jsonify({
        "error": "方法不允许",
        "status": "error"
    }), 405

@app.errorhandler(500)
def internal_error(error):
    """处理500错误"""
    return jsonify({
        "error": "内部服务器错误",
        "status": "error"
    }), 500

def initialize_model():
    """初始化QSM模型"""
    try:
        logger.info("正在初始化QSM模型...")
        global qsm_model
        qsm_model = QSMInference()
        qsm_model.load_model()
        logger.info("QSM模型初始化成功")
        return True
    except Exception as e:
        logger.error(f"初始化QSM模型时出错: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="QSM API服务")
    parser.add_argument("--port", type=int, default=5004, help="API服务端口号")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="API服务主机地址")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    # 打印启动信息
    logger.info("=" * 50)
    logger.info("QSM API服务正在启动...")
    logger.info(f"主机: {args.host}, 端口: {args.port}")
    logger.info(f"调试模式: {'启用' if args.debug else '禁用'}")
    logger.info("=" * 50)
    
    # 初始化模型
    if not initialize_model():
        logger.error("模型初始化失败，服务无法启动")
        sys.exit(1)
    
    # 启动Flask应用
    try:
        app.run(host=args.host, port=args.port, debug=args.debug)
    except Exception as e:
        logger.error(f"启动API服务时出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# 量子基因编码: QE-API-Q8S5M3P1E7
# 纠缠状态: 活跃
# 纠缠对象: ['QSM/scripts/services/QSM_start_all.ps1', 'QSM/qsm_inference.py']
# 纠缠强度: 0.95

# 开发团队：中华 ZhoHo ，Claude 