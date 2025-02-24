import sqlite3
from typing import List, Optional
from dataclasses import dataclass
import os
from pathlib import Path

@dataclass
class TemplateNode:
    """模板节点数据类"""
    id: int
    name: str
    type: str
    parent_id: Optional[int]
    naming_rule: Optional[str]
    meta: dict
    children: List['TemplateNode'] = None

class TemplateManager:
    """模板管理器 - 核心业务逻辑"""
    def __init__(self, db_path: str):
        """
        初始化模板管理器
        :param db_path: 数据库文件的完整路径（不是目录）
        """
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """初始化数据库"""
        try:
            # 确保数据库目录存在
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # 读取 schema 文件
            schema_path = Path(__file__).parent.parent / 'database' / 'schema.sql'
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = f.read()
            
            # 初始化数据库
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript(schema)
                
        except Exception as e:
            raise RuntimeError(f"数据库初始化失败: {e}")

    def get_template_tree(self, project_type: str) -> List[TemplateNode]:
        """获取完整的模板树结构"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # 获取所有节点
                cursor.execute("""
                    SELECT 
                        f.id,
                        f.name,
                        f.parent_id,
                        f.sort_order
                    FROM folder_templates f
                    INNER JOIN project_types pt ON f.project_type_id = pt.id
                    WHERE pt.name = ?
                    ORDER BY f.parent_id NULLS FIRST, f.sort_order, f.name
                """, (project_type,))
                
                rows = cursor.fetchall()
                
                # 构建节点字典
                nodes_dict = {}
                root_nodes = []
                
                # 第一遍：创建所有节点
                for row in rows:
                    node = TemplateNode(
                        id=row['id'],
                        name=row['name'],
                        type='folder',
                        parent_id=row['parent_id'],
                        naming_rule=None,
                        meta={},
                        children=[]
                    )
                    nodes_dict[node.id] = node
                
                # 第二遍：构建树结构
                for node in nodes_dict.values():
                    if node.parent_id is None:
                        root_nodes.append(node)
                    else:
                        parent = nodes_dict.get(node.parent_id)
                        if parent:
                            parent.children.append(node)
                
                return root_nodes
                
        except Exception as e:
            print(f"[ERROR] 获取模板树失败: {str(e)}")
            raise

    def create_node(self, project_type: str, name: str, parent_id: Optional[int] = None) -> int:
        """创建新节点"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 获取项目类型ID
                cursor.execute(
                    "SELECT id FROM project_types WHERE name = ?",
                    (project_type,)
                )
                result = cursor.fetchone()
                if not result:
                    raise ValueError(f"项目类型不存在: {project_type}")
                    
                type_id = result[0]
                
                # 检查父节点是否存在
                if parent_id:
                    cursor.execute("SELECT id FROM folder_templates WHERE id = ?", (parent_id,))
                    if not cursor.fetchone():
                        raise ValueError(f"父节点不存在: {parent_id}")
                
                # 获取排序顺序
                cursor.execute("""
                    SELECT COALESCE(MAX(sort_order), 0) + 1
                    FROM folder_templates 
                    WHERE project_type_id = ? AND parent_id IS ?
                """, (type_id, parent_id))
                
                sort_order = cursor.fetchone()[0]
                
                # 插入新节点
                cursor.execute("""
                    INSERT INTO folder_templates (
                        project_type_id, 
                        parent_id, 
                        name,
                        sort_order
                    ) VALUES (?, ?, ?, ?)
                """, (type_id, parent_id, name, sort_order))
                
                new_id = cursor.lastrowid
                return new_id
                
        except Exception as e:
            print(f"[ERROR] 创建节点失败: {str(e)}")
            raise

    def rename_node(self, node_id: int, new_name: str) -> bool:
        """重命名节点"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE folder_templates 
                    SET name = ? 
                    WHERE id = ?
                """, (new_name, node_id))
                conn.commit()
                return cursor.rowcount > 0
                
        except sqlite3.IntegrityError:
            # 唯一约束违反，说明同名文件夹已存在
            raise ValueError("同名文件夹已存在")
        except Exception as e:
            print(f"[ERROR] 重命名失败: {str(e)}")
            raise RuntimeError(f"重命名失败: {str(e)}")

    def delete_node(self, node_id: int) -> bool:
        """删除节点及其所有子节点"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 使用递归CTE删除节点及其所有子节点
                cursor.execute("""
                    WITH RECURSIVE descendants AS (
                        -- 起始节点
                        SELECT id FROM folder_templates WHERE id = ?
                        UNION ALL
                        -- 递归查找子节点
                        SELECT f.id 
                        FROM folder_templates f
                        INNER JOIN descendants d ON f.parent_id = d.id
                    )
                    DELETE FROM folder_templates 
                    WHERE id IN descendants
                """, (node_id,))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"[ERROR] 删除失败: {str(e)}")
            raise RuntimeError(f"删除失败: {e}") 