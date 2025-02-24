import flet as ft
from app.utils.db_manager import DatabaseManager

class HistoryView:
    def __init__(self, page: ft.Page, db: DatabaseManager):
        self.page = page
        self.db = db
        
    def build(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("历史工程", size=32, weight=ft.FontWeight.BOLD),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("工程名称")),
                            ft.DataColumn(ft.Text("创建时间")),
                            ft.DataColumn(ft.Text("最后修改")),
                            ft.DataColumn(ft.Text("状态")),
                            ft.DataColumn(ft.Text("操作"))
                        ],
                        rows=[]
                    )
                ],
                spacing=20,
            ),
            padding=20,
        ) 