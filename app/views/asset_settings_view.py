import flet as ft
from typing import Optional, Dict
from app.utils.asset_settings_manager import AssetSettingsManager
import os

class AssetSettingsView:
    def __init__(self, page: ft.Page, settings: dict):
        print("[DEBUG] 初始化资产设置视图")
        print(f"[DEBUG] 设置参数: {settings}")
        self.page = page
        self.settings = settings
        self.current_asset_type_id: Optional[int] = None
        self.manager = None
        self.tabs = None  # 添加 tabs 引用
        self.asset_types = []  # 添加资产类型列表
        
        try:
            # 从 settings 中获取数据库路径
            db_dir = settings.get("database_path", "")
            if not db_dir:
                raise ValueError("数据库路径未设置")
            
            # 构建数据库文件完整路径
            db_path = os.path.join(db_dir, "app.db")
            
            # 确保数据库目录存在
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            # 初始化资产设置管理器
            self.manager = AssetSettingsManager(db_path)
            
        except Exception as e:
            self.show_error(f"初始化失败: {str(e)}")
    
    def build(self):
        """构建界面"""
        # 获取所有资产类型
        self.asset_types = self.manager.get_asset_types() if self.manager else []
        print(f"[DEBUG] 获取到资产类型: {self.asset_types}")
        
        # 创建资产类型选择标签栏
        asset_type_tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(
                    text=t["display_name"],
                    content=None,
                )
                for t in self.asset_types
            ],
            on_change=self._handle_asset_type_tab_change,
        )
        
        # 如果有资产类型，设置初始选中的资产类型
        if self.asset_types:
            self.current_asset_type_id = self.asset_types[0]["id"]
        
        # 创建设置选项卡
        self.tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="分类", content=self._build_category_editor()),
                ft.Tab(text="标签", content=self._build_tag_editor()),
                ft.Tab(text="评分", content=self._build_rating_editor()),
                ft.Tab(text="颜色标记", content=self._build_color_editor()),
            ],
        )
        
        return ft.Container(
            content=ft.Column([
                # 顶部栏
                ft.Row([
                    ft.IconButton(
                        icon=ft.icons.ARROW_BACK,
                        on_click=lambda _: self.page.go("/settings")
                    ),
                    ft.Text("资产设置", size=20, weight=ft.FontWeight.BOLD),
                ]),
                
                # 资产类型选择标签栏
                asset_type_tabs,
                
                # 分隔线
                ft.Divider(height=1),
                
                # 设置选项卡
                self.tabs,
            ]),
            padding=20,
        )
    
    def _handle_asset_type_tab_change(self, e):
        """处理资产类型标签切换"""
        if e.data == "tab":  # 标签切换事件
            selected_index = e.control.selected_index
            print(f"[DEBUG] 选择资产类型索引: {selected_index}")
            if 0 <= selected_index < len(self.asset_types):
                selected_type = self.asset_types[selected_index]
                print(f"[DEBUG] 选择资产类型: {selected_type['display_name']} (ID: {selected_type['id']})")
                self.current_asset_type_id = selected_type["id"]
                self._refresh_all_editors()
    
    def _build_category_editor(self):
        """构建分类编辑器"""
        category_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=10,
        )
        
        def refresh_categories():
            """刷新分类列表"""
            category_list.controls.clear()
            
            if not self.current_asset_type_id:
                category_list.controls.append(
                    self._build_empty_hint("请选择资产类型")
                )
                return
            
            categories = self.manager.get_categories(self.current_asset_type_id)
            
            if not categories:
                category_list.controls.append(
                    self._build_empty_hint("暂无分类")
                )
                return
            
            for category in categories:
                category_list.controls.append(
                    ft.Container(
                        content=ft.ListTile(
                            leading=ft.Icon(ft.icons.FOLDER),
                            title=ft.Text(category["name"]),
                            subtitle=ft.Text(
                                category["description"] or "无描述",
                                size=12,
                                color=ft.colors.GREY_400,
                            ),
                            trailing=ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.icons.EDIT,
                                        tooltip="编辑",
                                        on_click=lambda e, c=category: self._show_edit_category_form(c)
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        tooltip="删除",
                                        on_click=lambda e, c=category: self._show_delete_category_form(c)
                                    ),
                                ],
                                spacing=0,
                            ),
                        ),
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        border_radius=8,
                        padding=5,
                    )
                )
        
        # 初始刷新
        refresh_categories()
        
        return ft.Column([
            category_list,
            ft.Container(
                content=ft.ElevatedButton(
                    "添加分类",
                    icon=ft.icons.ADD,
                    on_click=lambda _: self._show_add_category_form()
                ),
                padding=10,
            ),
        ])
    
    def _build_empty_hint(self, message: str):
        """构建空状态提示"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        ft.icons.INFO_OUTLINE,
                        size=64,
                        color=ft.colors.GREY_400,
                    ),
                    ft.Text(
                        message,
                        size=16,
                        color=ft.colors.GREY_400,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )
    
    def _show_add_category_form(self):
        """显示添加分类表单"""
        if not self.current_asset_type_id:
            self.show_error("请先选择资产类型")
            return
        
        name_field = ft.TextField(
            label="分类名称",
            width=300,
            autofocus=True
        )
        
        desc_field = ft.TextField(
            label="分类描述",
            width=300,
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        
        def handle_submit(e):
            name = name_field.value.strip()
            desc = desc_field.value.strip()
            if name:
                try:
                    self.manager.add_category(
                        self.current_asset_type_id,
                        name,
                        desc
                    )
                    self._refresh_all_editors()
                    self.show_success(f"已添加分类 '{name}'")
                    dialog.open = False
                    self.page.update()
                except Exception as ex:
                    self.show_error(str(ex))
        
        def handle_cancel(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("添加分类"),
            content=ft.Column([
                name_field,
                desc_field,
            ], tight=True),
            actions=[
                ft.TextButton("取消", on_click=handle_cancel),
                ft.FilledButton("添加", on_click=handle_submit),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _show_edit_category_form(self, category: Dict):
        """显示编辑分类表单"""
        name_field = ft.TextField(
            label="分类名称",
            width=300,
            value=category["name"],
            autofocus=True
        )
        
        desc_field = ft.TextField(
            label="分类描述",
            width=300,
            value=category["description"],
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        
        def handle_submit(e):
            name = name_field.value.strip()
            desc = desc_field.value.strip()
            if name and name != category["name"]:
                try:
                    self.manager.update_category(
                        category["id"],
                        name,
                        desc
                    )
                    self._refresh_all_editors()
                    self.show_success(f"已更新分类 '{name}'")
                    dialog.open = False
                    self.page.update()
                except Exception as ex:
                    self.show_error(str(ex))
        
        def handle_cancel(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("编辑分类"),
            content=ft.Column([
                name_field,
                desc_field,
            ], tight=True),
            actions=[
                ft.TextButton("取消", on_click=handle_cancel),
                ft.FilledButton("保存", on_click=handle_submit),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _show_delete_category_form(self, category: Dict):
        """显示删除分类确认框"""
        def handle_submit(e):
            try:
                self.manager.delete_category(category["id"])
                self._refresh_all_editors()
                self.show_success(f"已删除分类 '{category['name']}'")
                dialog.open = False
                self.page.update()
            except Exception as ex:
                self.show_error(str(ex))
        
        def handle_cancel(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("删除分类", color=ft.colors.ERROR),
            content=ft.Text(f"确定要删除分类 '{category['name']}' 吗？"),
            actions=[
                ft.TextButton("取消", on_click=handle_cancel),
                ft.FilledButton(
                    "删除",
                    on_click=handle_submit,
                    style=ft.ButtonStyle(
                        color=ft.colors.ON_ERROR,
                        bgcolor=ft.colors.ERROR,
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _refresh_all_editors(self):
        """刷新所有编辑器"""
        print(f"[DEBUG] 刷新编辑器, 当前资产类型: {self.current_asset_type_id}")
        if self.current_asset_type_id and self.tabs:
            self.tabs.tabs[0].content = self._build_category_editor()
            self.tabs.tabs[1].content = self._build_tag_editor()
            self.tabs.tabs[2].content = self._build_rating_editor()
            self.tabs.tabs[3].content = self._build_color_editor()
        self.page.update()
    
    def _build_tag_editor(self):
        """构建标签编辑器"""
        tag_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=10,
        )
        
        def refresh_tags():
            """刷新标签列表"""
            tag_list.controls.clear()
            
            if not self.current_asset_type_id:
                tag_list.controls.append(
                    self._build_empty_hint("请选择资产类型")
                )
                return
            
            tags = self.manager.get_tags(self.current_asset_type_id)
            
            if not tags:
                tag_list.controls.append(
                    self._build_empty_hint("暂无标签")
                )
                return
            
            for tag in tags:
                tag_list.controls.append(
                    ft.Container(
                        content=ft.ListTile(
                            leading=ft.Icon(ft.icons.LABEL),
                            title=ft.Text(tag["name"]),
                            subtitle=ft.Text(
                                tag["description"] or "无描述",
                                size=12,
                                color=ft.colors.GREY_400,
                            ),
                            trailing=ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.icons.EDIT,
                                        tooltip="编辑",
                                        on_click=lambda e, t=tag: self._show_edit_tag_form(t)
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        tooltip="删除",
                                        on_click=lambda e, t=tag: self._show_delete_tag_form(t)
                                    ),
                                ],
                                spacing=0,
                            ),
                        ),
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        border_radius=8,
                        padding=5,
                    )
                )
        
        # 初始刷新
        refresh_tags()
        
        return ft.Column([
            tag_list,
            ft.Container(
                content=ft.ElevatedButton(
                    "添加标签",
                    icon=ft.icons.ADD,
                    on_click=lambda _: self._show_add_tag_form()
                ),
                padding=10,
            ),
        ])
    
    def _show_add_tag_form(self):
        """显示添加标签表单"""
        if not self.current_asset_type_id:
            self.show_error("请先选择资产类型")
            return
        
        name_field = ft.TextField(
            label="标签名称",
            width=300,
            autofocus=True
        )
        
        desc_field = ft.TextField(
            label="标签描述",
            width=300,
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        
        def handle_submit(e):
            name = name_field.value.strip()
            desc = desc_field.value.strip()
            if name:
                try:
                    self.manager.add_tag(
                        self.current_asset_type_id,
                        name,
                        desc
                    )
                    self._refresh_all_editors()
                    self.show_success(f"已添加标签 '{name}'")
                    dialog.open = False
                    self.page.update()
                except Exception as ex:
                    self.show_error(str(ex))
        
        def handle_cancel(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("添加标签"),
            content=ft.Column([
                name_field,
                desc_field,
            ], tight=True),
            actions=[
                ft.TextButton("取消", on_click=handle_cancel),
                ft.FilledButton("添加", on_click=handle_submit),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _show_edit_tag_form(self, tag: Dict):
        """显示编辑标签表单"""
        name_field = ft.TextField(
            label="标签名称",
            width=300,
            value=tag["name"],
            autofocus=True
        )
        
        desc_field = ft.TextField(
            label="标签描述",
            width=300,
            value=tag["description"],
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        
        def handle_submit(e):
            name = name_field.value.strip()
            desc = desc_field.value.strip()
            if name and name != tag["name"]:
                try:
                    self.manager.update_tag(
                        tag["id"],
                        name,
                        desc
                    )
                    self._refresh_all_editors()
                    self.show_success(f"已更新标签 '{name}'")
                    dialog.open = False
                    self.page.update()
                except Exception as ex:
                    self.show_error(str(ex))
        
        def handle_cancel(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("编辑标签"),
            content=ft.Column([
                name_field,
                desc_field,
            ], tight=True),
            actions=[
                ft.TextButton("取消", on_click=handle_cancel),
                ft.FilledButton("保存", on_click=handle_submit),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _show_delete_tag_form(self, tag: Dict):
        """显示删除标签确认框"""
        def handle_submit(e):
            try:
                self.manager.delete_tag(tag["id"])
                self._refresh_all_editors()
                self.show_success(f"已删除标签 '{tag['name']}'")
                dialog.open = False
                self.page.update()
            except Exception as ex:
                self.show_error(str(ex))
        
        def handle_cancel(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("删除标签", color=ft.colors.ERROR),
            content=ft.Text(f"确定要删除标签 '{tag['name']}' 吗？"),
            actions=[
                ft.TextButton("取消", on_click=handle_cancel),
                ft.FilledButton(
                    "删除",
                    on_click=handle_submit,
                    style=ft.ButtonStyle(
                        color=ft.colors.ON_ERROR,
                        bgcolor=ft.colors.ERROR,
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _build_rating_editor(self):
        """构建评分编辑器"""
        if not self.current_asset_type_id:
            return self._build_empty_hint("请选择资产类型")
        
        settings = self.manager.get_rating_settings(self.current_asset_type_id)
        if not settings:
            settings = {"max_rating": 5, "allow_half_rating": True}
        
        max_rating_slider = ft.Slider(
            min=1,
            max=10,
            divisions=9,
            label="最大星级数: {value}",
            value=settings["max_rating"],
            on_change=lambda e: self._update_rating_settings(
                max_rating=int(e.data)
            ),
        )
        
        half_rating_switch = ft.Switch(
            label="允许半星评分",
            value=settings["allow_half_rating"],
            on_change=lambda e: self._update_rating_settings(
                allow_half=e.data
            ),
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("评分设置", size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(height=1),
                max_rating_slider,
                half_rating_switch,
            ], spacing=20),
            padding=20,
        )
    
    def _update_rating_settings(self, max_rating=None, allow_half=None):
        """更新评分设置"""
        if not self.current_asset_type_id:
            return
        
        try:
            self.manager.update_rating_settings(
                self.current_asset_type_id,
                max_rating,
                allow_half
            )
            self.show_success("评分设置已更新")
        except Exception as ex:
            self.show_error(str(ex))
    
    def _build_color_editor(self):
        """构建颜色标记编辑器"""
        color_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=10,
        )
        
        def refresh_colors():
            """刷新颜色标记列表"""
            color_list.controls.clear()
            
            if not self.current_asset_type_id:
                color_list.controls.append(
                    self._build_empty_hint("请选择资产类型")
                )
                return
            
            colors = self.manager.get_color_marks(self.current_asset_type_id)
            
            if not colors:
                color_list.controls.append(
                    self._build_empty_hint("暂无颜色标记")
                )
                return
            
            for color in colors:
                color_list.controls.append(
                    ft.Container(
                        content=ft.ListTile(
                            leading=ft.Container(
                                width=24,
                                height=24,
                                bgcolor=color["color"],
                                border_radius=12,
                            ),
                            title=ft.Text(color["name"]),
                            trailing=ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.icons.EDIT,
                                        tooltip="编辑",
                                        on_click=lambda e, c=color: self._show_edit_color_form(c)
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        tooltip="删除",
                                        on_click=lambda e, c=color: self._show_delete_color_form(c)
                                    ),
                                ],
                                spacing=0,
                            ),
                        ),
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        border_radius=8,
                        padding=5,
                    )
                )
        
        # 初始刷新
        refresh_colors()
        
        return ft.Column([
            color_list,
            ft.Container(
                content=ft.ElevatedButton(
                    "添加颜色标记",
                    icon=ft.icons.ADD,
                    on_click=lambda _: self._show_add_color_form()
                ),
                padding=10,
            ),
        ])
    
    def _show_add_color_form(self):
        """显示添加颜色标记表单"""
        if not self.current_asset_type_id:
            self.show_error("请先选择资产类型")
            return
        
        name_field = ft.TextField(
            label="标记名称",
            width=300,
            autofocus=True
        )
        
        color_picker = ft.ColorPicker(
            width=300,
            height=40,
            border_radius=8,
            selected_color=ft.colors.BLUE,
        )
        
        def handle_submit(e):
            name = name_field.value.strip()
            color = color_picker.selected_color
            if name and color:
                try:
                    self.manager.add_color_mark(
                        self.current_asset_type_id,
                        name,
                        color
                    )
                    self._refresh_all_editors()
                    self.show_success(f"已添加颜色标记 '{name}'")
                    dialog.open = False
                    self.page.update()
                except Exception as ex:
                    self.show_error(str(ex))
        
        def handle_cancel(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("添加颜色标记"),
            content=ft.Column([
                name_field,
                ft.Text("选择颜色:", size=12),
                color_picker,
            ], tight=True),
            actions=[
                ft.TextButton("取消", on_click=handle_cancel),
                ft.FilledButton("添加", on_click=handle_submit),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _show_edit_color_form(self, color: Dict):
        """显示编辑颜色标记表单"""
        name_field = ft.TextField(
            label="标记名称",
            width=300,
            value=color["name"],
            autofocus=True
        )
        
        color_picker = ft.ColorPicker(
            width=300,
            height=40,
            border_radius=8,
            selected_color=color["color"],
        )
        
        def handle_submit(e):
            name = name_field.value.strip()
            new_color = color_picker.selected_color
            if name and new_color:
                try:
                    self.manager.update_color_mark(
                        color["id"],
                        name,
                        new_color
                    )
                    self._refresh_all_editors()
                    self.show_success(f"已更新颜色标记 '{name}'")
                    dialog.open = False
                    self.page.update()
                except Exception as ex:
                    self.show_error(str(ex))
        
        def handle_cancel(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("编辑颜色标记"),
            content=ft.Column([
                name_field,
                ft.Text("选择颜色:", size=12),
                color_picker,
                ft.Container(
                    content=ft.Row([
                        ft.Text("当前颜色:"),
                        ft.Container(
                            width=24,
                            height=24,
                            bgcolor=color["color"],
                            border_radius=12,
                        ),
                    ]),
                    margin=ft.margin.only(top=10),
                ),
            ], tight=True),
            actions=[
                ft.TextButton("取消", on_click=handle_cancel),
                ft.FilledButton("保存", on_click=handle_submit),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _show_delete_color_form(self, color: Dict):
        """显示删除颜色标记确认框"""
        def handle_submit(e):
            try:
                self.manager.delete_color_mark(color["id"])
                self._refresh_all_editors()
                self.show_success(f"已删除颜色标记 '{color['name']}'")
                dialog.open = False
                self.page.update()
            except Exception as ex:
                self.show_error(str(ex))
        
        def handle_cancel(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("删除颜色标记", color=ft.colors.ERROR),
            content=ft.Column(
                [
                    ft.Text(f"确定要删除颜色标记 '{color['name']}' 吗？"),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text("标记颜色:"),
                                ft.Container(
                                    width=24,
                                    height=24,
                                    bgcolor=color["color"],
                                    border_radius=12,
                                ),
                            ]
                        ),
                        margin=ft.margin.only(top=10),
                    ),
                ]
            ),
            actions=[
                ft.TextButton("取消", on_click=handle_cancel),
                ft.FilledButton(
                    "删除",
                    on_click=handle_submit,
                    style=ft.ButtonStyle(
                        color=ft.colors.ON_ERROR,
                        bgcolor=ft.colors.ERROR,
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def show_error(self, message: str):
        """显示错误提示"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.colors.ERROR_CONTAINER,
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def show_success(self, message: str):
        """显示成功提示"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.colors.SURFACE_VARIANT,
        )
        self.page.snack_bar.open = True
        self.page.update() 