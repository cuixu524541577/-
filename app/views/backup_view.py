import flet as ft
from app.utils.db_manager import DatabaseManager

class BackupView:
    def __init__(self, page: ft.Page, db: DatabaseManager):
        self.page = page
        self.db = db
        
    def build(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("备份校验", size=32, weight=ft.FontWeight.BOLD),
                    ft.TextField(
                        label="源文件夹",
                        hint_text="选择源文件夹",
                    ),
                    ft.TextField(
                        label="备份文件夹",
                        hint_text="选择备份文件夹",
                    ),
                    ft.ElevatedButton(
                        text="开始校验",
                        on_click=self.start_verification
                    ),
                ],
                spacing=20,
            ),
            padding=20,
        )
        
    def start_verification(self, e):
        # 实现备份校验逻辑
        pass 