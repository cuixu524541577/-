import sqlite3
from typing import List, Dict, Optional
from datetime import datetime
import os
import pandas as pd

class ProjectManager:
    def __init__(self, db_path: str):
        """初始化项目管理器"""
        self.db_path = db_path
        self.conn = None
        self._init_db()
    
    def __del__(self):
        """析构函数"""
        try:
            if self.conn:
                self.conn.close()
                print("[DEBUG] 数据库连接已关闭")
        except Exception as e:
            print(f"[ERROR] 关闭数据库连接失败: {str(e)}")
    
    def _init_db(self):
        """初始化数据库"""
        try:
            # 确保数据库目录存在
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # 读取 schema.sql
            schema_path = os.path.join(os.path.dirname(__file__), "..", "database", "schema.sql")
            with open(schema_path, "r", encoding="utf-8") as f:
                schema = f.read()
            
            # 执行 schema
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript(schema)
                print("[DEBUG] 数据库初始化成功")
                
        except Exception as e:
            print(f"[ERROR] 数据库初始化失败: {str(e)}")
            raise Exception(f"数据库初始化失败: {str(e)}")
    
    def get_projects(self, filters: Dict = None) -> List[Dict]:
        """获取项目列表"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = """
                    SELECT * FROM projects
                """
                
                where_clauses = []
                params = []
                
                if filters:
                    if filters.get("disk_id"):
                        where_clauses.append("disk_id = ?")
                        params.append(filters["disk_id"])
                    
                    if filters.get("backup_status") is not None:
                        where_clauses.append("backup_status = ?")
                        params.append(filters["backup_status"])
                    
                    if filters.get("date_from"):
                        where_clauses.append("project_date >= ?")
                        params.append(filters["date_from"])
                    
                    if filters.get("date_to"):
                        where_clauses.append("project_date <= ?")
                        params.append(filters["date_to"])
                    
                    if filters.get("search_text"):
                        search_term = f"%{filters['search_text']}%"
                        where_clauses.append("""(
                            project_name LIKE ? OR 
                            notes LIKE ? OR 
                            project_path LIKE ? OR
                            filename LIKE ?
                        )""")
                        params.extend([search_term] * 4)
                
                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)
                
                query += " ORDER BY disk_id ASC, project_date DESC"
                
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"[ERROR] 获取项目列表失败: {str(e)}")
            raise Exception(f"获取项目列表失败: {str(e)}")

    def add_project(self, project_data: dict) -> None:
        """添加新项目"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO projects (
                        disk_id, project_date, project_name,
                        backup_status, notes, project_path, filename
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    project_data['disk_id'],
                    project_data['project_date'],
                    project_data['project_name'],
                    project_data['backup_status'],
                    project_data['notes'],
                    project_data['project_path'],
                    project_data['filename']
                ))
                conn.commit()
        except Exception as e:
            print(f"[ERROR] 添加项目失败: {str(e)}")
            raise Exception(f"添加项目失败: {str(e)}")

    def update_project(self, project_id: int, project_data: dict) -> None:
        """更新项目"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE projects SET
                        disk_id = ?,
                        project_date = ?,
                        project_name = ?,
                        backup_status = ?,
                        notes = ?,
                        project_path = ?,
                        filename = ?
                    WHERE id = ?
                """, (
                    project_data['disk_id'],
                    project_data['project_date'],
                    project_data['project_name'],
                    project_data['backup_status'],
                    project_data['notes'],
                    project_data['project_path'],
                    project_data['filename'],
                    project_id
                ))
                conn.commit()
        except Exception as e:
            print(f"[ERROR] 更新项目失败: {str(e)}")
            raise Exception(f"更新项目失败: {str(e)}")

    def delete_project(self, project_id: int) -> None:
        """删除项目"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
                conn.commit()
                
        except Exception as e:
            print(f"[ERROR] 删除项目失败: {str(e)}")
            raise Exception(f"删除项目失败: {str(e)}")

    def get_disk_ids(self) -> List[str]:
        """获取所有磁盘编号"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT disk_id 
                    FROM projects 
                    ORDER BY disk_id
                """)
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"[ERROR] 获取磁盘编号列表失败: {str(e)}")
            return []

    def import_from_excel(self, file_path: str) -> None:
        """从Excel导入数据"""
        try:
            print(f"[DEBUG] 开始导入Excel: {file_path}")
            # 读取Excel时指定列名映射
            df = pd.read_excel(
                file_path,
                dtype={
                    '磁盘编号': str,
                    '项目时间': str,
                    '项目名称': str,
                    '备份': str,
                    '项目备注': str,
                    '路径': str,
                    '文件名称': str
                }
            )
            
            # 删除空行
            df = df.dropna(how='all')
            
            # 重命名列以匹配数据库字段
            df = df.rename(columns={
                '磁盘编号': 'disk_id',
                '项目时间': 'project_date',
                '项目名称': 'project_name',
                '备份': 'backup_status',
                '项目备注': 'notes',
                '路径': 'project_path',
                '文件名称': 'filename'
            })
            
            # 数据清理和验证
            def clean_data(row):
                # 处理磁盘编号
                row['disk_id'] = str(int(float(row['disk_id']))) if pd.notnull(row['disk_id']) else '0'
                
                # 处理项目时间
                if pd.isnull(row['project_date']) or row['project_date'] == 'NANO':
                    row['project_date'] = '未知'
                else:
                    row['project_date'] = str(row['project_date']).strip()
                
                # 处理项目名称
                if pd.isnull(row['project_name']):
                    row['project_name'] = '未命名项目'
                else:
                    row['project_name'] = str(row['project_name']).strip()
                
                # 处理备份状态
                row['backup_status'] = 1 if str(row['backup_status']).strip() in ['是', '1', 'True', 'true'] else 0
                
                # 处理备注
                row['notes'] = str(row['notes']).strip() if pd.notnull(row['notes']) else ''
                
                # 处理路径
                row['project_path'] = str(row['project_path']).strip() if pd.notnull(row['project_path']) else ''
                if row['project_path'] == 'NANO':
                    row['project_path'] = ''
                
                # 处理文件名
                row['filename'] = str(row['filename']).strip() if pd.notnull(row['filename']) else ''
                if row['filename'] == 'NANO':
                    row['filename'] = ''
                    
                return row
            
            # 应用数据清理
            df = df.apply(clean_data, axis=1)
            
            print(f"[DEBUG] 处理后的数据预览:\n{df.head()}")
            
            # 批量插入数据
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for _, row in df.iterrows():
                    try:
                        print(f"[DEBUG] 正在处理行: {dict(row)}")
                        cursor.execute("""
                            INSERT INTO projects (
                                disk_id, project_date, project_name,
                                backup_status, notes, project_path, filename
                            ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            row['disk_id'],
                            row['project_date'],
                            row['project_name'],
                            row['backup_status'],
                            row['notes'],
                            row['project_path'],
                            row['filename']
                        ))
                    except Exception as e:
                        print(f"[WARNING] 跳过无效行: {str(e)}, 数据: {dict(row)}")
                        continue
                        
                conn.commit()
                print(f"[DEBUG] 导入完成，共处理 {len(df)} 条记录")
                
        except Exception as e:
            print(f"[ERROR] 导入Excel失败: {str(e)}")
            raise Exception(f"导入Excel失败: {str(e)}")

    def export_to_excel(self, file_path: str) -> None:
        """导出数据到Excel"""
        try:
            print(f"[DEBUG] 开始导出Excel: {file_path}")
            projects = self.get_projects()
            print(f"[DEBUG] 获取到 {len(projects)} 条记录")
            
            df = pd.DataFrame(projects)
            
            # 重命名列为中文
            df = df.rename(columns={
                'disk_id': '磁盘编号',
                'project_date': '项目时间',
                'project_name': '项目名称',
                'backup_status': '备份',
                'notes': '项目备注',
                'project_path': '路径',
                'filename': '文件名称'
            })
            
            # 处理备份状态显示
            df['备份'] = df['备份'].apply(lambda x: '是' if x == 1 else '否')
            
            print(f"[DEBUG] DataFrame预览:\n{df.head()}")
            df.to_excel(file_path, index=False)
            print("[DEBUG] 导出完成")
            
        except Exception as e:
            print(f"[ERROR] 导出Excel失败: {str(e)}")
            raise Exception(f"导出Excel失败: {str(e)}")

    def _get_connection(self):
        """获取数据库连接"""
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn