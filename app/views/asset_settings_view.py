import flet as ft
from typing import Optional, Dict
from app.utils.asset_settings_manager import AssetSettingsManager
import os
import json

class AssetSettingsView:
    def __init__(self, page: ft.Page, settings: dict):
        print("[DEBUG] 初始化资产设置视图")
        print(f"[DEBUG] 设置参数: {settings}")
        self.page = page
        self.settings = settings
        
        # 从 config.json 读取主题设置
        try:
            with open('config/config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.theme_mode = config["app"]["theme_mode"]
        except Exception as e:
            print(f"[ERROR] 读取配置文件失败: {str(e)}")
            self.theme_mode = "dark"  # 默认使用亮色主题
            
        # 根据主题模式设置图标颜色
        self.icon_color = ft.colors.WHITE if self.theme_mode == "dark" else ft.colors.BLACK
        self.current_asset_type_id: Optional[int] = None
        self.current_settings_type: Optional[str] = None
        self.manager = None
        self.content_container = None
        self.form_container = None
        self.asset_types = []
        self.asset_type_dropdown = None  # 添加下拉框引用
        self.settings_type_dropdown = None  # 添加下拉框引用
        
        # 添加表单容器引用
        self.category_form = ft.Container(
            visible=False,
            content=None,
            padding=10,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=8,
            margin=ft.margin.only(bottom=10),
        )
        
        # 添加颜色表单容器
        self.color_form = ft.Container(
            visible=False,
            content=None,
            padding=10,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=8,
            margin=ft.margin.only(bottom=10),
        )
        
        # 添加标签表单容器
        self.tag_form = ft.Container(
            visible=False,
            content=None,
            padding=10,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=8,
            margin=ft.margin.only(bottom=10),
        )
        
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
        
        # 创建资产类型下拉框
        self.asset_type_dropdown = ft.Dropdown(
            label="选择资产类型",
            width=450,  # 设置固定宽度
            border_color="blue",  # 设置边框颜色为蓝色
            options=[
                ft.dropdown.Option(
                    key=str(t["id"]),
                    text=t["display_name"]
                ) for t in self.asset_types
            ],
            value=str(self.current_asset_type_id) if self.current_asset_type_id else None,
            on_change=self._handle_asset_type_change,
            autofocus=True
        )
        
        # 创建设置类型下拉框
        self.settings_type_dropdown = ft.Dropdown(
            label="选择设置类型",
            width=450,  # 设置固定宽度
            border_color="blue",  # 设置边框颜色为蓝色
            options=[
                ft.dropdown.Option("category", "分类设置"),
                ft.dropdown.Option("tag", "标签设置"),
                ft.dropdown.Option("rating", "评分设置"),
                ft.dropdown.Option("color", "颜色标记"),
            ],
            on_change=self._handle_settings_type_change
        )
        
        # 创建下拉框容器
        dropdown_container = ft.Container(
            content=ft.Row(
                [
                    self.asset_type_dropdown,
                    self.settings_type_dropdown,
                ],
                spacing=20,
            ),
            margin=ft.margin.only(left=0, right=10, bottom=10),  # 修改边距，左边对齐
            padding=10
        )
        
        # 创建内容容器
        self.content_container = ft.Container(
            content=None,
            expand=True,
            padding=0,  # 移除内边距
        )
        
        # 创建表单容器
        self.form_container = ft.Container(
            visible=False,
            content=None,
            padding=10,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=8,
            margin=ft.margin.only(top=20)
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
                ], alignment=ft.MainAxisAlignment.START),
                
                # 下拉框区域
                dropdown_container,
                
                # 内容区域
                self.content_container,
                
                # 表单区域
                self.form_container,
            ]),
            padding=20,
        )
    
    def _handle_asset_type_change(self, e):
        """处理资产类型变化"""
        try:
            if e.data:
                print(f"[DEBUG] 资产类型切换: {e.data}")
                self.current_asset_type_id = int(e.data)
                print(f"[DEBUG] 当前资产类型ID: {self.current_asset_type_id}")
                self._refresh_content()
        except Exception as ex:
            print(f"[ERROR] 资产类型切换失败: {str(ex)}")
            self.show_error(f"切换失败: {str(ex)}")
    
    def _handle_settings_type_change(self, e):
        """处理设置类型变化"""
        try:
            if e.data:
                print(f"[DEBUG] 设置类型切换: {e.data}")
                self.current_settings_type = e.data
                print(f"[DEBUG] 当前设置类型: {self.current_settings_type}")
                self._refresh_content()
        except Exception as ex:
            print(f"[ERROR] 设置类型切换失败: {str(ex)}")
            self.show_error(f"切换失败: {str(ex)}")
    
    def _refresh_content(self):
        """刷新内容区域"""
        print(f"[DEBUG] 刷新内容: type_id={self.current_asset_type_id}, settings_type={self.current_settings_type}")
        
        if not self.current_asset_type_id or not self.current_settings_type:
            self.content_container.content = self._build_empty_hint(
                "请选择资产类型和设置类型"
            )
            self.page.update()
            return
        
        try:
            content_map = {
                "category": self._build_category_editor,
                "tag": self._build_tag_editor,
                "rating": self._build_rating_editor,
                "color": self._build_color_editor
            }
            
            builder = content_map.get(self.current_settings_type)
            if builder:
                self.content_container.content = builder()
            else:
                print(f"[ERROR] 未知的设置类型: {self.current_settings_type}")
                self.content_container.content = self._build_empty_hint(
                    "未知的设置类型"
                )
            
            self.page.update()
            
        except Exception as ex:
            print(f"[ERROR] 刷新内容失败: {str(ex)}")
            self.show_error(f"刷新失败: {str(ex)}")
    
    def _build_category_editor(self):
        """构建分类编辑器"""
        print("[DEBUG] 构建分类编辑器")
        
        # 分类列表
        category_list = ft.GridView(
            expand=True,
            runs_count=4,  # 每行4个
            max_extent=300,  # 调整宽度以适应4个项目
            spacing=10,  # 项目间距
            run_spacing=10,  # 行间距
            padding=10,
            child_aspect_ratio=4,  # 设置宽高比为4:1，使容器扁平化
        )
        
        try:
            print(f"[DEBUG] 获取分类列表, asset_type_id={self.current_asset_type_id}")
            categories = self.manager.get_categories(self.current_asset_type_id)
            print(f"[DEBUG] 获取到 {len(categories)} 个分类")
            
            for category in categories:
                category_data = category  # 创建一个局部变量来存储当前分类数据
                edit_button = ft.IconButton(
                    icon=ft.icons.EDIT,
                    tooltip="编辑",
                    on_click=lambda e, c=category_data: self._show_edit_category_form(c),  # 修改事件处理
                )
                delete_button = ft.IconButton(
                    icon=ft.icons.DELETE,
                    tooltip="删除",
                    on_click=lambda e, c=category_data: self._show_delete_category_form(c),  # 修改事件处理
                )
                print(f"[DEBUG] 创建分类项: {category['name']}")
                
                category_list.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Row(  # 将图标和文字放在一个 Row 中
                                    [
                                        ft.Icon(ft.icons.LOCAL_OFFER, color=self.icon_color),  # 使用主题相关的图标颜色
                                        ft.Container(  # 使用 Container 控制文字与图标的间距
                                            content=ft.Text(category["name"], size=14),
                                            padding=ft.padding.only(left=5),  # 只在左侧添加小间距
                                        ),
                                    ],
                                    spacing=0,  # 移除图标和文字之间的默认间距
                                ),
                                ft.Row(
                                    [edit_button, delete_button],
                                    spacing=0,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        border_radius=8,
                        padding=ft.padding.symmetric(horizontal=10, vertical=8),  # 减小水平内边距
                    )
                )
        except Exception as e:
            print(f"[ERROR] 加载分类列表失败: {str(e)}")
            category_list.controls.append(
                ft.Text(f"加载失败: {str(e)}", color=ft.colors.ERROR)
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("分类管理", size=16, weight=ft.FontWeight.BOLD),
                    ft.IconButton(
                        icon=ft.icons.ADD,
                        tooltip="添加分类",
                        on_click=lambda _: self._show_add_category_form(),
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=1),
                self.category_form,  # 添加表单容器
                category_list,
            ], spacing=10),
            padding=10,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=8,
            expand=True,
        )
    
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
        print("[DEBUG] 尝试显示添加分类表单")
        print(f"[DEBUG] 当前资产类型ID: {self.current_asset_type_id}")
        
        if not self.current_asset_type_id:
            print("[DEBUG] 未选择资产类型，显示错误提示")
            self.show_error("请先选择资产类型")
            return
        
        try:
            print("[DEBUG] 创建添加分类表单")
            name_field = ft.TextField(
                label="分类名称",
                expand=True,  # 使用 expand 而不是固定宽度
                autofocus=True
            )
            
            def handle_submit(e):
                print("[DEBUG] 提交添加分类表单")
                name = name_field.value.strip()
                print(f"[DEBUG] 分类名称: {name}")
                
                if name:
                    try:
                        self.manager.add_category(
                            self.current_asset_type_id,
                            name,
                            ""  # 空描述
                        )
                        print("[DEBUG] 分类添加成功")
                        self.category_form.visible = False
                        self._refresh_content()
                        self.show_success(f"已添加分类 '{name}'")
                        self.page.update()
                    except Exception as ex:
                        print(f"[ERROR] 添加分类失败: {str(ex)}")
                        self.show_error(str(ex))
            
            def handle_cancel(e):
                print("[DEBUG] 取消添加分类")
                self.category_form.visible = False
                self.page.update()
            
            # 更新表单内容
            self.category_form.content = ft.Row([
                name_field,
                ft.Container(
                    content=ft.Row([
                        ft.TextButton("取消", on_click=handle_cancel),
                        ft.FilledButton("添加", on_click=handle_submit),
                    ], spacing=10),  # 按钮之间的间距
                    padding=ft.padding.only(left=20),  # 与输入框的间距
                ),
            ])
            
            print("[DEBUG] 显示表单")
            self.category_form.visible = True
            self.page.update()
            
        except Exception as ex:
            print(f"[ERROR] 创建添加分类表单失败: {str(ex)}")
            self.show_error(f"创建表单失败: {str(ex)}")
    
    def _show_edit_category_form(self, category: Dict):
        """显示编辑分类表单"""
        print("[DEBUG] 显示编辑分类表单")
        print(f"[DEBUG] 编辑分类: {category}")
        
        try:
            name_field = ft.TextField(
                label="分类名称",
                expand=True,
                value=category["name"],
                autofocus=True
            )
            
            def handle_submit(e):
                print("[DEBUG] 提交编辑分类表单")
                name = name_field.value.strip()
                print(f"[DEBUG] 新分类名称: {name}")
                
                if name and name != category["name"]:
                    try:
                        self.manager.update_category(
                            category["id"],
                            name,
                            ""  # 空描述
                        )
                        print("[DEBUG] 分类更新成功")
                        self.category_form.visible = False
                        self._refresh_content()
                        self.show_success(f"已更新分类 '{name}'")
                        self.page.update()
                    except Exception as ex:
                        print(f"[ERROR] 更新分类失败: {str(ex)}")
                        self.show_error(str(ex))
            
            def handle_cancel(e):
                print("[DEBUG] 取消编辑分类")
                self.category_form.visible = False
                self.page.update()
            
            # 更新表单内容
            self.category_form.content = ft.Row([
                name_field,
                ft.Container(
                    content=ft.Row([
                        ft.TextButton("取消", on_click=handle_cancel),
                        ft.FilledButton("保存", on_click=handle_submit),
                    ], spacing=10),
                    padding=ft.padding.only(left=20),
                ),
            ])
            
            print("[DEBUG] 显示表单")
            self.category_form.visible = True
            self.page.update()
            
        except Exception as ex:
            print(f"[ERROR] 创建编辑分类表单失败: {str(ex)}")
            self.show_error(f"创建表单失败: {str(ex)}")
    
    def _show_delete_category_form(self, category: Dict):
        """显示删除分类表单"""
        print("[DEBUG] 显示删除分类表单")
        print(f"[DEBUG] 删除分类: {category}")
        
        try:
            def handle_submit(e):
                print("[DEBUG] 确认删除分类")
                try:
                    self.manager.delete_category(category["id"])
                    print("[DEBUG] 分类删除成功")
                    self.category_form.visible = False
                    self._refresh_content()
                    self.show_success(f"已删除分类 '{category['name']}'")
                    self.page.update()
                except Exception as ex:
                    print(f"[ERROR] 删除分类失败: {str(ex)}")
                    self.show_error(str(ex))
            
            def handle_cancel(e):
                print("[DEBUG] 取消删除分类")
                self.category_form.visible = False
                self.page.update()
            
            # 更新表单内容
            self.category_form.content = ft.Row([
                ft.Text(f"确定要删除分类 '{category['name']}' 吗？", color=ft.colors.ERROR),
                ft.Container(
                    content=ft.Row([
                        ft.TextButton("取消", on_click=handle_cancel),
                        ft.FilledButton(
                            "删除",
                            on_click=handle_submit,
                            style=ft.ButtonStyle(
                                color=ft.colors.ON_ERROR,
                                bgcolor=ft.colors.ERROR,
                            ),
                        ),
                    ], spacing=10),
                    padding=ft.padding.only(left=20),
                ),
            ])
            
            print("[DEBUG] 显示表单")
            self.category_form.visible = True
            self.page.update()
            
        except Exception as ex:
            print(f"[ERROR] 创建删除分类表单失败: {str(ex)}")
            self.show_error(f"创建表单失败: {str(ex)}")
    
    def _build_tag_editor(self):
        """构建标签编辑器"""
        tag_list = ft.GridView(
            expand=True,
            runs_count=4,  # 每行4个
            max_extent=300,  # 调整宽度以适应4个项目
            spacing=10,  # 项目间距
            run_spacing=10,  # 行间距
            padding=10,
            child_aspect_ratio=4,  # 设置宽高比为4:1，使容器扁平化
        )
        
        try:
            tags = self.manager.get_tags(self.current_asset_type_id)
            
            for tag in tags:
                tag_data = tag
                edit_button = ft.IconButton(
                    icon=ft.icons.EDIT,
                    tooltip="编辑",
                    on_click=lambda e, t=tag_data: self._show_edit_tag_form(t)
                )
                delete_button = ft.IconButton(
                    icon=ft.icons.DELETE,
                    tooltip="删除",
                    on_click=lambda e, t=tag_data: self._show_delete_tag_form(t)
                )
                
                tag_list.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Row(
                                    [
                                        ft.Icon(ft.icons.LOCAL_OFFER, color=self.icon_color),  # 使用主题颜色
                                        ft.Container(
                                            content=ft.Text(tag["name"], size=14),
                                            padding=ft.padding.only(left=5),
                                        ),
                                    ],
                                    spacing=0,
                                ),
                                ft.Row(
                                    [edit_button, delete_button],
                                    spacing=0,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        border_radius=8,
                        padding=ft.padding.symmetric(horizontal=10, vertical=8),
                    )
                )
        except Exception as e:
            print(f"[ERROR] 加载标签列表失败: {str(e)}")
            tag_list.controls.append(
                self._build_empty_hint("加载失败")
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("标签管理", size=16, weight=ft.FontWeight.BOLD),
                    ft.IconButton(
                        icon=ft.icons.ADD,
                        tooltip="添加标签",
                        on_click=lambda _: self._show_add_tag_form(),
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=1),
                self.tag_form,
                tag_list,
            ], spacing=10),
            padding=10,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=8,
            expand=True,
        )
    
    def _show_add_tag_form(self):
        """显示添加标签表单"""
        print("[DEBUG] 尝试显示添加标签表单")
        
        if not self.current_asset_type_id:
            print("[DEBUG] 未选择资产类型，显示错误提示")
            self.show_error("请先选择资产类型")
            return
        
        try:
            print("[DEBUG] 创建添加标签表单")
            name_field = ft.TextField(
                label="标签名称",
                expand=True,
                autofocus=True
            )
            
            def handle_submit(e):
                print("[DEBUG] 提交添加标签表单")
                name = name_field.value.strip()
                print(f"[DEBUG] 标签名称: {name}")
                
                if name:
                    try:
                        self.manager.add_tag(
                            self.current_asset_type_id,
                            name,
                            ""  # 空描述
                        )
                        print("[DEBUG] 标签添加成功")
                        self.tag_form.visible = False
                        self._refresh_content()
                        self.show_success(f"已添加标签 '{name}'")
                        self.page.update()
                    except Exception as ex:
                        print(f"[ERROR] 添加标签失败: {str(ex)}")
                        self.show_error(str(ex))
            
            def handle_cancel(e):
                print("[DEBUG] 取消添加标签")
                self.tag_form.visible = False
                self.page.update()
            
            # 更新表单内容
            self.tag_form.content = ft.Row([
                name_field,
                ft.Container(
                    content=ft.Row([
                        ft.TextButton("取消", on_click=handle_cancel),
                        ft.FilledButton("添加", on_click=handle_submit),
                    ], spacing=10),
                    padding=ft.padding.only(left=20),
                ),
            ])
            
            print("[DEBUG] 显示表单")
            self.tag_form.visible = True
            self.page.update()
            
        except Exception as ex:
            print(f"[ERROR] 创建添加标签表单失败: {str(ex)}")
            self.show_error(f"创建表单失败: {str(ex)}")
    
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
                    self._refresh_content()
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
                self._refresh_content()
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
        color_list = ft.GridView(
            expand=True,
            runs_count=4,  # 每行4个
            max_extent=300,  # 调整宽度以适应4个项目
            spacing=10,  # 项目间距
            run_spacing=10,  # 行间距
            padding=10,
            child_aspect_ratio=4,  # 设置宽高比为4:1，使容器扁平化
        )
        
        try:
            colors = self.manager.get_color_marks(self.current_asset_type_id)
            
            for color in colors:
                color_data = color
                edit_button = ft.IconButton(
                    icon=ft.icons.EDIT,
                    tooltip="编辑",
                    on_click=lambda e, c=color_data: self._show_edit_color_form(c)
                )
                delete_button = ft.IconButton(
                    icon=ft.icons.DELETE,
                    tooltip="删除",
                    on_click=lambda e, c=color_data: self._show_delete_color_form(c)
                )
                
                color_list.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Row(
                                    [
                                        ft.Icon(ft.icons.LOCAL_OFFER, color=self.icon_color),  # 使用主题颜色
                                        ft.Container(
                                            content=ft.Text(color["name"], size=14),
                                            padding=ft.padding.only(left=5),
                                        ),
                                    ],
                                    spacing=0,
                                ),
                                ft.Row(
                                    [edit_button, delete_button],
                                    spacing=0,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        border_radius=8,
                        padding=ft.padding.symmetric(horizontal=10, vertical=8),
                    )
                )
        except Exception as e:
            print(f"[ERROR] 加载颜色标记列表失败: {str(e)}")
            color_list.controls.append(
                self._build_empty_hint("加载失败")
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("颜色标记管理", size=16, weight=ft.FontWeight.BOLD),
                    ft.IconButton(
                        icon=ft.icons.ADD,
                        tooltip="添加颜色标记",
                        on_click=lambda _: self._show_add_color_form(),
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=1),
                self.color_form,
                color_list,
            ], spacing=10),
            padding=10,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=8,
            expand=True,
        )
    
    def _show_add_color_form(self):
        """显示添加颜色标记表单"""
        print("[DEBUG] 尝试显示添加颜色标记表单")
        
        if not self.current_asset_type_id:
            print("[DEBUG] 未选择资产类型，显示错误提示")
            self.show_error("请先选择资产类型")
            return
        
        try:
            print("[DEBUG] 创建添加颜色标记表单")
            name_field = ft.TextField(
                label="颜色标记名称",
                expand=True,
                autofocus=True
            )
            
            def handle_submit(e):
                print("[DEBUG] 提交添加颜色标记表单")
                name = name_field.value.strip()
                print(f"[DEBUG] 颜色标记名称: {name}")
                
                if name:
                    try:
                        self.manager.add_color_mark(
                            self.current_asset_type_id,
                            name,
                            ft.colors.BLUE  # 使用默认颜色
                        )
                        print("[DEBUG] 颜色标记添加成功")
                        self.color_form.visible = False
                        self._refresh_content()
                        self.show_success(f"已添加颜色标记 '{name}'")
                        self.page.update()
                    except Exception as ex:
                        print(f"[ERROR] 添加颜色标记失败: {str(ex)}")
                        self.show_error(str(ex))
            
            def handle_cancel(e):
                print("[DEBUG] 取消添加颜色标记")
                self.color_form.visible = False
                self.page.update()
            
            # 更新表单内容
            self.color_form.content = ft.Row([
                name_field,
                ft.Container(
                    content=ft.Row([
                        ft.TextButton("取消", on_click=handle_cancel),
                        ft.FilledButton("添加", on_click=handle_submit),
                    ], spacing=10),
                    padding=ft.padding.only(left=20),
                ),
            ])
            
            print("[DEBUG] 显示表单")
            self.color_form.visible = True
            self.page.update()
            
        except Exception as ex:
            print(f"[ERROR] 创建添加颜色标记表单失败: {str(ex)}")
            self.show_error(f"创建表单失败: {str(ex)}")
    
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
                    self._refresh_content()
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
                self._refresh_content()
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

    def _show_settings_form(self):
        """显示设置表单"""
        print("[DEBUG] 显示设置表单")
        
        if not self.current_asset_type_id:
            print("[DEBUG] 未选择资产类型")
            self.show_error("请先选择资产类型")
            return
        
        try:
            # 获取当前资产类型
            asset_type = next(
                (t for t in self.asset_types if t["id"] == self.current_asset_type_id),
                None
            )
            if not asset_type:
                print(f"[ERROR] 找不到资产类型: {self.current_asset_type_id}")
                return
            
            # 获取评分设置
            rating_settings = self.manager.get_rating_settings(self.current_asset_type_id)
            if not rating_settings:
                rating_settings = {"max_rating": 5, "allow_half_rating": True}
            
            # 创建表单字段
            name_field = ft.TextField(
                label="显示名称",
                value=asset_type["display_name"],
                width=300,
            )
            
            max_rating_field = ft.Slider(
                min=1,
                max=10,
                divisions=9,
                label="最大星级数: {value}",
                value=rating_settings["max_rating"],
            )
            
            half_rating_switch = ft.Switch(
                label="允许半星评分",
                value=rating_settings["allow_half_rating"],
            )
            
            def handle_submit(e):
                try:
                    # 更新资产类型显示名称
                    new_name = name_field.value.strip()
                    if new_name and new_name != asset_type["display_name"]:
                        self.manager.update_asset_type_name(
                            self.current_asset_type_id,
                            new_name
                        )
                    
                    # 更新评分设置
                    self.manager.update_rating_settings(
                        self.current_asset_type_id,
                        int(max_rating_field.value),
                        half_rating_switch.value
                    )
                    
                    self.show_success("设置已更新")
                    dialog.open = False
                    self._refresh_all()  # 使用 _refresh_all 而不是 _refresh_content
                    self.page.update()
                    
                except Exception as ex:
                    self.show_error(str(ex))
            
            def handle_cancel(e):
                dialog.open = False
                self.page.update()
            
            # 使用 AlertDialog 而不是 Container
            dialog = ft.AlertDialog(
                title=ft.Text("资产类型设置"),
                content=ft.Column([
                    ft.Text("基本设置", size=16, weight=ft.FontWeight.BOLD),
                    name_field,
                    ft.Divider(height=1),
                    ft.Text("评分设置", size=16, weight=ft.FontWeight.BOLD),
                    max_rating_field,
                    half_rating_switch,
                ], tight=True, spacing=20),
                actions=[
                    ft.TextButton("取消", on_click=handle_cancel),
                    ft.FilledButton("保存", on_click=handle_submit),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
        
        except Exception as ex:
            print(f"[ERROR] 显示设置表单失败: {str(ex)}")
            self.show_error(str(ex))

    def _refresh_all(self):
        """刷新所有数据和界面"""
        print("[DEBUG] 刷新所有数据")
        try:
            # 重新获取资产类型列表
            self.asset_types = self.manager.get_asset_types()
            
            # 更新下拉框选项
            if self.asset_type_dropdown:
                self.asset_type_dropdown.options = [
                    ft.dropdown.Option(
                        key=str(t["id"]),
                        text=t["display_name"]
                    ) for t in self.asset_types
                ]
            
            # 刷新内容
            self._refresh_content()
            
        except Exception as ex:
            print(f"[ERROR] 刷新所有数据失败: {str(ex)}")
            self.show_error(f"刷新失败: {str(ex)}") 