import flet as ft
from app.utils.db_manager import DatabaseManager
import json
import os
import shutil
from datetime import datetime
from app.utils.config_manager import ConfigManager

class SettingsView:
    def __init__(self, page: ft.Page, db: DatabaseManager):
        self.page = page
        self.db = db
        self.config_manager = ConfigManager()
        self.load_settings()
        
    def load_settings(self):
        """加载设置"""
        try:
            # 先加载 config.json
            with open('config/config.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            # 再加载 workflow_settings.json
            with open('config/workflow_settings.json', 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
            
        except FileNotFoundError:
            # 默认设置
            self.config = {
                "app": {
                    "title": "流影工坊",
                    "theme_mode": "light",
                    "window_width": 1534,
                    "window_height": 1029
                }
            }
            
            self.settings = {
                "project_path": "",
                "editing_templates_path": "",
                "folder_language": "english",  # english/chinese
                "folder_structures": {
                    "standard": [
                        "01_Camera",
                        "02_File",
                        "03_Proxy",
                        "04_Project",
                        "05_Audio",
                        "06_VFX",
                        "07_SFX",
                        "08_IMG",
                        "09_Script",
                        "10_Export",
                        "11_Handover"
                    ],
                    "large": [
                        # 可自定义大型项目结构
                    ]
                },
                "folder_names": {
                    "english": {
                        "01_Camera": "01_Camera",
                        "02_File": "02_File",
                        "03_Proxy": "03_Proxy",
                        "04_Project": "04_Project",
                        "05_Audio": "05_Audio",
                        "06_VFX": "06_VFX",
                        "07_SFX": "07_SFX",
                        "08_IMG": "08_IMG",
                        "09_Script": "09_Script",
                        "10_Export": "10_Export",
                        "11_Handover": "11_Handover"
                    },
                    "chinese": {
                        "01_Camera": "01_相机",
                        "02_File": "02_文件",
                        "03_Proxy": "03_代理",
                        "04_Project": "04_工程",
                        "05_Audio": "05_音频",
                        "06_VFX": "06_VFX",
                        "07_SFX": "07_音效",
                        "08_IMG": "08_图片",
                        "09_Script": "09_脚本",
                        "10_Export": "10_输出",
                        "11_Handover": "11_交接"
                    }
                }
            }
            self.save_settings()
            
            # 保存默认配置
            with open('config/config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def save_settings(self):
        """保存设置"""
        with open('config/workflow_settings.json', 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)
    
    def build(self):
        def on_theme_change(e):
            """主题切换处理函数"""
            try:
                new_theme = e.control.value
                old_theme = self.config["app"]["theme_mode"]
                
                if new_theme and new_theme != old_theme:
                    # 更新配置
                    self.config["app"]["theme_mode"] = new_theme
                    self.config_manager.save_config(self.config)
                    
                    # 直接重启应用
                    self.page.window_destroy()
            except Exception as ex:
                self.show_error(f"主题切换失败：{str(ex)}")
        
        # 创建主题下拉菜单
        theme_dropdown = ft.Dropdown(
            value=self.config["app"]["theme_mode"],
            width=150,
            options=[
                ft.dropdown.Option("light", "白色主题"),
                ft.dropdown.Option("dark", "黑色主题"),
            ],
            on_change=on_theme_change
        )
        
        return ft.Container(
            content=ft.Column([
                # 顶部标题
                ft.Row([
                    ft.Text("设置", size=32, weight=ft.FontWeight.BOLD),
                    ft.IconButton(
                        icon=ft.icons.HELP_OUTLINE,
                        tooltip="查看帮助",
                        on_click=lambda _: self.show_help()
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                # 样式设置区
                ft.Container(
                    content=ft.Column([
                        ft.Text("样式设置", size=20, weight=ft.FontWeight.W_500),
                        ft.Row([
                            ft.Text("主题设置（重启生效）："),
                            theme_dropdown,
                        ]),
                        ft.Row([
                            ft.Text("文件夹语言（目录语言）："),
                            ft.Dropdown(
                                value=self.settings["folder_language"],
                                width=150,
                                options=[
                                    ft.dropdown.Option("english", "English"),
                                    ft.dropdown.Option("chinese", "中文"),
                                ],
                                on_change=self.change_language
                            ),
                        ]),
                    ]),
                    bgcolor=ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE),
                    padding=20,
                    border_radius=10,
                ),
                
                # 路径设置区
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.ListTile(
                                leading=ft.Icon(ft.icons.FOLDER_OPEN),
                                title=ft.Text("路径设置", size=20, weight=ft.FontWeight.BOLD),
                                subtitle=ft.Text("设置各类文件的存储路径"),
                                on_click=lambda _: self.page.go("/path-settings")
                            ),
                        ]),
                        bgcolor=ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE),
                        padding=20,
                        border_radius=10,
                    ),
                ),
                
                # 工作流设置区
                ft.Container(
                    content=ft.Column([
                        ft.Text("工作流设置", size=20, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.ElevatedButton(
                                "编辑文件夹结构",
                                icon=ft.icons.FOLDER,
                                on_click=lambda _: self.page.go("/folder-manager")
                            ),
                            ft.ElevatedButton(
                                "管理相机型号",
                                icon=ft.icons.CAMERA_ALT,
                                on_click=lambda _: self.page.go("/camera-manager")
                            ),
                            ft.ElevatedButton(
                                "分类标签设置",
                                icon=ft.icons.SETTINGS,
                                on_click=lambda _: self.page.go("/asset-settings")
                            ),
                        ]),
                    ]),
                    bgcolor=ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE),
                    padding=20,
                    border_radius=10,
                ),
                
                # 配置管理区
                ft.Container(
                    content=ft.Column([
                        ft.Text("配置管理", size=20, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.ElevatedButton(
                                "导入配置",
                                icon=ft.icons.UPLOAD_FILE,
                                on_click=self.import_settings
                            ),
                            ft.ElevatedButton(
                                "导出配置",
                                icon=ft.icons.DOWNLOAD,
                                on_click=self.export_settings
                            ),
                            ft.ElevatedButton(
                                "备份设置",
                                icon=ft.icons.BACKUP,
                                on_click=self.backup_settings
                            ),
                            ft.ElevatedButton(
                                "重置设置",
                                icon=ft.icons.RESTORE,
                                style=ft.ButtonStyle(
                                    color=ft.Colors.ERROR
                                ),
                                on_click=self.reset_settings
                            ),
                        ]),
                    ]),
                    bgcolor=ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE),
                    padding=20,
                    border_radius=10,
                ),
                
                # 关于区
                ft.Container(
                    content=ft.Column([
                        ft.Text("关于", size=20, weight=ft.FontWeight.BOLD),
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.INFO),
                            title=ft.Text("关于流影工坊"),
                            subtitle=ft.Text("查看软件版本、许可证和致谢信息"),
                            on_click=lambda _: self.page.go("/about")
                        ),
                    ]),
                    bgcolor=ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE),
                    padding=20,
                    border_radius=10,
                ),
                
            ], spacing=20, scroll=ft.ScrollMode.AUTO),
            padding=20,
        )
    
    def create_path_setting(self, label, setting_key, hint):
        """创建路径设置组件"""
        return ft.Column([
            ft.Text(label),
            ft.Row([
                ft.TextField(
                    value=self.settings.get(setting_key, ""),
                    hint_text=hint,
                    expand=True,
                    read_only=True,
                ),
                ft.ElevatedButton(
                    "浏览",
                    icon=ft.icons.FOLDER_OPEN,
                    on_click=lambda _: self.pick_folder(setting_key)
                ),
            ]),
        ])
    
    def show_asset_management(self, e):
        """显示资源管理设置对话框"""
        tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(
                    text="分类",
                    content=self.create_category_editor()
                ),
                ft.Tab(
                    text="标签",
                    content=self.create_tags_editor()
                ),
                ft.Tab(
                    text="评分",
                    content=self.create_rating_editor()
                ),
                ft.Tab(
                    text="颜色标记",
                    content=self.create_color_editor()
                ),
            ],
        )
        
        dialog = ft.AlertDialog(
            title=ft.Text("资源管理设置"),
            content=tabs,
            actions=[
                ft.TextButton("取消", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                ft.TextButton("保存", on_click=lambda e: self.save_asset_settings(dialog)),
            ],
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def import_settings(self, e):
        """导入设置"""
        def get_file_result(e: ft.FilePickerResultEvent):
            if e.files and len(e.files) > 0:
                try:
                    file_path = e.files[0].path
                    with open(file_path, 'r', encoding='utf-8') as f:
                        imported_settings = json.load(f)
                    self.settings.update(imported_settings)
                    self.save_settings()
                    self.show_success("设置导入成功")
                    self.page.update()
                except Exception as ex:
                    self.show_error(f"导入失败：{str(ex)}")
        
        picker = ft.FilePicker(
            on_result=get_file_result
        )
        self.page.overlay.append(picker)
        self.page.update()
        picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["json"]
        )
    
    def export_settings(self, e):
        """导出设置"""
        def get_file_result(e: ft.FilePickerResultEvent):
            if e.path:
                try:
                    with open(e.path, 'w', encoding='utf-8') as f:
                        json.dump(self.settings, f, ensure_ascii=False, indent=2)
                    self.show_success("设置导出成功")
                except Exception as ex:
                    self.show_error(f"导出失败：{str(ex)}")
        
        picker = ft.FilePicker(
            on_result=get_file_result
        )
        self.page.overlay.append(picker)
        self.page.update()
        picker.save_file(
            allowed_extensions=["json"]
        )
    
    def save_all_settings(self, e):
        """保存所有设置"""
        try:
            self.save_settings()
            self.show_success("设置保存成功")
        except Exception as ex:
            self.show_error(f"保存失败：{str(ex)}")
    
    def pick_folder(self, setting_key):
        """选择文件夹"""
        def get_directory_result(e: ft.FilePickerResultEvent):
            if e.path:
                self.settings[setting_key] = e.path
                self.save_settings()
                self.page.update()
        
        picker = ft.FilePicker(
            on_result=get_directory_result
        )
        self.page.overlay.append(picker)
        self.page.update()
        picker.get_directory_path()
    
    def change_language(self, e):
        """更改文件夹命名语言"""
        self.settings["folder_language"] = e.data
        self.save_settings()
    
    def show_camera_manager(self, e):
        """显示相机管理对话框"""
        camera_list = ft.Column(spacing=10)
        
        def add_camera_preset():
            camera_list.controls.append(
                ft.Row(
                    [
                        ft.TextField(
                            label="品牌",
                            width=150,
                        ),
                        ft.TextField(
                            label="型号",
                            width=150,
                        ),
                        ft.IconButton(
                            icon=ft.icons.DELETE,
                            on_click=lambda e, row=len(camera_list.controls)-1: 
                                camera_list.controls.pop(row) or self.page.update()
                        )
                    ],
                    alignment=ft.MainAxisAlignment.START,
                )
            )
            self.page.update()
        
        # 加载现有相机预设
        for camera in self.settings["camera_presets"]:
            camera_list.controls.append(
                ft.Row(
                    [
                        ft.TextField(
                            label="品牌",
                            value=camera["brand"],
                            width=150,
                        ),
                        ft.TextField(
                            label="型号",
                            value=camera["model"],
                            width=150,
                        ),
                        ft.IconButton(
                            icon=ft.icons.DELETE,
                            on_click=lambda e, row=len(camera_list.controls)-1: 
                                camera_list.controls.pop(row) or self.page.update()
                        )
                    ],
                    alignment=ft.MainAxisAlignment.START,
                )
            )
        
        def save_camera_presets(e):
            new_presets = []
            for row in camera_list.controls:
                brand = row.controls[0].value
                model = row.controls[1].value
                if brand and model:  # 只保存完整的数据
                    new_presets.append({"brand": brand, "model": model})
            self.settings["camera_presets"] = new_presets
            self.save_settings()
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("相机预设管理"),
            content=ft.Column(
                [
                    camera_list,
                    ft.ElevatedButton(
                        "添加相机",
                        icon=ft.icons.ADD,
                        on_click=lambda _: add_camera_preset()
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
                height=400,
            ),
            actions=[
                ft.TextButton("取消", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                ft.TextButton("保存", on_click=save_camera_presets),
            ],
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def show_folder_manager(self, e):
        """显示文件夹结构管理对话框"""
        folder_tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(
                    text="简易项目",
                    content=self.create_folder_structure_editor("simple")
                ),
                ft.Tab(
                    text="标准项目",
                    content=self.create_folder_structure_editor("standard")
                ),
                ft.Tab(
                    text="大型项目",
                    content=self.create_folder_structure_editor("large")
                ),
            ],
        )
        
        dialog = ft.AlertDialog(
            title=ft.Text("文件夹结构管理"),
            content=folder_tabs,
            actions=[
                ft.TextButton("取消", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                ft.TextButton("保存", on_click=lambda e: self.save_folder_structures(dialog)),
            ],
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def create_folder_structure_editor(self, structure_type):
        """创建文件夹结构编辑器"""
        folder_list = ft.Column(spacing=10)
        
        def add_folder():
            folder_list.controls.append(
                ft.Row(
                    [
                        ft.TextField(
                            label="文件夹名称",
                            width=300,
                        ),
                        ft.IconButton(
                            icon=ft.icons.DELETE,
                            on_click=lambda e, row=len(folder_list.controls)-1: 
                                folder_list.controls.pop(row) or self.page.update()
                        )
                    ],
                    alignment=ft.MainAxisAlignment.START,
                )
            )
            self.page.update()
        
        # 加载现有文件夹结构
        for folder in self.settings["folder_structures"][structure_type]:
            folder_list.controls.append(
                ft.Row(
                    [
                        ft.TextField(
                            label="文件夹名称",
                            value=folder,
                            width=300,
                        ),
                        ft.IconButton(
                            icon=ft.icons.DELETE,
                            on_click=lambda e, row=len(folder_list.controls)-1: 
                                folder_list.controls.pop(row) or self.page.update()
                        )
                    ],
                    alignment=ft.MainAxisAlignment.START,
                )
            )
        
        return ft.Column(
            [
                folder_list,
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "添加文件夹",
                            icon=ft.icons.ADD,
                            on_click=lambda _: add_folder()
                        ),
                        ft.ElevatedButton(
                            "预览结构",
                            icon=ft.icons.PREVIEW,
                            on_click=lambda _: self.preview_folder_structure(structure_type)
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            height=400,
        )

    def save_folder_structures(self, dialog):
        """保存文件夹结构"""
        for i, structure_type in enumerate(["simple", "standard", "large"]):
            folder_list = dialog.content.tabs[i].content.controls[0]
            new_structure = []
            for row in folder_list.controls:
                folder_name = row.controls[0].value
                if folder_name:  # 只保存非空文件夹名
                    new_structure.append(folder_name)
            self.settings["folder_structures"][structure_type] = new_structure
        
        self.save_settings()
        dialog.open = False
        self.page.update()

    def show_error(self, message):
        """显示错误提示"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.colors.ERROR,
            show_close_icon=True,
            duration=4000
        )
        self.page.snack_bar.open = True
        self.page.update()

    def show_success(self, message):
        """显示成功提示"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.colors.SUCCESS,
            show_close_icon=True,
            duration=4000
        )
        self.page.snack_bar.open = True
        self.page.update()

    def show_preview(self, title, content):
        """显示预览对话框"""
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=content,
            actions=[
                ft.TextButton("关闭", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def create_category_editor(self):
        """创建分类编辑器"""
        category_list = ft.Column(spacing=10)
        
        def add_category():
            category_list.controls.append(
                ft.Row(
                    [
                        ft.TextField(
                            label="分类名称",
                            width=200,
                        ),
                        ft.TextField(
                            label="分类描述",
                            width=300,
                        ),
                        ft.IconButton(
                            icon=ft.icons.DELETE,
                            on_click=lambda e, row=len(category_list.controls)-1: 
                                category_list.controls.pop(row) or self.page.update()
                        )
                    ],
                    alignment=ft.MainAxisAlignment.START,
                )
            )
            self.page.update()
        
        # 加载现有分类
        for category in self.settings.get("categories", []):
            category_list.controls.append(
                ft.Row(
                    [
                        ft.TextField(
                            label="分类名称",
                            value=category["name"],
                            width=200,
                        ),
                        ft.TextField(
                            label="分类描述",
                            value=category["description"],
                            width=300,
                        ),
                        ft.IconButton(
                            icon=ft.icons.DELETE,
                            on_click=lambda e, row=len(category_list.controls)-1: 
                                category_list.controls.pop(row) or self.page.update()
                        )
                    ],
                    alignment=ft.MainAxisAlignment.START,
                )
            )
        
        return ft.Column(
            [
                category_list,
                ft.ElevatedButton(
                    "添加分类",
                    icon=ft.icons.ADD,
                    on_click=lambda _: add_category()
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            height=400,
        )

    def create_tags_editor(self):
        """创建标签编辑器"""
        tag_list = ft.Column(spacing=10)
        
        def add_tag():
            tag_list.controls.append(
                ft.Row(
                    [
                        ft.TextField(
                            label="标签名称",
                            width=150,
                        ),
                        ft.Dropdown(
                            label="标签类型",
                            width=150,
                            options=[
                                ft.dropdown.Option("project"),
                                ft.dropdown.Option("asset"),
                                ft.dropdown.Option("camera"),
                            ],
                        ),
                        ft.IconButton(
                            icon=ft.icons.DELETE,
                            on_click=lambda e, row=len(tag_list.controls)-1: 
                                tag_list.controls.pop(row) or self.page.update()
                        )
                    ],
                    alignment=ft.MainAxisAlignment.START,
                )
            )
            self.page.update()
        
        return ft.Column(
            [
                tag_list,
                ft.ElevatedButton(
                    "添加标签",
                    icon=ft.icons.ADD,
                    on_click=lambda _: add_tag()
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            height=400,
        )

    def create_rating_editor(self):
        """创建评分编辑器"""
        return ft.Column(
            [
                ft.Text("星级评分设置"),
                ft.Slider(
                    min=1,
                    max=5,
                    divisions=4,
                    label="最大星级数",
                    value=self.settings.get("max_rating", 5),
                ),
                ft.Checkbox(
                    label="允许半星评分",
                    value=self.settings.get("allow_half_rating", True),
                ),
            ],
            spacing=20,
        )

    def create_color_editor(self):
        """创建颜色标记编辑器"""
        color_list = ft.Column(spacing=10)
        
        def add_color():
            color_list.controls.append(
                ft.Row(
                    [
                        ft.TextField(
                            label="标记名称",
                            width=150,
                        ),
                        ft.ColorPicker(
                            width=50,
                            height=50,
                            border_radius=25,
                        ),
                        ft.IconButton(
                            icon=ft.icons.DELETE,
                            on_click=lambda e, row=len(color_list.controls)-1: 
                                color_list.controls.pop(row) or self.page.update()
                        )
                    ],
                    alignment=ft.MainAxisAlignment.START,
                )
            )
            self.page.update()
        
        return ft.Column(
            [
                color_list,
                ft.ElevatedButton(
                    "添加颜色标记",
                    icon=ft.icons.ADD,
                    on_click=lambda _: add_color()
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            height=400,
        )

    def preview_folder_structure(self, structure_type):
        """预览文件夹结构"""
        structure = self.settings["folder_structures"][structure_type]
        language = self.settings["folder_language"]
        folder_names = self.settings["folder_names"][language]
        
        preview = ft.Column(
            controls=[
                ft.Text("📁 项目根目录"),
                *[
                    ft.Text(f"  └─ {folder_names[folder]}", selectable=True)
                    for folder in structure
                ],
            ],
            spacing=10,
        )
        
        self.show_preview(
            f"{structure_type.title()} 项目结构预览",
            preview
        )

    def save_asset_settings(self, dialog):
        """保存资源管理设置"""
        try:
            # 保存分类设置
            categories = []
            category_list = dialog.content.tabs[0].content.controls[0]
            for row in category_list.controls:
                name = row.controls[0].value
                desc = row.controls[1].value
                if name:
                    categories.append({"name": name, "description": desc})
            self.settings["categories"] = categories
            
            # 保存标签设置
            tags = []
            tag_list = dialog.content.tabs[1].content.controls[0]
            for row in tag_list.controls:
                name = row.controls[0].value
                tag_type = row.controls[1].value
                if name and tag_type:
                    tags.append({"name": name, "type": tag_type})
            self.settings["tags"] = tags
            
            # 保存评分设置
            rating_controls = dialog.content.tabs[2].content.controls
            self.settings["max_rating"] = rating_controls[1].value
            self.settings["allow_half_rating"] = rating_controls[2].value
            
            # 保存颜色标记
            colors = []
            color_list = dialog.content.tabs[3].content.controls[0]
            for row in color_list.controls:
                name = row.controls[0].value
                color = row.controls[1].value
                if name and color:
                    colors.append({"name": name, "color": color})
            self.settings["colors"] = colors
            
            self.save_settings()
            dialog.open = False
            self.show_success("资源管理设置已保存")
            self.page.update()
            
        except Exception as ex:
            self.show_error(f"保存失败：{str(ex)}")

    def validate_settings(self):
        """验证设置完整性"""
        required_paths = [
            ("工程目录", "project_path"),
            ("剪辑软件模板目录", "editing_templates_path"),
        ]
        
        missing = []
        for name, key in required_paths:
            if not self.settings.get(key):
                missing.append(name)
        
        if missing:
            self.show_error(f"以下必要路径未设置：{', '.join(missing)}")
            return False
        
        return True

    def reset_settings(self, e):
        """重置设置"""
        dialog = ft.AlertDialog(
            title=ft.Text("确认重置"),
            content=ft.Text("确定要重置所有设置吗？这将清除所有自定义配置。"),
            actions=[
                ft.TextButton("取消", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                ft.TextButton(
                    "确定",
                    on_click=lambda e: self.do_reset_settings(dialog),
                    style=ft.ButtonStyle(color=ft.Colors.ERROR),
                ),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def do_reset_settings(self, dialog):
        """执行重置设置"""
        try:
            if os.path.exists('config/workflow_settings.json'):
                os.remove('config/workflow_settings.json')
            self.load_settings()  # 重新加载默认设置
            dialog.open = False
            self.show_success("设置已重置为默认值")
            self.page.update()
        except Exception as ex:
            self.show_error(f"重置失败：{str(ex)}")

    def backup_settings(self, e):
        """备份设置"""
        try:
            backup_dir = "config/backups"
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"settings_backup_{timestamp}.json")
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
                
            self.show_success("设置已备份")
        except Exception as ex:
            self.show_error(f"备份失败：{str(ex)}")

    def show_help(self):
        """显示帮助对话框"""
        dialog = ft.AlertDialog(
            title=ft.Text("帮助"),
            content=ft.Text("这里是帮助内容"),
            actions=[
                ft.TextButton("关闭", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update() 