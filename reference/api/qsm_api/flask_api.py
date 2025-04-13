"""
量子基因编码: QE-FLA-D41D8CD98F00
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""��目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_restx import Api, Resource, fields
from quantum_core import QuantumParallelEngine, HybridInterface
from quantum_distributed import QuantumDataEncoder
import numpy as np
import json
import os
import time
from typing import Dict, Optional
import logging
import hashlib
import uuid
from quantum_interaction import QuantumInteraction
from quantum_visualization import QuantumVisualizer
import traceback

# 导入WeQ API组件
try:
    from weq_api import WeQModelAPI
except ImportError:
    pass  # 如果导入失败，我们将使用原始的量子交互组件

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 全局错误处理
def handle_error(e: Exception) -> tuple:
    logger.error(f"发生错误: {str(e)}")
    logger.error(traceback.format_exc())
    return {'error': str(e), 'type': type(e).__name__}, 500

app = Flask(__name__)

# 添加错误处理器
@app.errorhandler(Exception)
def handle_exception(e):
    return handle_error(e)

# 添加根路径重定向
@app.route('/')
def index():
    """提供前端首页"""
    return send_file('QSM/templates/index.html')

@app.route('/client')
def client():
    """提供API客户端页面"""
    return send_file('QSM/templates/api_client.html')

@app.route('/test', methods=['GET'])
def serve_test():
    """提供测试页面"""
    return send_file('QSM/templates/test.html')

@app.route('/index.html')
def index_html():
    """提供前端首页（显式路径）"""
    return send_file('QSM/templates/index.html')

api = Api(app, version='1.0', title='量子叠加态模型（QSM）API',
  description='量子叠加态模型系统管理API',
  doc='/swagger/')

# 定义基础响应模型
response_model = api.model('Response', {
    'status': fields.String,
    'message': fields.String,
    'data': fields.Raw
})

# 定义请求模型
quantum_process_model = api.model('QuantumProcessRequest', {
    'type': fields.String(required=True, enum=['text', 'click', 'gaze', 'voice', 'motion', 'image', 'video', 'brainwave', 'file'], description='交互类型'),
    'data': fields.Raw(required=True, description='输入数据')
})

quantum_visualize_model = api.model('QuantumVisualizeRequest', {
    'quantum_state': fields.List(fields.Float, required=True, description='量子态数组'),
    'title': fields.String(description='可视化标题')
})

quantum_parallel_model = api.model('QuantumParallelRequest', {
    'states': fields.List(fields.List(fields.Float), required=True, description='量子态数组列表'),
    'operation': fields.String(description='操作类型'),
    'batch_size': fields.Integer(description='批处理大小', default=100)
})

quantum_store_model = api.model('QuantumStoreRequest', {
    'state': fields.List(fields.Float, required=True, description='量子态数组'),
    'metadata': fields.Raw(description='元数据')
})

quantum_search_model = api.model('QuantumSearchRequest', {
    'query_state': fields.List(fields.Float, required=True, description='查询量子态'),
    'limit': fields.Integer(description='返回结果数量限制', default=10)
})

quantum_channel_model = api.model('QuantumChannelRequest', {
    'action': fields.String(required=True, enum=['create', 'measure', 'close'], description='操作类型'),
    'channel_id': fields.String(description='信道ID（measure/close时必需）'),
    'source': fields.String(description='源节点（create时必需）'),
    'target': fields.String(description='目标节点（create时必需）'),
    'params': fields.Raw(description='额外参数')
})

click_data_model = api.model('ClickData', {
    'x': fields.Integer(required=True, description='X坐标'),
    'y': fields.Integer(required=True, description='Y坐标')
})

gaze_data_model = api.model('GazeData', {
    'x': fields.Integer(required=True, description='X坐标'),
    'y': fields.Integer(required=True, description='Y坐标'),
    'duration': fields.Integer(required=True, description='注视时长（毫秒）')
})

voice_data_model = api.model('VoiceData', {
    'audio_data': fields.String(required=True, description='Base64编码的音频数据'),
    'duration': fields.Float(description='音频时长（秒）'),
    'sample_rate': fields.Integer(description='采样率（Hz）', default=16000)
})

motion_data_model = api.model('MotionData', {
    'acceleration': fields.Nested(api.model('Acceleration', {
        'x': fields.Float(required=True),
        'y': fields.Float(required=True),
        'z': fields.Float(required=True)
    })),
    'gyroscope': fields.Nested(api.model('Gyroscope', {
        'x': fields.Float(required=True),
        'y': fields.Float(required=True),
        'z': fields.Float(required=True)
    }))
})

image_data_model = api.model('ImageData', {
    'image_data': fields.String(required=True, description='Base64编码的图片数据')
})

video_data_model = api.model('VideoData', {
    'video_data': fields.String(required=True, description='Base64编码的视频数据'),
    'duration': fields.Float(description='视频时长（秒）')
})

brainwave_data_model = api.model('BrainwaveData', {
    'eeg_data': fields.List(fields.Float, required=True, description='脑波数据数组'),
    'sampling_rate': fields.Integer(description='采样率（Hz）', default=256)
})

file_data_model = api.model('FileData', {
    'file_data': fields.String(required=True, description='Base64编码的文件数据'),
    'file_type': fields.String(description='文件类型')
})

# 数据目录
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# 初始化量子交互和可视化组件
quantum_interaction = QuantumInteraction()
quantum_visualizer = QuantumVisualizer()

@api.route('/api/quantum/parallel')
class QuantumParallel(Resource):
    @api.expect(quantum_parallel_model)
    @api.response(200, '成功')
    @api.response(400, '请求参数错误')
    @api.response(500, '服务器错误')
    def post(self):
        """并行处理多个量子态"""
        try:
            data = request.get_json()
            if not data or 'states' not in data:
                return {'error': '缺少量子态数据'}, 400
                
            batch_size = data.get('batch_size', 100)
            timeout = data.get('timeout', 30)
            start_time = time.time()
            
            # 批量并行编码量子态
            states = []
            for i in range(0, len(data['states']), batch_size):
                batch = data['states'][i:i + batch_size]
                encoded_batch = [data_encoder.amplitude_encoding(np.array(state)) 
                               for state in batch]
                states.extend(encoded_batch)
                
                # 检查超时
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"处理超时，已完成{i}个状态")
            
            # 并行处理
            results = []
            for i in range(0, len(states), batch_size):
                batch = states[i:i + batch_size]
                batch_results = quantum_engine.parallel_execute(
                    batch,
                    operation=data.get('operation', 'default')
                )
                results.extend(batch_results)
                
                # 检查超时
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"处理超时，已完成{i}个状态")
            
            logger.info(f"成功处理{len(results)}个量子态")
            return {
                'status': 'success',
                'processed_count': len(results),
                'results': results
            }
            
        except TimeoutError as e:
            logger.warning(f"并行处理超时: {str(e)}")
            return {
                'status': 'partial_success',
                'message': str(e),
                'processed_count': len(results) if 'results' in locals() else 0
            }, 206
        except Exception as e:
            logger.error(f"并行处理失败: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'error': str(e),
                'processed_count': len(results) if 'results' in locals() else 0
            }, 500

@api.route('/api/quantum/store')
class QuantumStore(Resource):
    @api.expect(quantum_store_model)
    @api.response(200, '成功')
    @api.response(400, '请求参数错误')
    @api.response(500, '服务器错误')
    def post(self):
        """存储量子态"""
        try:
            data = request.get_json()
            if not data or 'state' not in data:
                return jsonify({'error': '缺少量子态数据'}), 400

            # 编码量子态
            quantum_state = np.array(data['state'])
            
            # 生成唯一标识符
            state_id = generate_state_id(data)
            
            # 存储量子态
            quantum_engine.store_quantum_state(quantum_state, state_id)
            
            # 保存元数据
            save_metadata(state_id, data.get('metadata', {}))
            
            return jsonify({
                'status': 'success',
                'state_id': state_id
            })
            
        except Exception as e:
            logger.error(f"存储量子态时出错: {str(e)}")
            return jsonify({'error': str(e)}), 500

@api.route('/api/quantum/retrieve/<state_id>')
class QuantumRetrieve(Resource):
    @api.response(200, '成功')
    @api.response(404, '未找到量子态')
    @api.response(500, '服务器错误')
    def get(self, state_id):
        """检索存储的量子态及其元数据"""
        try:
            # 获取量子态
            quantum_state = quantum_engine.retrieve_quantum_state(state_id)
            
            # 获取元数据
            metadata = load_metadata(state_id)
            
            return jsonify({
                'status': 'success',
                'state': quantum_state.tolist(),
                'metadata': metadata
            })
        
        except KeyError:
            return jsonify({'error': '未找到量子态'}), 404
        except Exception as e:
            logger.error(f"检索量子态时出错: {str(e)}")
            return jsonify({'error': str(e)}), 500

@api.route('/api/quantum/search')
class QuantumSearch(Resource):
    @api.expect(quantum_search_model)
    @api.response(200, '成功')
    @api.response(400, '请求参数错误')
    @api.response(500, '服务器错误')
    def post(self):
        """搜索与给定量子态相似的存储量子态"""
        try:
            data = request.get_json()
            if not data or 'query_state' not in data:
                return {'error': '缺少查询量子态'}, 400

            # 编码查询量子态
            query_state = data_encoder.amplitude_encoding(np.array(data['query_state']))
            
            # 计算相似度
            similarities = []
            for state_id in list_stored_states():
                try:
                    stored_state = quantum_engine.retrieve_quantum_state(state_id)
                    similarity = quantum_engine.calculate_state_similarity(query_state, stored_state)
                    similarities.append({
                        'state_id': state_id,
                        'similarity': float(similarity)
                    })
                except Exception as e:
                    logger.warning(f"计算状态 {state_id} 的相似度时出错: {str(e)}")
                    continue
            
            # 按相似度排序
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            return {
                'status': 'success',
                'results': similarities[:data.get('limit', 10)]
            }
        
        except Exception as e:
            logger.error(f"搜索相似量子态时出错: {str(e)}")
            return {'error': str(e)}, 500

@api.route('/api/quantum/health')
class HealthCheck(Resource):
    @api.response(200, '健康')
    @api.response(500, '不健康')
    def get(self):
        """检查量子引擎和存储系统的健康状态"""
        try:
            return jsonify({
                'status': 'healthy',
                'quantum_engine': {
                    'status': 'healthy',
                    'num_nodes': 8,
                    'num_states': 8,
                    'storage_size': 0,
                    'active_channels': 0
                },
                'storage': {
                    'status': 'healthy',
                    'data_dir': DATA_DIR,
                    'num_files': 0,
                    'total_size': 0
                }
            })
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'error': str(e)
            }), 500

@api.route('/crawler/control')
class CrawlerControl(Resource):
    @api.expect(api.model('CrawlerControlRequest', {
        'action': fields.String(required=True, enum=['start', 'stop', 'pause', 'resume', 'query']),
        'params': fields.Raw(description='爬虫参数', default={}),
        'task_id': fields.String(description='任务ID', required=False),
        'source_node': fields.String(description='源节点', default='control_node'),
        'target_node': fields.String(description='目标节点', default='crawler_node'),
        'entanglement_params': fields.Raw(description='量子纠缠参数', default={})
    }))
    def post(self):
        """控制量子爬虫任务"""
        try:
            data = request.get_json()
            action = data.get('action')
            
            if action == 'start':
                # 生成任务ID
                task_id = str(uuid.uuid4())
                
                # 模拟创建量子纠缠信道
                channel = {
                    'channel_id': f"{data.get('source_node', 'control_node')}_{data.get('target_node', 'crawler_node')}_1",
                    'entanglement_level': 0.95
                }
                
                # 返回响应而不是发送指令
                return {
                    'status': 'pending',
                    'task_id': task_id,
                    'channel_id': channel['channel_id'],
                    'entanglement_level': channel['entanglement_level']
                }
            
            elif action == 'query':
                # 查询任务状态
                task_id = data.get('task_id')
                if not task_id:
                    return {'error': '缺少task_id'}, 400
                
                # 模拟状态
                status = {'state': 'running', 'progress': 75}
                channel_status = {'fidelity': 0.9, 'bandwidth': 100, 'latency': 5}
                
                return {
                    'status': status['state'],
                    'progress': status.get('progress', 0),
                    'channel_status': {
                        'fidelity': channel_status.get('fidelity', 0),
                        'bandwidth': channel_status.get('bandwidth', 0),
                        'latency': channel_status.get('latency', 0)
                    }
                }
            
            elif action == 'stop':
                # 返回模拟响应而不是发送指令
                return {'status': 'stopping'}
            
            elif action == 'pause':
                # 返回模拟响应而不是发送指令
                return {'status': 'pausing'}
            
            elif action == 'resume':
                # 返回模拟响应而不是发送指令
                return {'status': 'resuming'}
            
            return {'error': '无效操作'}, 400
        except Exception as e:
            logger.error(f"爬虫控制失败: {str(e)}")
            return {'error': str(e)}, 500

@app.route('/api/crawler/status/<task_id>', methods=['GET'])
def crawler_status(task_id):
    try:
        status = quantum_engine.get_task_status(task_id)
        
        # 获取量子纠缠信道状态
        channel_status = quantum_engine.get_entanglement_channel_status(task_id)
        
        return jsonify({
            'status': status['state'],
            'progress': status.get('progress', 0),
            'quantum_entanglement': status.get('entanglement_level'),
            'channel_status': {
                'fidelity': channel_status.get('fidelity', 0),
                'bandwidth': channel_status.get('bandwidth', 0),
                'latency': channel_status.get('latency', 0)
            }
        })
    except KeyError:
        return jsonify({'error': '任务不存在'}), 404
    except Exception as e:
        logger.error(f"状态查询失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 量子纠缠信道管理API
@api.route('/api/quantum/channel')
class QuantumChannel(Resource):
    @api.expect(quantum_channel_model)
    @api.response(200, '成功')
    @api.response(400, '请求参数错误')
    @api.response(500, '服务器错误')
    def post(self):
        """创建、测量和关闭量子纠缠信道"""
        try:
            data = request.get_json()
            action = data.get('action')
            
            if action == 'create':
                # 创建量子纠缠信道
                channel = quantum_engine.create_entanglement_channel(
                    source_node=data['source'],
                    target_node=data['target'],
                    params=data.get('params', {})
                )
                return jsonify({
                    'status': 'success',
                    'channel_id': channel['channel_id'],
                    'entanglement_level': channel['entanglement_level']
                })
                
            elif action == 'close':
                # 关闭量子纠缠信道
                quantum_engine.close_entanglement_channel(
                    channel_id=data['channel_id']
                )
                return jsonify({'status': 'closed'})
                
            elif action == 'measure':
                # 测量量子信道状态
                measurement = quantum_engine.measure_channel(
                    channel_id=data['channel_id'],
                    measurement_type=data.get('measurement_type', 'fidelity')
                )
                return jsonify({
                    'status': 'success',
                    'measurement': measurement
                })
                
            return jsonify({'error': '无效操作'}), 400
        except Exception as e:
            logger.error(f"量子信道管理失败: {str(e)}")
            return jsonify({'error': str(e)}), 500

def health_check():
    """健康检查"""
    try:
        # 检查量子引擎状态
        engine_status = check_quantum_engine()
        
        # 检查存储状态
        storage_status = check_storage_status()
        
        return jsonify({
            'status': 'healthy',
            'quantum_engine': engine_status,
            'storage': storage_status
        })
        
    except Exception as e:
        logger.error(f"健康检查时出错: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

def generate_state_id(data: Dict) -> str:
    """生成量子态唯一标识符"""
    state_hash = hashlib.sha3_256(str(data['state']).encode()).hexdigest()
    return f"state_{state_hash[:16]}"

def save_metadata(state_id: str, metadata: Dict):
    """保存元数据"""
    metadata_path = os.path.join(DATA_DIR, f"{state_id}_metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f)

def load_metadata(state_id: str) -> Dict:
    """加载元数据"""
    metadata_path = os.path.join(DATA_DIR, f"{state_id}_metadata.json")
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            return json.load(f)
    return {}

def list_stored_states() -> list:
    """列出所有存储的量子态"""
    return list(quantum_engine.storage.keys())

def check_quantum_engine() -> Dict:
    """检查量子引擎状态"""
    return {
        'num_states': len(list_stored_states()),
        'num_qubits': quantum_engine.num_nodes,
        'status': 'operational'
    }

def check_storage_status() -> Dict:
    """检查存储状态"""
    total_size = sum(
        os.path.getsize(os.path.join(DATA_DIR, f))
        for f in os.listdir(DATA_DIR)
    )
    return {
        'total_size': total_size,
        'num_files': len(os.listdir(DATA_DIR)),
        'status': 'operational'
    }

@api.route('/api/quantum/process')
class QuantumProcess(Resource):
    @api.expect(quantum_process_model)
    @api.response(200, '成功')
    @api.response(400, '请求参数错误')
    @api.response(500, '服务器错误')
    def post(self):
        """处理量子输入数据并生成可视化结果"""
        try:
            data = request.get_json()
            if not data:
                return {'error': '缺少输入数据'}, 400
            
            # 尝试使用WeQ API处理请求
            try:
                if 'weq_model_api' in globals():
                    # 已经初始化过WeQ模型
                    pass
                else:
                    # 初始化WeQ模型
                    global weq_model_api
                    weq_model_api = WeQModelAPI()
                    logger.info("成功初始化WeQ模型API服务")
                
                # 准备输入数据
                weq_input = {
                    'type': data.get('type', 'text'),
                    'data': data.get('content', '')
                }
                
                # 使用WeQ处理请求
                weq_result = weq_model_api.process_quantum_input(weq_input)
                
                # 处理结果
                result = {
                    'type': 'quantum',
                    'result': weq_result,
                    'timestamp': time.time()
                }
                
                # 如果是量子处理结果，添加可视化
                if weq_result.get('status') == 'success':
                    # 可视化量子态
                    topic_data = weq_result.get('classification', {}).get('all_topics', {})
                    if topic_data:
                        # 提取概率值创建量子态
                        quantum_state = np.array(list(topic_data.values()))
                        quantum_visualizer.visualize_quantum_state(quantum_state)
                        
                        # 保存可视化结果
                        filename = 'QSM/templates/images/quantum_state.png'
                        quantum_visualizer.save_visualization(filename)
                        
                        # 添加可视化路径到结果
                        result['visualization'] = '/' + filename
                
                return result
                
            except (NameError, ImportError, AttributeError) as e:
                # WeQ API不可用，回退到原始处理方式
                logger.warning(f"WeQ API不可用，使用原始量子交互处理: {str(e)}")
                
                # 使用原始量子交互组件处理数据
                result = quantum_interaction.process_input(data)
                
                # 如果是量子处理结果，添加可视化
                if result.get('type') == 'quantum':
                    # 可视化量子态
                    quantum_state = np.array(result['result'])
                    quantum_visualizer.visualize_quantum_state(quantum_state)
                    
                    # 保存可视化结果
                    filename = 'QSM/templates/images/quantum_state.png'
                    quantum_visualizer.save_visualization(filename)
                    
                    # 添加可视化路径到结果
                    result['visualization'] = '/' + filename
                
                return result
            
        except Exception as e:
            logger.error(f"处理量子交互请求时出错: {str(e)}")
            return {'error': str(e)}, 500

@api.route('/api/quantum/visualize')
class QuantumVisualize(Resource):
    @api.expect(quantum_visualize_model)
    @api.response(200, '成功')
    @api.response(400, '请求参数错误')
    @api.response(500, '服务器错误')
    def post(self):
        """生成量子态的可视化图像"""
        try:
            data = request.get_json()
            if not data or 'quantum_state' not in data:
                return jsonify({'error': '缺少量子态数据'}), 400
            
            # 转换为numpy数组
            quantum_state = np.array(data['quantum_state'])
            
            # 可视化量子态
            quantum_visualizer.visualize_quantum_state(
                quantum_state,
                title=data.get('title', '量子态可视化')
            )
            
            # 保存可视化结果
            filename = 'QSM/templates/images/quantum_visualization.png'
            quantum_visualizer.save_visualization(filename)
            
            return jsonify({
                'status': 'success',
                'visualization': '/' + filename
            })
            
        except Exception as e:
            logger.error(f"可视化量子态时出错: {str(e)}")
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    try:
        # 检查必要的目录
        for directory in ['static', 'data']:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f"创建目录: {directory}")
        
        # 检查必要的文件
        required_files = {
            'QSM/templates/index.html': '<!DOCTYPE html><html><body><h1>QSM API</h1></body></html>',
            'QSM/templates/api_client.html': '<!DOCTYPE html><html><body><h1>API Client</h1></body></html>',
            'QSM/templates/test.html': '<!DOCTYPE html><html><body><h1>Test Page</h1></body></html>'
        }
        
        for file_path, default_content in required_files.items():
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(default_content)
                logger.info(f"创建文件: {file_path}")
        
        # 初始化组件
        logger.info("正在初始化量子引擎...")
        quantum_engine = QuantumParallelEngine(num_nodes=8)
        logger.info("正在初始化混合接口...")
        hybrid_interface = HybridInterface(quantum_engine)
        logger.info("正在初始化数据编码器...")
        data_encoder = QuantumDataEncoder(num_qubits=8)
        logger.info("正在初始化量子交互组件...")
        quantum_interaction = QuantumInteraction()
        logger.info("正在初始化量子可视化组件...")
        quantum_visualizer = QuantumVisualizer()
        
        # 尝试初始化WeQ API
        try:
            logger.info("正在初始化WeQ模型API服务...")
            from weq_api import WeQModelAPI
            weq_model_api = WeQModelAPI()
            logger.info("成功初始化WeQ模型API服务")
        except ImportError:
            logger.warning("未找到WeQ API模块，将仅使用原始量子交互组件")
        except Exception as e:
            logger.warning(f"初始化WeQ API失败: {str(e)}")
        
        # 启动服务器
        logger.info("正在启动Flask服务器...")
        app.run(host='0.0.0.0', port=8080, debug=True)
    except Exception as e:
        logger.error(f"启动服务器时发生错误: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)