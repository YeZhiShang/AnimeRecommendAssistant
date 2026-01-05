"""
配置加载器
"""
import json
import os
import sys
from typing import Any, Dict
from pathlib import Path

class Config:
    """配置管理器"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """加载配置文件"""
        config_path = Path("config.json")
        
        if not config_path.exists():
            print(f"错误: 配置文件 {config_path} 不存在")
            sys.exit(1)
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 替换环境变量
            self.config = self._replace_env_vars(config_data)
            
        except json.JSONDecodeError as e:
            print(f"配置文件格式错误: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            sys.exit(1)
    
    def _replace_env_vars(self, config: Any) -> Any:
        """递归替换环境变量"""
        if isinstance(config, dict):
            return {k: self._replace_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._replace_env_vars(item) for item in config]
        elif isinstance(config, str) and config.startswith('${') and config.endswith('}'):
            env_var = config[2:-1]
            return os.getenv(env_var, '')
        else:
            return config
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        """设置配置值（运行时修改）"""
        keys = key_path.split('.')
        config_ref = self.config
        
        for i, key in enumerate(keys[:-1]):
            if key not in config_ref:
                config_ref[key] = {}
            config_ref = config_ref[key]
        
        config_ref[keys[-1]] = value

# 全局配置实例
config = Config()