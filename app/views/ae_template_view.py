import flet as ft
from app.utils.db_manager import DatabaseManager

class AETemplateView:
    def __init__(self, page: ft.Page, db: DatabaseManager):
        self.page = page
        self.db = db
        
    def build(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("AE模板管理", size=32, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.TextField(
                            label="模板名称",
                            hint_text="搜索模板",
                            expand=True
                        ),
                        ft.ElevatedButton(
                            text="添加模板",
                            on_click=self.add_template
                        )
                    ]),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("模板名称")),
                            ft.DataColumn(ft.Text("分类")),
                            ft.DataColumn(ft.Text("创建时间")),
                            ft.DataColumn(ft.Text("操作"))
                        ],
                        rows=[]
                    )
                ],
                spacing=20,
            ),
            padding=20,
        )
        
    def add_template(self, e):
        # 实现添加模板的逻辑
        pass 