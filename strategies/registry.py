"""
QNT 策略注册中心
支持策略发现和加载
"""
import importlib
import json
from typing import Dict, List, Any, Optional, Type
from dataclasses import dataclass, field


@dataclass
class StrategyMeta:
    """策略元数据"""
    name: str
    module: str
    class_name: str
    description: str
    params_schema: Dict[str, Any]
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)


class StrategyRegistry:
    """策略注册中心"""
    
    def __init__(self):
        self._strategies: Dict[str, StrategyMeta] = {}
        self._instances: Dict[str, Any] = {}
    
    def register(self, strategy: StrategyMeta):
        """注册策略"""
        self._strategies[strategy.name] = strategy
    
    def load(self, name: str, **params) -> Any:
        """加载策略实例"""
        if name not in self._strategies:
            raise ValueError(f"Strategy not found: {name}")
        
        meta = self._strategies[name]
        module = importlib.import_module(meta.module)
        cls = getattr(module, meta.class_name)
        
        instance = cls(**params)
        self._instances[name] = instance
        return instance
    
    def get_meta(self, name: str) -> Optional[StrategyMeta]:
        """获取策略元数据"""
        return self._strategies.get(name)
    
    def list_strategies(self) -> List[Dict[str, Any]]:
        """列出所有策略"""
        return [
            {
                'name': m.name,
                'module': m.module,
                'class': m.class_name,
                'description': m.description,
                'version': m.version,
                'tags': m.tags,
                'params': m.params_schema
            }
            for m in self._strategies.values()
        ]
    
    def get_instance(self, name: str) -> Optional[Any]:
        """获取策略实例"""
        return self._instances.get(name)
    
    def auto_register(self, search_path: str = 'strategies'):
        """自动发现并注册策略"""
        import os
        import pkgutil
        
        base_dir = os.path.dirname(os.path.dirname(__file__))
        search_dir = os.path.join(base_dir, search_path)
        
        if not os.path.exists(search_dir):
            return
        
        for finder, modname, ispkg in pkgutil.iter_modules([search_dir]):
            if modname.startswith('_'):
                continue
            try:
                module = importlib.import_module(f'{search_path}.{modname}')
                # 查找策略类
                for attr_name in dir(module):
                    if attr_name.endswith('Strategy') or attr_name.endswith('Agent'):
                        attr = getattr(module, attr_name)
                        if hasattr(attr, '_strategy_meta'):
                            self.register(attr._strategy_meta)
            except Exception:
                pass


# 全局注册中心
_registry = StrategyRegistry()


def get_registry() -> StrategyRegistry:
    """获取策略注册中心"""
    return _registry


def register_strategy(strategy: StrategyMeta):
    """注册策略装饰器"""
    def decorator(cls):
        _registry.register(strategy)
        # 给类添加元数据标记
        cls._strategy_meta = strategy
        return cls
    return decorator


def load_strategy(name: str, **params) -> Any:
    """加载策略快捷函数"""
    return _registry.load(name, **params)
