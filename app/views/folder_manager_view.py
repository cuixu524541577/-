# -*- coding: utf-8 -*-
import flet as ft
import sqlite3
import os
import uuid
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from app.utils.template_manager import TemplateManager, TemplateNode
from app.views.base_view import BaseView

@dataclass
class TemplateNode:
    """模板节点数据结构"""
    id: int  # 改为 INTEGER 类型
    name: str
    type: str  # 'folder' or 'virtual'
    parent_id: Optional[int]  # 改为 INTEGER 类型
    naming_rule: Optional[str]
    meta: Dict
    children: List['TemplateNode'] = None

class FolderManager:
    """文件夹管理器 - 数据操作类"""
    def __init__(self, db_path: str):
        self.db_path = os.path.join(db_path, "app.db")
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 读取并执行schema.sql文件
            schema_path = Path(__file__).parent.parent / 'database' / 'schema.sql'
            with open(schema_path, 'r', encoding='utf-8') as f:
                cursor.executescript(f.read())
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] 数据库初始化失败: {str(e)}")
            raise

    def _handle_db_error(self, e: Exception, operation: str) -> bool:
        """统一处理数据库错误"""
        if isinstance(e, sqlite3.IntegrityError):
            if "UNIQUE constraint failed" in str(e):
                print(f"[ERROR] {operation} - 同名文件夹已存在")
                return False
        print(f"[ERROR] {operation}失败: {str(e)}")
        return False

    def _get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    def _execute(self, sql: str, params: tuple = None, fetch: bool = False):
        """执行SQL语句"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
                
            result = None
            if fetch:
                result = cursor.fetchall()
                
            conn.commit()
            conn.close()
            return result
            
        except Exception as e:
            print(f"[ERROR] SQL执行失败: {str(e)}")
            raise

    def get_project_type_id(self, project_type: str) -> int:
        """获取项目类型ID"""
        result = self._execute(
            "SELECT id FROM project_types WHERE name = ?",
            (project_type,),
            fetch=True
        )
        return result[0][0] if result else None

    def get_folders(self, project_type: str) -> List[dict]:
        """获取文件夹列表"""
        try:
            type_id = self.get_project_type_id(project_type)
            if not type_id:
                return []
                
            folders = self._execute("""
                SELECT id, parent_id, name, description, sort_order
                FROM folder_templates
                WHERE project_type_id = ?
                ORDER BY sort_order, name
            """, (type_id,), fetch=True)
            
            return [
                {
                    'id': row[0],
                    'parent_id': row[1],
                    'name': row[2],
                    'description': row[3],
                    'sort_order': row[4],
                    'children': []  # 用于构建树形结构
                }
                for row in folders
            ]
            
        except Exception as e:
            print(f"[ERROR] 获取文件夹失败: {str(e)}")
            return []

    def build_folder_tree(self, folders: List[dict]) -> List[dict]:
        """构建文件夹树形结构"""
        folder_map = {folder['id']: folder for folder in folders}
        root_folders = []
        
        for folder in folders:
            if folder['parent_id'] is None:
                root_folders.append(folder)
            else:
                parent = folder_map.get(folder['parent_id'])
                if parent:
                    parent['children'].append(folder)
                    
        return root_folders

    def create_folder(self, project_type: str, name: str, parent_id: int = None) -> bool:
        """创建文件夹"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取项目类型ID
            cursor.execute(
                "SELECT id FROM project_types WHERE name = ?",
                (project_type,)
            )
            type_id = cursor.fetchone()[0]
            
            # 检查同级目录下是否存在同名文件夹
            cursor.execute("""
                SELECT COUNT(*) FROM folder_templates 
                WHERE project_type_id = ? AND parent_id IS ? AND name = ?
            """, (type_id, parent_id, name))
            
            if cursor.fetchone()[0] > 0:
                raise ValueError("同名文件夹已存在")
            
            # 获取排序顺序
            cursor.execute("""
                SELECT COALESCE(MAX(sort_order), 0) + 1
                FROM folder_templates 
                WHERE project_type_id = ? AND parent_id IS ?
            """, (type_id, parent_id))
            
            sort_order = cursor.fetchone()[0]
            
            # 创建文件夹记录
            cursor.execute("""
                INSERT INTO folder_templates (project_type_id, parent_id, name, sort_order)
                VALUES (?, ?, ?, ?)
            """, (type_id, parent_id, name, sort_order))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"[ERROR] 创建文件夹失败: {str(e)}")
            return False

    def rename_folder(self, folder_id: int, new_name: str) -> bool:
        """重命名文件夹"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查同级目录下是否存在同名文件夹
            cursor.execute("""
                SELECT parent_id, project_type_id 
                FROM folder_templates 
                WHERE id = ?
            """, (folder_id,))
            parent_id, type_id = cursor.fetchone()
            
            cursor.execute("""
                SELECT COUNT(*) FROM folder_templates 
                WHERE project_type_id = ? AND parent_id IS ? AND name = ? AND id != ?
            """, (type_id, parent_id, new_name, folder_id))
            
            if cursor.fetchone()[0] > 0:
                raise ValueError("同名文件夹已存在")
            
            # 更新文件夹名称
            cursor.execute("""
                UPDATE folder_templates 
                SET name = ? 
                WHERE id = ?
            """, (new_name, folder_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"[ERROR] 重命名文件夹失败: {str(e)}")
            return False

    def delete_folder(self, folder_id: int) -> bool:
        """删除文件夹及其子文件夹"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            def delete_recursive(fid):
                # 递归删除子文件夹
                cursor.execute(
                    "SELECT id FROM folder_templates WHERE parent_id = ?",
                    (fid,)
                )
                for (child_id,) in cursor.fetchall():
                    delete_recursive(child_id)
                    
                # 删除当前文件夹
                cursor.execute(
                    "DELETE FROM folder_templates WHERE id = ?",
                    (fid,)
                )
            
            delete_recursive(folder_id)
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"[ERROR] 删除文件夹失败: {str(e)}")
            return False

