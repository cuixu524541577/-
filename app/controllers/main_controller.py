import flet as ft
from app.utils.db_manager import DatabaseManager
from app.views.navigation_view import NavigationView
from app.views.workflow_view import WorkflowView
from app.views.backup_view import BackupView
from app.views.ae_template_view import AETemplateView
from app.views.video_assets_view import VideoAssetsView
from app.views.audio_assets_view import AudioAssetsView
from app.views.lut_view import LUTView
from app.views.sample_download_view import SampleDownloadView
from app.views.history_view import HistoryView
from app.views.settings_view import SettingsView
from app.views.about_view import AboutView
from app.views.camera_manager_view import CameraManagerView
from app.views.folder_manager_view import FolderManagerView
from app.views.path_settings_view import PathSettingsView
from app.views.asset_settings_view import AssetSettingsView
import json
import os

class MainController:
    def __init__(self, page: ft.Page, db: DatabaseManager):
        self.page = page
        self.db = db
        self.current_view = None
        
        # 加载设置
        try:
            with open('config/workflow_settings.json', 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
        except Exception as e:
            print(f"[ERROR] 加载设置失败: {str(e)}")
            self.settings = {}
        
    def initialize(self):
        """初始化主界面"""
        # 创建主布局
        self.main_content = ft.Container(
            content=None,
            expand=True,  # 让容器自动填充可用空间
        )
        
        # 创建导航栏
        self.navigation = NavigationView(self.page, self.handle_route_change)
        
        # 设置主布局
        self.page.add(
            ft.Row(
                [
                    self.navigation.build(),
                    ft.VerticalDivider(width=1),
                    self.main_content,
                ],
                expand=True,  # 让行布局填充整个窗口
                spacing=0,    # 减少间距使布局更紧凑
            )
        )
        
        # 检查路径设置
        if not self.check_paths():
            # 如果路径无效，跳转到设置页面
            self.handle_route_change(8)  # 8是设置页面的索引
            self.show_path_warning()
        else:
            # 默认显示工作流创建界面
            self.handle_route_change(0)
        
        # 添加路由处理
        self.page.on_route_change = self.handle_page_route_change
        self.page.go("/")
    
    def check_paths(self):
        """检查必要路径是否有效"""
        try:
            with open('config/workflow_settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                
            required_paths = [
                settings.get("project_path", ""),
                settings.get("editing_templates_path", ""),
            ]
            
            for path in required_paths:
                if not path or not os.path.exists(path):
                    return False
            
            return True
            
        except Exception:
            return False
    
    def show_path_warning(self):
        """显示路径警告"""
        dialog = ft.AlertDialog(
            title=ft.Text("路径设置无效"),
            content=ft.Text("检测到必要的路径设置无效或不存在，请在设置中配置正确的路径。"),
            actions=[
                ft.TextButton("确定", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def handle_route_change(self, route):
        """处理路由变化"""
        if isinstance(route, str):
            # 处理字符串路由
            if route == "/path-settings":
                self.main_content.content = PathSettingsView(self.page, self.current_view.settings).build()
            elif route == "/asset-settings":
                # 构建资产设置所需的配置
                asset_settings = {
                    "database_path": self.settings.get("database_path", ""),
                }
                # 如果数据库路径未设置，使用默认路径
                if not asset_settings["database_path"]:
                    asset_settings["database_path"] = os.path.join(
                        self.settings.get("project_path", ""),
                        "database"
                    )
                self.main_content.content = AssetSettingsView(
                    self.page,
                    asset_settings
                ).build()
            elif route == "/camera-manager":
                self.main_content.content = CameraManagerView(self.page, self.current_view.settings).build()
            elif route == "/folder-manager":
                self.main_content.content = FolderManagerView(self.page, self.current_view.settings).build()
        else:
            # 处理数字索引
            index = route.control.selected_index if isinstance(route, ft.ControlEvent) else route
            
            views = [
                WorkflowView(self.page, self.db),
                BackupView(self.page, self.db),
                AETemplateView(self.page, self.db),
                VideoAssetsView(self.page, self.db),
                AudioAssetsView(self.page, self.db),
                LUTView(self.page, self.db),
                SampleDownloadView(self.page, self.db),
                HistoryView(self.page, self.db),
                SettingsView(self.page, self.db),
            ]
            
            # 如果不是设置页面，检查路径是否有效
            if index != 8 and not self.check_paths():
                self.show_path_warning()
                index = 8  # 强制跳转到设置页面
            
            self.current_view = views[index]
            self.main_content.content = self.current_view.build()
        
        self.page.update()
    
    def handle_page_route_change(self, route):
        """处理页面路由变化"""
        if route.route == "/about":
            self.main_content.content = AboutView(self.page).build()
        elif route.route == "/settings":
            self.handle_route_change(8)  # 切换到设置页面
        else:
            # 处理其他路由
            self.handle_route_change(route.route)
        self.page.update() 