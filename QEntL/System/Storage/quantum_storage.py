#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量子存储模块 - 量子态存储和检索
"""

import json
import hashlib
import os
from datetime import datetime

class QuantumStorage:
    """量子态存储系统"""

    def __init__(self, storage_path="/root/QSM/data/quantum_storage"):
        self.storage_path = storage_path
        self.index = {}
        os.makedirs(storage_path, exist_ok=True)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子存储初始化: {storage_path}")

    def store_quantum_state(self, state_id, state_data, metadata=None):
        """
        存储量子态
        """
        # 生成存储路径
        state_hash = hashlib.sha256(state_id.encode()).hexdigest()[:16]
        filename = f"quantum_state_{state_hash}.json"
        filepath = os.path.join(self.storage_path, filename)

        # 构建存储对象
        storage_object = {
            'state_id': state_id,
            'state_data': state_data,
            'metadata': metadata or {},
            'created': datetime.now().isoformat(),
            'hash': state_hash
        }

        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(storage_object, f, indent=2, ensure_ascii=False)

        # 更新索引
        self.index[state_id] = {
            'filepath': filepath,
            'hash': state_hash,
            'created': storage_object['created']
        }

        return {
            'state_id': state_id,
            'stored': True,
            'location': filepath,
            'hash': state_hash
        }

    def retrieve_quantum_state(self, state_id):
        """
        检索量子态
        """
        if state_id not in self.index:
            # 尝试通过哈希查找
            state_hash = hashlib.sha256(state_id.encode()).hexdigest()[:16]
            filename = f"quantum_state_{state_hash}.json"
            filepath = os.path.join(self.storage_path, filename)

            if not os.path.exists(filepath):
                return {'error': 'State not found', 'state_id': state_id}

        # 获取文件路径
        filepath = self.index.get(state_id, {}).get('filepath')
        if not filepath:
            state_hash = hashlib.sha256(state_id.encode()).hexdigest()[:16]
            filepath = os.path.join(self.storage_path, f"quantum_state_{state_hash}.json")

        if not os.path.exists(filepath):
            return {'error': 'State file not found', 'state_id': state_id}

        # 读取文件
        with open(filepath, 'r', encoding='utf-8') as f:
            storage_object = json.load(f)

        return {
            'state_id': state_id,
            'state_data': storage_object.get('state_data'),
            'metadata': storage_object.get('metadata'),
            'retrieved': datetime.now().isoformat()
        }

    def list_stored_states(self):
        """
        列出所有存储的量子态
        """
        states = []
        for filename in os.listdir(self.storage_path):
            if filename.startswith('quantum_state_') and filename.endswith('.json'):
                filepath = os.path.join(self.storage_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        states.append({
                            'state_id': data.get('state_id'),
                            'hash': data.get('hash'),
                            'created': data.get('created')
                        })
                except:
                    pass

        return {
            'total': len(states),
            'states': states
        }

    def delete_quantum_state(self, state_id):
        """
        删除量子态
        """
        if state_id not in self.index:
            return {'error': 'State not found', 'state_id': state_id}

        filepath = self.index[state_id]['filepath']

        if os.path.exists(filepath):
            os.remove(filepath)

        del self.index[state_id]

        return {
            'state_id': state_id,
            'deleted': True,
            'timestamp': datetime.now().isoformat()
        }

    def quantum_backup(self, backup_path):
        """
        量子态备份
        """
        import shutil

        # 创建备份目录
        os.makedirs(backup_path, exist_ok=True)

        # 复制所有文件
        backup_count = 0
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                src = os.path.join(self.storage_path, filename)
                dst = os.path.join(backup_path, filename)
                shutil.copy2(src, dst)
                backup_count += 1

        return {
            'backup_path': backup_path,
            'files_backed_up': backup_count,
            'timestamp': datetime.now().isoformat()
        }

    def get_storage_stats(self):
        """
        获取存储统计
        """
        total_size = 0
        file_count = 0

        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                filepath = os.path.join(self.storage_path, filename)
                total_size += os.path.getsize(filepath)
                file_count += 1

        return {
            'storage_path': self.storage_path,
            'total_files': file_count,
            'total_size_bytes': total_size,
            'total_size_kb': round(total_size / 1024, 2),
            'index_entries': len(self.index)
        }

def main():
    print("=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子存储模块测试")
    print("=" * 60)

    storage = QuantumStorage()

    # 存储量子态
    print("\n存储量子态:")
    state1 = storage.store_quantum_state(
        'bell_state_001',
        {'type': 'Bell', 'qubits': 2, 'state': [1, 0, 0, 1]},
        {'experiment': 'Bell test', 'fidelity': 0.99}
    )
    print(f"  状态ID: {state1['state_id']}")
    print(f"  哈希: {state1['hash']}")

    state2 = storage.store_quantum_state(
        'ghz_state_001',
        {'type': 'GHZ', 'qubits': 3, 'state': [1, 0, 0, 0, 0, 0, 0, 1]},
        {'experiment': 'GHZ test'}
    )
    print(f"  状态ID: {state2['state_id']}")

    # 检索量子态
    print("\n检索量子态:")
    retrieved = storage.retrieve_quantum_state('bell_state_001')
    print(f"  状态ID: {retrieved['state_id']}")
    print(f"  类型: {retrieved['state_data']['type']}")

    # 列出所有状态
    print("\n列出所有存储的量子态:")
    all_states = storage.list_stored_states()
    print(f"  总数: {all_states['total']}")
    for state in all_states['states']:
        print(f"  - {state['state_id']} ({state['created'][:10]})")

    # 存储统计
    print("\n存储统计:")
    stats = storage.get_storage_stats()
    print(f"  文件数: {stats['total_files']}")
    print(f"  总大小: {stats['total_size_kb']} KB")

    print("\n" + "=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