class FolderManagerView(BaseView):
    def __init__(self, page: ft.Page, settings: dict):
        super().__init__(page)
        self.settings = settings
        self.folder_lists = {}  # 存储不同类型的列表控件
        self.operation_forms = {}  # 存储不同类型的表单容器
        self.current_type = 'simple'  # 当前选中的类型
        self.loading = False
        
        try:
            # 从 settings 中获取数据库路径
            db_dir = settings.get("database_path", "")
            if not db_dir:
                raise ValueError("数据库路径未设置，请先在路径设置中配置")
                
            # 构建数据库文件完整路径
            db_path = os.path.join(db_dir, "app.db")
            
            # 初始化模板管理器
            self.manager = TemplateManager(db_path)
            
            # 初始化 tabs
            self.tabs = ft.Tabs(
                selected_index=0,
                animation_duration=300,
                animate_size=True,
                on_change=self.handle_tab_change,
                tabs=[
                    ft.Tab(
                        text="简易项目",
                        content=self._build_folder_section('simple'),
                    ),
                    ft.Tab(
                        text="大型项目",
                        content=self._build_folder_section('complex'),
                    ),
                ],
            )
            
            # 初始刷新
            self.refresh_folders()
            
        except Exception as e:
            print(f"[ERROR] 初始化失败: {str(e)}")
            self.show_error(str(e))
            # 创建一个空的 tabs 作为后备
            self.tabs = ft.Tabs(
                tabs=[
                    ft.Tab(text="简易项目", content=ft.Container()),
                    ft.Tab(text="大型项目", content=ft.Container()),
                ]
            )

    def build(self):
        """构建界面"""
        return ft.Container(
            content=ft.Column([
                # 顶部栏
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            on_click=lambda _: self.page.go("/settings"),
                            tooltip="返回设置",
                        ),
                        ft.Text("编辑文件夹结构", size=20, weight=ft.FontWeight.BOLD),
                        # 添加一个空的扩展容器来占据剩余空间
                        ft.Container(expand=True),
                    ], 
                    alignment=ft.MainAxisAlignment.START),  # 改为左对齐
                    padding=10,
                ),
                # 内容区域
                ft.Container(
                    content=self.tabs,
                    expand=True,
                ),
            ]),
            expand=True,
        )

    def _build_folder_section(self, project_type: str):
        """构建文件夹区域"""
        
        # 创建列表控件
        folder_list = ft.ListView(
            expand=True,
            spacing=10,  # 增加文件夹之间的间距，从2改为10
            padding=10,
        )
        self.folder_lists[project_type] = folder_list

        # 创建操作表单容器
        operation_form = ft.Container(
            visible=False,
            content=None,
            padding=20,
            margin=ft.margin.all(10),  # 添加外边距，与边框保持距离
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=8,
        )
        # 存储表单容器引用
        self.operation_forms[project_type] = operation_form

        return ft.Container(
            # 最外层容器，expand=True表示填充所有可用空间
            content=ft.Column([
                # Column用于垂直排列子组件
                # 工具栏区域
                ft.Container(
                    content=ft.Row([
                        # Row用于水平排列子组件
                        ft.FilledButton(
                            "新建文件夹",
                            icon=ft.icons.CREATE_NEW_FOLDER,  # 按钮左侧图标
                            on_click=lambda _: self._show_create_form(project_type)
                        ),
                        ft.IconButton(
                            icon=ft.icons.REFRESH,
                            tooltip="刷新",  # 鼠标悬停时显示的提示文本
                            on_click=lambda _: self.refresh_folders()
                        ),
                    ], spacing=10),  # Row子组件之间的间距为10像素
                    padding=10,  # Container四周填充10像素的内边距
                ),
                ft.Divider(height=1),  # 分割线，高度为1像素
                operation_form,  # 当前类型的操作表单
                folder_list,     # 文件夹列表组件
            ]),
            expand=True,  # Container扩展填充父组件的所有可用空间
            margin=ft.margin.only(top=10),  # Container顶部填充20像素的间距
        )

    def _show_create_form(self, project_type: str, parent_id: int = None):
        """显示创建文件夹表单"""
        form = self.operation_forms.get(project_type)
        if not form:
            return

        name_field = ft.TextField(
            label="文件夹名称",
            width=300,
        )

        def handle_submit(e):
            name = name_field.value.strip()
            if name:
                try:
                    new_id = self.manager.create_node(project_type, name, parent_id)
                    if new_id:
                        self._hide_form(project_type)
                        self.refresh_folders()
                        self.show_success(f"已创建{'子' if parent_id else ''}文件夹 '{name}'")
                    else:
                        self.show_error("创建失败")
                except Exception as ex:
                    print(f"[ERROR] 创建失败: {str(ex)}")
                    self.show_error(str(ex))

        form.content = ft.Column([
            ft.Text("新建" + ("子" if parent_id else "") + "文件夹", size=16),
            name_field,
            ft.Row([
                ft.TextButton("取消", on_click=lambda _: self._hide_form(project_type)),
                ft.FilledButton("创建", on_click=handle_submit),
            ], alignment=ft.MainAxisAlignment.END),
        ], tight=True)
        
        form.visible = True
        self.page.update()
        name_field.focus()

    def _show_rename_form(self, project_type: str, node: TemplateNode):
        """显示重命名表单"""
        form = self.operation_forms.get(project_type)
        if not form:
            return

        name_field = ft.TextField(
            label="新名称",
            value=node.name,
            width=300,
        )

        def handle_submit(e):
            new_name = name_field.value.strip()
            if new_name and new_name != node.name:
                try:
                    if self.manager.rename_node(node.id, new_name):
                        self._hide_form(project_type)
                        self.refresh_folders()
                        self.show_success(f"已重命名为 '{new_name}'")
                    else:
                        self.show_error("重命名失败")
                except Exception as ex:
                    print(f"[ERROR] 重命名失败: {str(ex)}")
                    self.show_error(str(ex))

        form.content = ft.Column([
            ft.Text("重命名文件夹", size=16),
            name_field,
            ft.Row([
                ft.TextButton("取消", on_click=lambda _: self._hide_form(project_type)),
                ft.FilledButton("确定", on_click=handle_submit),
            ], alignment=ft.MainAxisAlignment.END),
        ], tight=True)
        
        form.visible = True
        self.page.update()
        name_field.focus()

    def _show_delete_form(self, project_type: str, node: TemplateNode):
        """显示删除确认表单"""
        form = self.operation_forms.get(project_type)
        if not form:
            return

        def handle_submit(e):
            try:
                if self.manager.delete_node(node.id):
                    self._hide_form(project_type)
                    self.refresh_folders()
                    self.show_success(f"已删除 '{node.name}'")
                else:
                    self.show_error("删除失败")
            except Exception as ex:
                print(f"[ERROR] 删除失败: {str(ex)}")
                self.show_error(str(ex))

        form.content = ft.Column([
            ft.Text("确认删除", size=16, color=ft.colors.ERROR),
            ft.Text(f"是否删除文件夹 '{node.name}'？"),
            ft.Row([
                ft.TextButton("取消", on_click=lambda _: self._hide_form(project_type)),
                ft.FilledButton(
                    "删除",
                    on_click=handle_submit,
                    style=ft.ButtonStyle(
                        color=ft.colors.ON_ERROR,
                        bgcolor=ft.colors.ERROR,
                    ),
                ),
            ], alignment=ft.MainAxisAlignment.END),
        ], tight=True)
        
        form.visible = True
        self.page.update()

    def _hide_form(self, project_type: str):
        """隐藏表单"""
        form = self.operation_forms.get(project_type)
        if form:
            form.visible = False
            self.page.update()

    def _build_folder_item(self, node: TemplateNode, level: int = 0):
        """构建文件夹项目"""
        try:
            return ft.Container(
                content=ft.ListTile(
                    leading=ft.Icon(
                        name=ft.icons.FOLDER,
                        color=ft.colors.BLUE,
                    ),
                    title=ft.Text(
                        value=node.name,
                        size=16,
                    ),
                    trailing=ft.PopupMenuButton(
                        icon=ft.icons.MORE_VERT,
                        items=[
                            ft.PopupMenuItem(
                                text="新建子文件夹",
                                icon=ft.icons.CREATE_NEW_FOLDER,
                                on_click=lambda e: self._show_create_form(self.current_type, node.id)
                            ),
                            ft.PopupMenuItem(
                                text="重命名",
                                icon=ft.icons.DRIVE_FILE_RENAME_OUTLINE,
                                on_click=lambda e: self._show_rename_form(self.current_type, node)
                            ),
                            ft.PopupMenuItem(
                                text="删除",
                                icon=ft.icons.DELETE_FOREVER,
                                on_click=lambda e: self._show_delete_form(self.current_type, node)
                            ),
                        ]
                    ),
                ),
                margin=ft.margin.only(left=level * 20),
                bgcolor=ft.colors.SURFACE_VARIANT,
                border_radius=8,
                padding=5,
            )
        except Exception as e:
            print(f"[ERROR] 构建文件夹项目失败: {str(e)}")
            return ft.Container(
                content=ft.Text(f"加载失败: {node.name}"),
                padding=10,
                bgcolor=ft.colors.RED_100,
            )

    def refresh_folders(self):
        """刷新文件夹列表"""
        try:
            # 获取文件夹树
            nodes = self.manager.get_template_tree(self.current_type)
            
            # 获取列表控件
            folder_list = self.folder_lists.get(self.current_type)
            if not folder_list:
                print(f"[ERROR] 找不到列表控件: type={self.current_type}")
                return
            
            # 清空列表
            folder_list.controls.clear()
            
            # 递归添加节点
            def add_node_recursive(node: TemplateNode, level: int = 0):
                try:
                    item = self._build_folder_item(node, level)
                    if item:
                        folder_list.controls.append(item)
                        
                    # 递归添加子节点
                    if node.children:
                        for child in node.children:
                            add_node_recursive(child, level + 1)
                            
                except Exception as e:
                    print(f"[ERROR] 添加节点失败: id={node.id}, error={str(e)}")
            
            # 添加所有根节点及其子节点
            for node in nodes:
                add_node_recursive(node)
            
            # 更新显示
            folder_list.visible = True
            self.page.update()
            
        except Exception as e:
            print(f"[ERROR] 刷新失败: {str(e)}")
            self.show_error(f"刷新失败: {str(e)}")

    def handle_tab_change(self, e):
        """处理标签页切换"""
        self.current_type = 'simple' if e.control.selected_index == 0 else 'complex'
        self.refresh_folders()

    def show_error(self, message: str):
        """显示错误提示"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.colors.ERROR,
        )
        self.page.snack_bar.open = True
        self.page.update()

    def show_success(self, message: str):
        """显示成功提示"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.colors.GREEN,
        )
        self.page.snack_bar.open = True
        self.page.update()

    def _build_empty_view(self):
        """构建空状态视图"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(
                    name=ft.icons.FOLDER_OFF,
                    size=64,
                    color=ft.colors.GREY_400,
                ),
                ft.Text(
                    "暂无文件夹模板",
                    size=16,
                    color=ft.colors.GREY_400,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )

