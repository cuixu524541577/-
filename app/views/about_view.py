import flet as ft

class AboutView:
    def __init__(self, page: ft.Page):
        self.page = page
        
    def build(self):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.IconButton(
                        icon=ft.icons.ARROW_BACK,
                        on_click=lambda _: self.page.go("/settings")
                    ),
                    ft.Text("关于我们", size=32, weight=ft.FontWeight.BOLD),
                ]),
                
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("软件信息", size=20, weight=ft.FontWeight.BOLD),
                            ft.Text("流影工坊 v1.0.0"),
                            ft.Text("一个集工作流创建、备份校验、素材工程管理的专业管理工具"),
                            ft.Text("by Johnny Cui"),
                            ft.Row([
                                ft.ElevatedButton(
                                    "bilibili",
                                    icon=ft.icons.PLAY_CIRCLE,
                                    url="https://space.bilibili.com/120602530?spm_id_from=333.1007.0.0",
                                    style=ft.ButtonStyle(
                                        bgcolor="#2D2D2D",
                                        color=ft.colors.WHITE,
                                    )
                                ),
                                ft.ElevatedButton(
                                    "抖音",
                                    icon=ft.icons.MUSIC_NOTE,
                                    url="https://www.douyin.com/user/MS4wLjABAAAA9icn6798dXb_Sa6NyzAch4Gng2kV62K5-7FprpTAnUle1hv7pkH9gBUE8tMmqSGO",
                                    style=ft.ButtonStyle(
                                        bgcolor="#2D2D2D",
                                        color=ft.colors.WHITE,
                                    )
                                ),
                            ], spacing=10),
                        ]),
                        padding=20,
                        margin=ft.margin.symmetric(horizontal=10),
                    ),
                    width=float("inf"),
                ),
                
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("开源协议", size=20, weight=ft.FontWeight.BOLD),
                            ft.Text("GPL License"),
                            ft.Text("禁止本代码改为闭源商用软件"),
                            ft.Text("Copyright (c) 2025 Johnny Cui"),
                        ]),
                        padding=20,
                        margin=ft.margin.symmetric(horizontal=10),
                    ),
                    width=float("inf"),
                ),
                
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("感谢", size=20, weight=ft.FontWeight.BOLD),
                            ft.Text("特别感谢以下开源项目："),
                            ft.Text("• Flet - 现代化的 Flutter 框架"),
                            ft.Text("• DeepSeek R1、Claude 3.5 大模型 And Cursor"),
                            ft.Text("• Python - 编程语言"),
                            ft.Text("感谢所有开源代码贡献者的支持！"),
                        ]),
                        padding=20,
                        margin=ft.margin.symmetric(horizontal=10),
                    ),
                    width=float("inf"),
                ),
            ], spacing=20),
            padding=20,
        ) 