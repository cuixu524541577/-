import sqlite3
from typing import List, Dict, Optional

class AssetSettingsManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        print(f"[DEBUG] 初始化数据库: {self.db_path}")
        with sqlite3.connect(self.db_path) as conn:
            # 启用外键约束
            conn.execute("PRAGMA foreign_keys = ON")
            
            cursor = conn.cursor()
            
            # 创建资产类型表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS asset_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE COLLATE NOCASE,  -- 不区分大小写
                    display_name TEXT NOT NULL COLLATE NOCASE
                )
            """)
            
            # 创建分类表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_type_id INTEGER NOT NULL,
                    name TEXT NOT NULL COLLATE NOCASE,
                    description TEXT COLLATE NOCASE,
                    sort_order INTEGER DEFAULT 0,
                    FOREIGN KEY (asset_type_id) REFERENCES asset_types (id),
                    UNIQUE (asset_type_id, name)
                )
            """)
            
            # 创建标签表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_type_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    sort_order INTEGER DEFAULT 0,
                    FOREIGN KEY (asset_type_id) REFERENCES asset_types (id),
                    UNIQUE (asset_type_id, name)
                )
            """)
            
            # 创建颜色标记表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS color_marks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_type_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    color TEXT NOT NULL,  -- 存储HEX颜色值
                    sort_order INTEGER DEFAULT 0,
                    FOREIGN KEY (asset_type_id) REFERENCES asset_types (id),
                    UNIQUE (asset_type_id, name)
                )
            """)
            
            # 创建评分设置表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rating_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_type_id INTEGER NOT NULL UNIQUE,
                    max_rating INTEGER NOT NULL DEFAULT 5,
                    allow_half_rating BOOLEAN NOT NULL DEFAULT 1,
                    FOREIGN KEY (asset_type_id) REFERENCES asset_types (id)
                )
            """)
            
            print("[DEBUG] 插入默认资产类型")
            cursor.executemany(
                "INSERT OR IGNORE INTO asset_types (name, display_name) VALUES (?, ?)",
                [
                    ("ae_template", "AE模板"),
                    ("video", "视频素材"),
                    ("audio", "音效素材"),
                    ("lut", "LUT"),
                ]
            )
            
            conn.commit()
    
    def get_asset_types(self) -> List[Dict]:
        """获取所有资产类型"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM asset_types ORDER BY id")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_categories(self, asset_type_id: int) -> List[Dict]:
        """获取指定资产类型的分类列表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM categories WHERE asset_type_id = ? ORDER BY sort_order, id",
                (asset_type_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def add_category(self, asset_type_id: int, name: str, description: str = "") -> int:
        """添加分类"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO categories (asset_type_id, name, description)
                VALUES (?, ?, ?)
                """,
                (asset_type_id, name, description)
            )
            return cursor.lastrowid
    
    def update_category(self, category_id: int, name: str, description: str = ""):
        """更新分类"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE categories 
                SET name = ?, description = ?
                WHERE id = ?
                """,
                (name, description, category_id)
            )
    
    def delete_category(self, category_id: int):
        """删除分类"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    
    # 标签相关方法
    def get_tags(self, asset_type_id: int) -> List[Dict]:
        """获取指定资产类型的标签列表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM tags WHERE asset_type_id = ? ORDER BY sort_order, id",
                (asset_type_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def add_tag(self, asset_type_id: int, name: str, description: str = "") -> int:
        """添加标签"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tags (asset_type_id, name, description) VALUES (?, ?, ?)",
                (asset_type_id, name, description)
            )
            return cursor.lastrowid
    
    # ... 其他标签相关方法 ...
    
    # 颜色标记相关方法
    def get_color_marks(self, asset_type_id: int) -> List[Dict]:
        """获取指定资产类型的颜色标记列表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM color_marks WHERE asset_type_id = ? ORDER BY sort_order, id",
                (asset_type_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    # ... 其他颜色标记相关方法 ...
    
    # 评分设置相关方法
    def get_rating_settings(self, asset_type_id: int) -> Optional[Dict]:
        """获取指定资产类型的评分设置"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM rating_settings WHERE asset_type_id = ?",
                (asset_type_id,)
            )
            result = cursor.fetchone()
            return dict(result) if result else None
    
    # ... 其他评分设置相关方法 ... 