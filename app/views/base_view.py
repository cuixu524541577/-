import flet as ft

class BaseView:
    def __init__(self, page: ft.Page):
        self.page = page

    def show_error(self, message: str):
        """显示错误提示"""
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.colors.ERROR,
            )
        )

    def show_success(self, message: str):
        """显示成功提示"""
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.colors.GREEN,
            )
        ) 