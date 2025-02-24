import flet as ft
from app.utils.db_manager import DatabaseManager

class LUTView:
    def __init__(self, page: ft.Page, db: DatabaseManager):
        self.page = page
        self.db = db
        
    def build(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("LUT管理", size=32, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.TextField(
                            label="LUT名称",
                            hint_text="搜索LUT",
                            expand=True
                        ),
                        ft.ElevatedButton(
                            text="添加LUT",
                            on_click=self.add_lut
                        )
                    ]),
                    ft.GridView(
                        expand=1,
                        runs_count=4,
                        max_extent=200,
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
        
    def add_lut(self, e):
        # 实现添加LUT的逻辑
        pass 