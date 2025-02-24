import flet as ft

class NavigationView:
    def __init__(self, page: ft.Page, on_route_change):
        self.page = page
        self.on_route_change = on_route_change
        
    def build(self):
        return ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.CREATE_NEW_FOLDER,
                    selected_icon=ft.icons.CREATE_NEW_FOLDER,
                    label="工作流创建"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.BACKUP,
                    selected_icon=ft.icons.BACKUP,
                    label="备份校验"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.MOVIE_FILTER,
                    selected_icon=ft.icons.MOVIE_FILTER,
                    label="AE模版管理"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.VIDEO_LIBRARY,
                    selected_icon=ft.icons.VIDEO_LIBRARY,
                    label="视频素材"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.AUDIO_FILE,
                    selected_icon=ft.icons.AUDIO_FILE,
                    label="音效管理"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.FILTER,
                    selected_icon=ft.icons.FILTER,
                    label="LUT管理"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.DOWNLOAD,
                    selected_icon=ft.icons.DOWNLOAD,
                    label="样片下载"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.HISTORY,
                    selected_icon=ft.icons.HISTORY,
                    label="历史工程"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SETTINGS,
                    selected_icon=ft.icons.SETTINGS,
                    label="设置"
                ),
            ],
            on_change=self.on_route_change,
        ) 