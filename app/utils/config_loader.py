import json
import os

class ConfigLoader:
    @staticmethod
    def load_config():
        """加载配置文件"""
        config_path = os.path.join('config', 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f) 