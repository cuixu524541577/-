import sqlite3
from typing import List, Dict, Optional
import os
from pathlib import Path

class CameraManager:
    def __init__(self, db_path: str):
        """初始化相机管理器
        :param db_path: 数据库文件的完整路径
        """
        self.db_path = db_path
        print(f"[DEBUG] 初始化相机管理器: {db_path}")
        
        try:
            # 确保数据库目录存在
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            # 读取 schema 文件
            schema_path = Path(__file__).parent.parent / 'database' / 'schema.sql'
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = f.read()
            
            # 初始化数据库
            with sqlite3.connect(db_path) as conn:
                conn.executescript(schema)
                
        except Exception as e:
            print(f"[ERROR] 数据库初始化失败: {str(e)}")
            raise RuntimeError(f"数据库初始化失败: {e}")

    def get_all_brands(self) -> List[Dict]:
        """获取所有品牌"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT id, name FROM camera_brands ORDER BY name")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[ERROR] 获取品牌列表失败: {str(e)}")
            raise

    def add_brand(self, name: str) -> int:
        """添加品牌"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO camera_brands (name) VALUES (?)",
                    (name.strip(),)
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError("品牌已存在")
        except Exception as e:
            print(f"[ERROR] 添加品牌失败: {str(e)}")
            raise

    def get_models_by_brand(self, brand_id: int) -> List[Dict]:
        """获取指定品牌的所有型号"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT m.id, m.name, b.name as brand_name
                    FROM camera_models m
                    JOIN camera_brands b ON m.brand_id = b.id
                    WHERE m.brand_id = ?
                    ORDER BY m.name
                """, (brand_id,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[ERROR] 获取型号列表失败: {str(e)}")
            raise

    def add_model(self, brand_id: int, name: str) -> int:
        """添加型号"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO camera_models (brand_id, name) VALUES (?, ?)",
                    (brand_id, name.strip())
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError("型号已存在")
        except Exception as e:
            print(f"[ERROR] 添加型号失败: {str(e)}")
            raise

    def update_model(self, model_id: int, name: str) -> bool:
        """更新型号"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE camera_models SET name = ? WHERE id = ?",
                    (name.strip(), model_id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            raise ValueError("型号已存在")
        except Exception as e:
            print(f"[ERROR] 更新型号失败: {str(e)}")
            raise

    def delete_model(self, model_id: int) -> bool:
        """删除型号"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM camera_models WHERE id = ?", (model_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"[ERROR] 删除型号失败: {str(e)}")
            raise

    def rename_brand(self, brand_id: int, new_name: str) -> bool:
        """重命名品牌"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE camera_brands SET name = ? WHERE id = ?",
                    (new_name.strip(), brand_id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            raise ValueError("品牌名称已存在")
        except Exception as e:
            print(f"[ERROR] 重命名品牌失败: {str(e)}")
            raise

    def delete_brand(self, brand_id: int) -> bool:
        """删除品牌及其所有型号"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # 首先删除该品牌的所有型号
                cursor.execute("DELETE FROM camera_models WHERE brand_id = ?", (brand_id,))
                # 然后删除品牌
                cursor.execute("DELETE FROM camera_brands WHERE id = ?", (brand_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"[ERROR] 删除品牌失败: {str(e)}")
            raise 