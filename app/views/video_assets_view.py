import flet as ft
from app.utils.db_manager import DatabaseManager

class VideoAssetsView:
    def __init__(self, page: ft.Page, db: DatabaseManager):
        self.page = page
        self.db = db
        
    def build(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("视频素材管理", size=32, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.TextField(
                            label="素材名称",
                            hint_text="搜索素材",
                            expand=True
                        ),
                        ft.ElevatedButton(
                            text="导入素材",
                            on_click=self.import_asset
                        )
                    ]),
                    ft.GridView(
                        expand=1,
                        runs_count=5,
                        max_extent=150,
                        child_aspect_ratio=1.0,
                        spacing=10,
                        run_spacing=10,
                    )
                ],
                spacing=20,
                expand=True,
            ),
            padding=20,
            expand=True,
        )
        
    def import_asset(self, e):
        # 实现导入素材的逻辑
        pass 