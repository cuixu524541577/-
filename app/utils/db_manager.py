# -*- coding: utf-8 -*-
import sqlite3
from typing import List, Dict, Any
import os
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        # 获取当前文件所在目录的根目录路径
        self.root_dir = Path(__file__).parent.parent.parent
        self.initialize_db()
    
    def initialize_db(self):
        """初始化数据库"""
        try:
            # 确保数据库目录存在
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # 使用 Path 来构建正确的文件路径
            schema_path = self.root_dir / 'app' / 'database' / 'schema.sql'
            
            with open(schema_path, 'r', encoding='utf-8') as schema_file:
                schema = schema_file.read()
                
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript(schema)
                
            # 验证表结构
            self.check_tables()
            
        except Exception as e:
            print(f"[ERROR] 数据库初始化失败: {str(e)}")
            raise
            
    def check_tables(self):
        """检查数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 检查表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # 检查 folder_templates 表结构
            cursor.execute("PRAGMA table_info(folder_templates)")
            columns = [row[1] for row in cursor.fetchall()]
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行SQL查询"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            result = [dict(row) for row in cursor.fetchall()]
            return result 