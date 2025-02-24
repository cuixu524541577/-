import flet as ft
from app.utils.db_manager import DatabaseManager
from datetime import datetime, timedelta
import os
import json

class WorkflowView:
    def __init__(self, page: ft.Page, db: DatabaseManager):
        self.page = page
        self.db = db
        self.camera_rows = []  # 存储相机输入行
        
    def build(self):
        # 项目类型下拉框
        self.project_type = ft.Dropdown(
            label="项目类型",
            hint_text="请选择项目类型",
            options=[
                ft.dropdown.Option("简易项目"),
                ft.dropdown.Option("标准项目"),
                ft.dropdown.Option("大型项目"),
            ],
            width=200,
        )
        
        # 剪辑软件下拉框
        self.editing_software = ft.Dropdown(
            label="剪辑软件",
            hint_text="请选择剪辑软件",
            options=[
                ft.dropdown.Option("Premiere Pro"),
                ft.dropdown.Option("Davinci Resolve"),
                ft.dropdown.Option("Final Cut Pro"),
            ],
            width=200,
        )
        
        # 日期类型选择
        self.date_type = ft.Dropdown(
            label="日期选择",
            hint_text="请选择日期类型",
            options=[
                ft.dropdown.Option("当天日期"),
                ft.dropdown.Option("交付日期"),
            ],
            width=200,
            on_change=self.handle_date_selection
        )
        
        # 项目名称输入
        self.project_name = ft.TextField(
            label="项目名称",
            hint_text="请输入项目名称",
            width=400,
        )
        
        # 相机列表容器
        self.camera_container = ft.Column(
            controls=[],
            spacing=10,
        )
        
        # 添加第一个相机输入行
        self.add_camera_row()
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("工作流创建", size=32, weight=ft.FontWeight.BOLD),
                    ft.Row([self.project_type], alignment=ft.MainAxisAlignment.START),
                    ft.Row([self.editing_software], alignment=ft.MainAxisAlignment.START),
                    ft.Row([self.date_type], alignment=ft.MainAxisAlignment.START),
                    ft.Row([self.project_name], alignment=ft.MainAxisAlignment.START),
                    ft.Divider(),
                    ft.Text("相机设置", size=16, weight=ft.FontWeight.BOLD),
                    self.camera_container,
                    ft.ElevatedButton(
                        text="添加相机",
                        icon=ft.icons.ADD,
                        on_click=lambda _: self.add_camera_row()
                    ),
                    ft.Divider(),
                    ft.ElevatedButton(
                        text="创建工作流文件夹",
                        icon=ft.icons.CREATE_NEW_FOLDER,
                        on_click=self.create_workflow
                    ),
                ],
                spacing=20,
            ),
            padding=20,
        )
    
    def add_camera_row(self):
        """添加相机输入行"""
        camera_row = ft.Row(
            controls=[
                ft.TextField(
                    label="相机型号",
                    hint_text="请输入相机型号",
                    width=200,
                ),
                ft.TextField(
                    label="标识",
                    hint_text="可选",
                    width=100,
                ),
                ft.IconButton(
                    icon=ft.icons.DELETE,
                    on_click=lambda e, row=len(self.camera_rows): self.remove_camera_row(row)
                )
            ],
            alignment=ft.MainAxisAlignment.START,
        )
        self.camera_rows.append(camera_row)
        self.camera_container.controls.append(camera_row)
        self.page.update()
    
    def remove_camera_row(self, index):
        """删除相机输入行"""
        if len(self.camera_rows) > 1:  # 保持至少一行
            self.camera_container.controls.pop(index)
            self.camera_rows.pop(index)
            self.page.update()
    
    def handle_date_selection(self, e):
        """处理日期选择"""
        if e.data == "交付日期":
            self.show_date_dialog()
    
    def show_date_dialog(self):
        """显示日期选择对话框"""
        date_dialog = ft.AlertDialog(
            title=ft.Text("选择交付日期"),
            content=ft.Column(
                controls=[
                    ft.TextField(
                        label="天数",
                        hint_text="请输入天数",
                        keyboard_type=ft.KeyboardType.NUMBER,
                    ),
                    # 这里可以添加日期选择器
                ],
                spacing=10,
            ),
        )
        self.page.dialog = date_dialog
        date_dialog.open = True
        self.page.update()
    
    def create_workflow(self, e):
        """创建工作流文件夹"""
        try:
            # 加载设置
            with open('config/workflow_settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # 验证必要的设置和输入
            if not settings["project_path"]:
                self.show_error("请先在设置中配置工程路径")
                return
            
            if not self.project_name.value:
                self.show_error("请输入项目名称")
                return
            
            if not self.project_type.value:
                self.show_error("请选择项目类型")
                return
            
            # 获取日期
            if self.date_type.value == "当天日期":
                date_str = datetime.now().strftime("%Y%m%d")
            else:
                # TODO: 处理交付日期
                date_str = datetime.now().strftime("%Y%m%d")
            
            # 创建项目根目录
            project_folder = os.path.join(
                settings["project_path"],
                f"{date_str}_{self.project_name.value}"
            )
            os.makedirs(project_folder, exist_ok=True)
            
            # 获取文件夹结构
            structure_type = self.project_type.value
            if structure_type == "简易项目":
                structure = settings["folder_structures"]["simple"]
            elif structure_type == "标准项目":
                structure = settings["folder_structures"]["standard"]
            else:
                structure = settings["folder_structures"]["large"]
            
            # 创建文件夹结构
            language = settings["folder_language"]
            folder_names = settings["folder_names"][language]
            
            for folder in structure:
                folder_path = os.path.join(project_folder, folder_names[folder])
                os.makedirs(folder_path, exist_ok=True)
                
                # 如果是相机文件夹，创建相机子文件夹
                if folder == "01_Camera":
                    for row in self.camera_rows:
                        camera_model = row.controls[0].value
                        camera_tag = row.controls[1].value
                        if camera_model:
                            camera_folder = f"{date_str}_{camera_model}"
                            if camera_tag:
                                camera_folder += f"_{camera_tag}"
                            os.makedirs(os.path.join(folder_path, camera_folder), exist_ok=True)
            
            # 复制剪辑软件模板
            if self.editing_software.value and settings["editing_templates_path"]:
                software_path = os.path.join(
                    settings["editing_templates_path"],
                    self.editing_software.value
                )
                if os.path.exists(software_path):
                    project_folder = os.path.join(
                        project_folder,
                        folder_names["04_Project"]
                    )
                    # TODO: 实现文件夹复制功能
                    
            self.show_success("工作流文件夹创建成功！")
            
        except Exception as ex:
            self.show_error(f"创建失败：{str(ex)}")

    def show_error(self, message):
        """显示错误提示"""
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.colors.ERROR
            )
        )

    def show_success(self, message):
        """显示成功提示"""
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.colors.SUCCESS
            )
        ) 