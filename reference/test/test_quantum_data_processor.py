"""
Test Quantum Data Processing System
测试量子数据处理系统
"""

import unittest
import threading
import time
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import numpy as np
import sys
import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
import statistics

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quantum_data_processor import (
    QuantumDataProcessor,
    QuantumDataBlock,
    QuantumDataConverter,
    QuantumCompressor,
    QuantumIndex,
    QuantumDataSync
)

class TestQuantumDataProcessor(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        self.processor = QuantumDataProcessor()
        self.processor.start()
        time.sleep(0.1)  # 给同步线程一些启动时间

    def tearDown(self):
        """测试后清理"""
        try:
            self.processor.stop()
            self.processor.clear()
            time.sleep(0.1)  # 给清理过程一些时间
        except Exception as e:
            print(f"Cleanup error: {e}")

    def test_data_conversion_and_chunking(self):
        """测试数据转换和分块处理"""
        # 测试小数据（不需要分块）
        small_data = "Test"
        small_state = self.processor.converter.convert_to_quantum(small_data)
        self.assertIsNotNone(small_state)
        self.assertLessEqual(small_state.num_qubits, self.processor.converter.max_qubits)

        # 测试大数据（需要分块）
        large_data = "A" * 100
        large_state = self.processor.converter.convert_to_quantum(large_data)
        self.assertIsNotNone(large_state)
        self.assertLessEqual(large_state.num_qubits, self.processor.converter.max_qubits)

        # 验证缓存
        cached_state = self.processor.converter.convert_to_quantum(large_data)
        self.assertEqual(id(large_state), id(cached_state))  # 应该返回相同的对象

    def test_compression_with_cache(self):
        """测试压缩功能和缓存"""
        # 创建测试数据
        test_data = "A" * 100
        quantum_state = self.processor.converter.convert_to_quantum(test_data)
        
        # 首次压缩
        start_time = time.time()
        compressed1 = self.processor.compressor.compress_state(quantum_state)
        first_compression_time = time.time() - start_time
        
        # 再次压缩（应该使用缓存）
        start_time = time.time()
        compressed2 = self.processor.compressor.compress_state(quantum_state)
        cached_compression_time = time.time() - start_time
        
        # 验证结果
        self.assertIsNotNone(compressed1)
        self.assertEqual(compressed1, compressed2)  # 结果应该相同
        self.assertLess(cached_compression_time, first_compression_time)  # 缓存应该更快

    def test_batch_processing(self):
        """测试批处理功能"""
        # 准备测试数据
        test_data = [f"Test{i}" for i in range(15)]  # 超过一个批次大小
        
        # 并行处理所有数据
        start_time = time.time()
        futures = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            for data in test_data:
                futures.append(executor.submit(self.processor.process_data, data))
            
            # 等待所有任务完成
            results = [f.result(timeout=10) for f in as_completed(futures, timeout=15)]
        
        processing_time = time.time() - start_time
        
        # 验证结果
        self.assertEqual(len(results), len(test_data))
        self.assertTrue(all(r is not None for r in results))
        
        # 验证批处理时间合理
        avg_time_per_item = processing_time / len(test_data)
        self.assertLess(avg_time_per_item, 1.0)  # 平均每项应小于1秒

    def test_concurrent_operations_stability(self):
        """测试并发操作的稳定性"""
        def process_with_retry(data, max_retries=3):
            for _ in range(max_retries):
                try:
                    result = self.processor.process_data(data)
                    if result is not None:
                        return result
                except Exception:
                    time.sleep(0.1)
            return None

        # 创建大量并发请求
        test_data = [f"Concurrent{i}" for i in range(20)]
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(process_with_retry, data) for data in test_data]
            results = [f.result(timeout=15) for f in as_completed(futures, timeout=20)]
        
        processing_time = time.time() - start_time
        
        # 验证结果
        successful_results = [r for r in results if r is not None]
        success_rate = len(successful_results) / len(test_data)
        
        self.assertGreaterEqual(success_rate, 0.8)  # 成功率应至少80%
        self.assertLess(processing_time, 30.0)  # 总处理时间应在合理范围内

    def test_system_stability_under_load(self):
        """测试系统在负载下的稳定性"""
        # 准备不同大小的数据
        test_cases = [
            "Small" * 1,      # 小数据
            "Medium" * 10,    # 中等数据
            "Large" * 100,    # 大数据
        ]
        
        results = []
        processing_times = []
        
        # 对每种大小的数据进行多次测试
        for test_data in test_cases:
            start_time = time.time()
            block = self.processor.process_data(test_data)
            processing_time = time.time() - start_time
            
            results.append(block is not None)
            processing_times.append(processing_time)
            
            # 给系统一些恢复时间
            time.sleep(0.1)
        
        # 验证结果
        self.assertTrue(all(results))  # 所有处理都应该成功
        
        # 验证处理时间随数据大小增加而增加，但增长应该是可控的
        self.assertLess(processing_times[0], processing_times[1])  # 小数据应该比中等数据快
        self.assertLess(processing_times[1], processing_times[2])  # 中等数据应该比大数据快
        self.assertLess(processing_times[2], 5.0)  # 即使是大数据也不应该太慢

    def test_error_recovery(self):
        """测试错误恢复机制"""
        # 测试无效数据
        invalid_data = None
        result = self.processor.process_data(invalid_data)
        self.assertIsNone(result)
        
        # 测试超大数据
        very_large_data = "X" * 10000
        result = self.processor.process_data(very_large_data)
        self.assertIsNotNone(result)  # 应该能够处理，即使数据很大
        
        # 测试快速连续请求
        results = []
        for i in range(5):
            result = self.processor.process_data(f"Quick{i}")
            results.append(result is not None)
            time.sleep(0.01)  # 非常短的间隔
        
        self.assertTrue(any(results))  # 至少有一些请求应该成功

    def test_cache_effectiveness(self):
        """测试缓存效果"""
        # 重复处理相同数据
        test_data = "CacheTest"
        
        # 第一次处理（未缓存）
        start_time = time.time()
        first_result = self.processor.process_data(test_data)
        first_time = time.time() - start_time
        
        # 等待一下确保异步处理完成
        time.sleep(0.1)
        
        # 第二次处理（应该使用缓存）
        start_time = time.time()
        second_result = self.processor.process_data(test_data)
        second_time = time.time() - start_time
        
        # 验证结果
        self.assertIsNotNone(first_result)
        self.assertIsNotNone(second_result)
        self.assertEqual(first_result.id, second_result.id)  # 应该得到相同的数据块
        self.assertLess(second_time, first_time)  # 缓存处理应该更快

if __name__ == '__main__':
    unittest.main() 

"""
"""
量子基因编码: QE-TES-3DB80249A0CA
纠缠状态: 活跃
纠缠对象: ['test/test_common.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
