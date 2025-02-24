import os
import json
import sys
import shutil

class ConfigManager:
    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.ensure_config_files()
    
    def _get_config_dir(self):
        """获取配置文件目录"""
        if getattr(sys, 'frozen', False):
            # 打包后的应用
            if sys.platform == 'win32':
                config_dir = os.path.join(os.getenv('APPDATA'), 'FlowStudio')
            elif sys.platform == 'darwin':
                config_dir = os.path.expanduser('~/Library/Application Support/FlowStudio')
            else:  # Linux
                config_dir = os.path.expanduser('~/.config/flowstudio')
        else:
            # 开发环境
            config_dir = 'config'
            
        return config_dir
    
    def ensure_config_files(self):
        """确保配置文件存在"""
        os.makedirs(self.config_dir, exist_ok=True)
        
        # 配置文件路径
        config_file = os.path.join(self.config_dir, 'config.json')
        workflow_file = os.path.join(self.config_dir, 'workflow_settings.json')
        
        # 如果是打包后首次运行，复制默认配置
        if getattr(sys, 'frozen', False):
            if not os.path.exists(config_file):
                default_config = {
                    "app": {
                        "title": "流影工坊",
                        "theme_mode": "dark",
                        "window_width": 1534,
                        "window_height": 1029
                    },
                    "database": {
                        "path": os.path.join(self.config_dir, "database", "app.db")
                    }
                }
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, ensure_ascii=False, indent=2)
    
    def load_config(self):
        """加载配置"""
        config_file = os.path.join(self.config_dir, 'config.json')
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_config(self, config):
        """保存配置"""
        config_file = os.path.join(self.config_dir, 'config.json')
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2) 