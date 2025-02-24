# -*- coding: utf-8 -*-
import flet as ft
import platform  # 系统检测模块
from app.controllers.main_controller import MainController
from app.utils.db_manager import DatabaseManager
from app.utils.config_loader import ConfigLoader

# 将字符串声明为 UTF-8
text = u'你的中文字符串'

def main():
    def app_view(page: ft.Page):
        # 动态平台检测
        current_os = platform.system()
        print(f"当前运行平台: {current_os}")
        
        # 设置窗口尺寸和属性
        page.window_width = 1534
        page.window_height = 1030
        page.window_min_width = 1200
        page.window_min_height = 800
        page.window_resizable = True
        page.window_maximizable = True
        page.title = "流影工坊"
        
        # 加载配置
        config = ConfigLoader.load_config()
        
        # 初始化数据库
        db = DatabaseManager(config['database']['path'])
        
        # 跨平台主题配置
        system_font = {
            "Darwin": "PingFang SC",  # macOS
            "Windows": "Microsoft YaHei UI",  # Windows
            "Linux": "Noto Sans CJK SC"  # Linux
        }.get(current_os, "Arial")  # 默认回退字体
        
        # 设置深色主题
        page.dark_theme = ft.Theme(
            visual_density=ft.VisualDensity.COMFORTABLE,
            use_material3=True,
            font_family=system_font,
            color_scheme=ft.ColorScheme(
                primary=ft.Colors.BLUE_700,
                secondary=ft.Colors.GREEN_700,
                surface=ft.Colors.GREY_900,
            )
        )
        
        # 设置浅色主题
        page.light_theme = ft.Theme(
            visual_density=ft.VisualDensity.COMFORTABLE,
            use_material3=True,
            font_family=system_font,
            color_scheme=ft.ColorScheme(
                primary=ft.Colors.BLUE_700,
                secondary=ft.Colors.GREEN_700,
                surface=ft.Colors.GREY_100,
            )
        )
        
        # 设置当前主题
        page.theme_mode = config['app']['theme_mode']

        # 页面布局优化
        page.padding = 0
        page.spacing = 0
        page.vertical_alignment = ft.CrossAxisAlignment.START
        page.horizontal_alignment = ft.CrossAxisAlignment.START
        
        # 初始化主控制器
        controller = MainController(page, db)
        controller.initialize()

        # 增强调试信息
        print(f"[系统状态] 窗口尺寸: {page.window_width}x{page.window_height}")

    # 启动应用
    ft.app(
        target=app_view,
        assets_dir="assets",
        view=ft.AppView.FLET_APP,
        port=0
    )

if __name__ == "__main__":
    main()