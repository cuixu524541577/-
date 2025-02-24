import flet as ft
from app.utils.db_manager import DatabaseManager

class AudioAssetsView:
    def __init__(self, page: ft.Page, db: DatabaseManager):
        self.page = page
        self.db = db
        
    def build(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("音效管理", size=32, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.TextField(
                            label="音效名称",
                            hint_text="搜索音效",
                            expand=True
                        ),
                        ft.ElevatedButton(
                            text="导入音效",
                            on_click=self.import_audio
                        )
                    ]),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("音效名称")),
                            ft.DataColumn(ft.Text("时长")),
                            ft.DataColumn(ft.Text("分类")),
                            ft.DataColumn(ft.Text("操作"))
                        ],
                        rows=[]
                    )
                ],
                spacing=20,
            ),
            padding=20,
        )
        
    def import_audio(self, e):
        # 实现导入音效的逻辑
        pass 