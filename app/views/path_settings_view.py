import flet as ft
import os
import json
import sqlite3

class PathSettingsView:
    def __init__(self, page: ft.Page, settings):
        self.page = page
        self.settings = settings
        self.path_fields = {}  # 存储路径输入框的引用
        
    def build(self):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.IconButton(
                        icon=ft.icons.ARROW_BACK,
                        on_click=lambda _: self.page.go("/settings")
                    ),
                    ft.Text("路径设置", size=32, weight=ft.FontWeight.BOLD),
                ]),
                
                # 添加数据库路径设置
                self.create_path_setting(
                    "数据库文件路径：", 
                    "database_path", 
                    "存储应用数据的数据库文件路径",
                    is_database=True
                ),
                ft.Divider(height=2, color=ft.colors.GREY_400),  # 添加分隔线
                
                self.create_path_setting("工程目录：", "project_path", "所有工作文件夹将创建在此目录下"),
                self.create_path_setting("剪辑软件模板目录：", "editing_templates_path", "存储各种剪辑软件的模板"),
                self.create_path_setting("AE模版存储目录：", "ae_templates_path", "存储After Effects模板文件"),
                self.create_path_setting("视频素材目录：", "video_assets_path", "存储视频、音频等素材文件"),
                self.create_path_setting("音效库目录：", "audio_assets_path", "存储音效文件"),
                self.create_path_setting("LUT库目录：", "lut_path", "存储LUT文件"),
                self.create_path_setting("样片下载目录：", "sample_download_path", "存储样片下载文件"),
            ]),
            padding=20,
        )
    
    def create_path_setting(self, label, setting_key, hint, is_database=False):
        """创建路径设置组件"""
        # 创建文本框并保存引用
        text_field = ft.TextField(
            value=self.settings.get(setting_key, ""),
            hint_text=hint,
            expand=True,
            read_only=True,
        )
        self.path_fields[setting_key] = text_field
        
        return ft.Column([
            ft.Text(label),
            ft.Row([
                text_field,
                ft.ElevatedButton(
                    "浏览",
                    icon=ft.icons.FOLDER_OPEN,
                    on_click=lambda _: self.pick_folder(setting_key, is_database)
                ),
            ]),
        ])
    
    def pick_folder(self, setting_key, is_database=False):
        """选择文件夹"""
        def get_result(e):
            if e.path:
                try:
                    print(f"[DEBUG] 选择路径: {e.path} (is_database={is_database})")
                    
                    if is_database:
                        # 数据库目录处理
                        db_dir = e.path
                        db_file = os.path.join(db_dir, "app.db")
                        
                        # 确保目录存在
                        os.makedirs(db_dir, exist_ok=True)
                        
                        # 更新设置
                        self.settings[setting_key] = db_dir
                        self.path_fields[setting_key].value = db_dir
                        
                        print(f"[DEBUG] 数据库路径已更新: {db_dir}")
                        self.show_success("数据库路径已更新")
                        
                    else:
                        # 普通文件夹处理
                        self.settings[setting_key] = e.path
                        self.path_fields[setting_key].value = e.path
                        self.show_success("路径已更新")
                    
                    # 保存设置
                    self.save_settings()
                    self.page.update()
                    
                except Exception as ex:
                    print(f"[ERROR] 设置路径失败: {str(ex)}")
                    self.show_error(f"设置路径失败：{str(ex)}")
        
        file_picker = ft.FilePicker(
            on_result=get_result
        )
        self.page.overlay.append(file_picker)
        self.page.update()
        
        # 统一使用文件夹选择
        file_picker.get_directory_path()
    
    def validate_database(self, db_path):
        """验证数据库文件是否有效"""
        if not os.path.exists(db_path):
            return False
            
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 检查是否包含必要的表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ['projects', 'assets', 'templates']  # 添加你的必要表名
            
            conn.close()
            return all(table in tables for table in required_tables)
            
        except sqlite3.Error:
            return False
    
    def create_database(self, db_path):
        """创建新数据库"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            # 创建数据库
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 读取并执行schema.sql文件
            with open('database/schema.sql', 'r', encoding='utf-8') as f:
                schema = f.read()
                cursor.executescript(schema)
            
            conn.commit()
            conn.close()
            
            # 更新设置（使用数据库目录路径）
            db_dir = os.path.dirname(db_path)
            self.settings["database_path"] = db_dir
            self.path_fields["database_path"].value = db_dir
            self.save_settings()
            
            self.show_success("数据库创建成功")
            
        except Exception as e:
            self.show_error(f"创建数据库失败：{str(e)}")
    
    def show_success(self, message):
        """显示成功提示"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.colors.GREEN,
            show_close_icon=True,
            duration=4000
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def save_settings(self):
        """保存设置"""
        with open('config/workflow_settings.json', 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)
    
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