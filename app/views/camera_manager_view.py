import flet as ft
from typing import Optional
from app.utils.camera_manager import CameraManager
import os

class CameraManagerView:
    def __init__(self, page: ft.Page, settings: dict):
        self.page = page
        self.settings = settings
        self.current_brand_id: Optional[int] = None
        
        # 初始化表单容器
        self.brand_form = ft.Container(
            visible=False,
            content=None,
            padding=10,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=8,
            margin=ft.margin.only(bottom=10),
        )
        
        self.model_form = ft.Container(
            visible=False,
            content=None,
            padding=10,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=8,
            margin=ft.margin.only(bottom=10),
        )
        
        # 初始化型号列表容器
        self.model_container = ft.Container(
            expand=True,
            content=None
        )
        
        # 下拉框和按钮引用
        self.brand_dropdown = ft.Ref()
        self.brand_menu_button = ft.Ref()
        self.brand_delete_button = ft.Ref()
        
        try:
            # 从 settings 中获取数据库路径
            db_dir = settings.get("database_path", "")
            if not db_dir:
                raise ValueError("数据库路径未设置，请先在路径设置中配置")
            
            # 构建数据库文件完整路径
            db_path = os.path.join(db_dir, "app.db")
            
            # 确保数据库目录存在
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            # 初始化相机管理器
            self.manager = CameraManager(db_path)
            
        except Exception as e:
            self.show_error(f"初始化失败: {str(e)}")
            self.manager = None
        
    def build(self):
        """构建界面"""
        return ft.Container(
            content=ft.Column([
                # 顶部栏
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            on_click=lambda _: self.page.go("/settings"),
                            tooltip="返回设置",
                        ),
                        ft.Text("相机管理", size=20, weight=ft.FontWeight.BOLD),
                    ]),
                    padding=10,
                ),
                
                # 主要内容区域
                ft.Container(
                    content=ft.Column([
                        # 品牌区域
                        self._build_brand_section(),
                        
                        # 型号区域
                        self._build_model_section(),
                    ], 
                    spacing=20),  # 增加上下间距
                    padding=20,  # 增加四周间距
                    expand=True,
                ),
            ]),
            expand=True,
        )
    
    def _build_brand_section(self):
        """构建品牌区域"""
        
        # 初始化下拉框选项
        try:
            brands = self.manager.get_all_brands()
            dropdown_options = [
                ft.dropdown.Option(
                    key=str(brand["id"]),
                    text=brand["name"]
                ) for brand in brands
            ]
        except Exception as e:
            print(f"[ERROR] 加载品牌列表失败: {str(e)}")
            dropdown_options = []
        
        # 品牌下拉选择器和操作按钮行
        brand_row = ft.Row([
            ft.Dropdown(
                label="选择品牌（重命名后请重选品牌）：",
                width=400,  # 固定宽度
                options=dropdown_options,  # 设置选项
                value=str(self.current_brand_id) if self.current_brand_id else None,  # 设置当前值
                on_change=self._handle_brand_change,
                ref=self.brand_dropdown,
            ),
            ft.IconButton(
                icon=ft.icons.EDIT,
                tooltip="重命名品牌",
                visible=bool(self.current_brand_id),  # 根据是否有选中品牌设置初始可见性
                ref=self.brand_menu_button,
                on_click=lambda _: self._show_rename_brand_form(),
            ),
            ft.IconButton(
                icon=ft.icons.DELETE,
                tooltip="删除品牌",
                visible=bool(self.current_brand_id),  # 根据是否有选中品牌设置初始可见性
                ref=self.brand_delete_button,
                on_click=lambda _: self._show_delete_brand_form(),
            ),
        ], spacing=0)  # 减小按钮间距

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("品牌管理", size=16, weight=ft.FontWeight.BOLD),
                    ft.IconButton(
                        icon=ft.icons.ADD,
                        tooltip="添加品牌",
                        on_click=lambda _: self._show_add_brand_form(),
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=1),
                brand_row,  # 品牌选择和操作行
                self.brand_form,  # 品牌表单
            ], spacing=10),  # 增加垂直间距
            padding=10,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=8,
        )
    
    def _handle_brand_change(self, e):
        """处理品牌选择变化"""
        if e.data:
            self.current_brand_id = int(e.data)
            # 显示操作按钮
            self.brand_menu_button.current.visible = True
            self.brand_delete_button.current.visible = True
            # 刷新型号列表
            self._refresh_model_list()  # 使用新方法刷新型号列表
        else:
            self.current_brand_id = None
            # 隐藏操作按钮
            self.brand_menu_button.current.visible = False
            self.brand_delete_button.current.visible = False
            self._refresh_model_list()  # 同样刷新型号列表
        
        self.page.update()
    
    def _show_add_brand_form(self):
        """显示添加品牌表单"""
        name_field = ft.TextField(
            label="品牌名称",
            width=300,
            autofocus=True
        )
        
        def handle_submit(e):
            name = name_field.value.strip()
            if name:
                try:
                    brand_id = self.manager.add_brand(name)
                    self.brand_form.visible = False
                    self.current_brand_id = brand_id
                    self._refresh_brand_dropdown()  # 刷新下拉框
                    self._refresh_model_list()  # 刷新型号列表
                    self.show_success(f"已添加品牌 '{name}'")
                except Exception as ex:
                    print(f"[ERROR] 添加品牌失败: {str(ex)}")
                    self.show_error(str(ex))
        
        def handle_cancel(e):
            self.brand_form.visible = False
            self.page.update()
        
        self.brand_form.content = ft.Column([
            ft.Text("添加品牌", size=16, weight=ft.FontWeight.BOLD),
            name_field,
            ft.Row([
                ft.TextButton(
                    "取消",
                    on_click=handle_cancel
                ),
                ft.FilledButton(
                    "添加",
                    on_click=handle_submit
                ),
            ], alignment=ft.MainAxisAlignment.END),
        ], tight=True)
        
        self.brand_form.visible = True
        self.page.update()
    
    def _show_rename_brand_form(self):
        """显示重命名品牌表单"""
        if not self.current_brand_id:
            return
        
        # 获取当前品牌信息
        current_brand = next(
            (b for b in self.manager.get_all_brands() 
             if b["id"] == self.current_brand_id), 
            None
        )
        if not current_brand:
            return

        name_field = ft.TextField(
            label="品牌名称",
            value=current_brand["name"],
            width=300,
            autofocus=True
        )
        
        def handle_submit(e):
            name = name_field.value.strip()
            if name and name != current_brand["name"]:
                try:
                    self.manager.rename_brand(self.current_brand_id, name)
                    self.brand_form.visible = False
                    self._refresh_brand_dropdown()  # 刷新下拉框
                    self.show_success(f"已重命名为 '{name}'")
                except Exception as ex:
                    self.show_error(str(ex))
        
        def handle_cancel(e):
            self.brand_form.visible = False
            self.page.update()
        
        self.brand_form.content = ft.Column([
            ft.Text("重命名品牌", size=16, weight=ft.FontWeight.BOLD),
            name_field,
            ft.Row([
                ft.TextButton(
                    "取消",
                    on_click=handle_cancel
                ),
                ft.FilledButton(
                    "保存",
                    on_click=handle_submit
                ),
            ], alignment=ft.MainAxisAlignment.END),
        ], tight=True)
        
        self.brand_form.visible = True
        self.page.update()
    
    def _show_delete_brand_form(self):
        """显示删除品牌表单"""
        if not self.current_brand_id:
            return
        
        # 获取当前品牌信息
        current_brand = next(
            (b for b in self.manager.get_all_brands() 
             if b["id"] == self.current_brand_id), 
            None
        )
        if not current_brand:
            return

        def handle_submit(e):
            try:
                self.manager.delete_brand(self.current_brand_id)
                self.brand_form.visible = False
                self.current_brand_id = None
                self._refresh_brand_dropdown()  # 刷新下拉框
                self._refresh_model_list()  # 清空型号列表
                self.show_success(f"已删除品牌 '{current_brand['name']}'")
            except Exception as ex:
                self.show_error(str(ex))
        
        def handle_cancel(e):
            self.brand_form.visible = False
            self.page.update()
        
        self.brand_form.content = ft.Column([
            ft.Text("删除品牌", size=16, color=ft.colors.ERROR),
            ft.Text(
                f"确定要删除品牌 '{current_brand['name']}' 吗？\n"
                "删除后将同时删除该品牌下的所有型号！"
            ),
            ft.Row([
                ft.TextButton(
                    "取消",
                    on_click=handle_cancel
                ),
                ft.FilledButton(
                    "删除",
                    on_click=handle_submit,
                    style=ft.ButtonStyle(
                        color=ft.colors.ON_ERROR,
                        bgcolor=ft.colors.ERROR,
                    ),
                ),
            ], alignment=ft.MainAxisAlignment.END),
        ], tight=True)
        
        self.brand_form.visible = False  # 先隐藏
        self.brand_form.visible = True   # 再显示，确保更新
        self.page.update()
    
    def _load_brands(self):
        """加载品牌列表到下拉框"""
        try:
            brands = self.manager.get_all_brands()
            # 更新下拉选项
            self.brand_dropdown.current.options = [
                ft.dropdown.Option(
                    key=str(brand["id"]),
                    text=brand["name"]
                ) for brand in brands
            ]
            # 如果当前选中的品牌被删除，清除选择
            if self.current_brand_id:
                if not any(b["id"] == self.current_brand_id for b in brands):
                    self.current_brand_id = None
                    self.brand_dropdown.current.value = None
                    self.brand_menu_button.current.visible = False
                    self.brand_delete_button.current.visible = False
            
            self.page.update()
        except Exception as e:
            print(f"[ERROR] 加载品牌失败: {str(e)}")
            self.show_error(f"加载品牌失败: {str(e)}")
    
    def _refresh_model_list(self):
        """刷新型号列表"""
        
        if not self.current_brand_id:
            self.model_container.content = ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(
                                    ft.icons.CAMERA_ALT,
                                    size=64,
                                    color=ft.colors.GREY_400,
                                ),
                                ft.Text(
                                    "请选择品牌",
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
                ],
                expand=True
            )
        else:
            try:
                models = self.manager.get_models_by_brand(self.current_brand_id)
                
                if not models:
                    self.model_container.content = ft.Column(
                        [
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Icon(
                                            ft.icons.CAMERA_ALT,
                                            size=64,
                                            color=ft.colors.GREY_400,
                                        ),
                                        ft.Text(
                                            "暂无型号",
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
                        ],
                        expand=True
                    )
                else:
                    model_rows = []
                    current_row = []
                    
                    for model in models:
                        model_item = ft.Container(
                            content=ft.Row(
                                [
                                    ft.Icon(
                                        ft.icons.CAMERA_ALT,
                                        color=ft.colors.BLUE_GREY_400,
                                        size=20,
                                    ),
                                    ft.Text(
                                        model["name"],
                                        size=14,
                                        weight=ft.FontWeight.NORMAL,
                                        expand=True,
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.EDIT,
                                        icon_size=18,
                                        tooltip="编辑型号",
                                        on_click=lambda e, m=model: self._show_edit_model_form(m)
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        icon_size=18,
                                        tooltip="删除型号",
                                        on_click=lambda e, m=model: self._show_delete_model_form(m)
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.START,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=10,
                            ),
                            padding=ft.padding.only(left=15, right=5, top=8, bottom=8),
                            bgcolor=ft.colors.SURFACE_VARIANT,
                            border_radius=8,
                            expand=True,  # 让每个项目都能填充可用空间
                            width=300,  # 固定每个型号项的宽度，确保均匀分布
                        )
                        
                        current_row.append(model_item)
                        
                        # 每3个型号为一行
                        if len(current_row) == 3:
                            model_rows.append(
                                ft.Row(
                                    current_row,
                                    alignment=ft.MainAxisAlignment.START,
                                    spacing=15,  # 增加列间距
                                )
                            )
                            current_row = []
                    
                    # 处理最后一行不足3个的情况
                    if current_row:
                        # 添加空白容器填充最后一行
                        while len(current_row) < 3:
                            current_row.append(
                                ft.Container(width=300)  # 空白占位容器
                            )
                        model_rows.append(
                            ft.Row(
                                current_row,
                                alignment=ft.MainAxisAlignment.START,
                                spacing=15,
                            )
                        )
                    
                    self.model_container.content = ft.Column(
                        model_rows,
                        scroll=ft.ScrollMode.AUTO,
                        spacing=10,
                        expand=True,
                        horizontal_alignment=ft.CrossAxisAlignment.START,  # 确保左对齐
                    )
                
                self.page.update()
                
            except Exception as e:
                print(f"[ERROR] 加载型号失败: {str(e)}")
                print(f"[ERROR] 错误类型: {type(e)}")
                import traceback
                print(f"[ERROR] 堆栈跟踪:\n{traceback.format_exc()}")
                self.show_error(f"加载型号失败: {str(e)}")
    
    def _build_model_section(self):
        """构建型号区域"""
        
        # 初始加载型号列表
        self._refresh_model_list()
        
        # 型号区域
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("型号管理", size=16, weight=ft.FontWeight.BOLD),
                    ft.IconButton(
                        icon=ft.icons.ADD,
                        tooltip="添加型号",
                        on_click=lambda _: self._show_add_model_form(),
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=1),
                self.model_form,
                self.model_container,
            ], spacing=10, expand=True),
            padding=10,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=8,
            expand=True,
        )
    
    def _show_add_model_form(self):
        """显示添加型号表单"""
        if not self.current_brand_id:
            self.show_error("请先选择品牌")
            return
        
        name_field = ft.TextField(
            label="型号名称",
            width=300,
            autofocus=True
        )
        
        def handle_submit(e):
            name = name_field.value.strip()
            if name:
                try:
                    self.manager.add_model(self.current_brand_id, name)
                    self.model_form.visible = False
                    self._refresh_model_list()  # 刷新型号列表
                    self.show_success(f"已添加型号 '{name}'")
                except Exception as ex:
                    self.show_error(str(ex))
        
        def handle_cancel(e):
            self.model_form.visible = False
            self.page.update()
        
        self.model_form.content = ft.Column([
            ft.Text("添加型号", size=16, weight=ft.FontWeight.BOLD),
            name_field,
            ft.Row([
                ft.TextButton(
                    "取消",
                    on_click=handle_cancel
                ),
                ft.FilledButton(
                    "添加",
                    on_click=handle_submit
                ),
            ], alignment=ft.MainAxisAlignment.END),
        ], tight=True)
        
        self.model_form.visible = True
        self.page.update()
    
    def _show_edit_model_form(self, model):
        """显示编辑型号表单"""
        name_field = ft.TextField(
            label="型号名称",
            value=model["name"],
            width=300,
            autofocus=True
        )
        
        def handle_submit(e):
            name = name_field.value.strip()
            if name and name != model["name"]:
                try:
                    self.manager.update_model(model["id"], name)
                    self.model_form.visible = False
                    self._refresh_model_list()  # 刷新型号列表
                    self.show_success(f"已更新型号名称为 '{name}'")
                except Exception as ex:
                    self.show_error(str(ex))
        
        def handle_cancel(e):
            self.model_form.visible = False
            self.page.update()
        
        self.model_form.content = ft.Column([
            ft.Text("编辑型号", size=16, weight=ft.FontWeight.BOLD),
            name_field,
            ft.Row([
                ft.TextButton(
                    "取消",
                    on_click=handle_cancel
                ),
                ft.FilledButton(
                    "保存",
                    on_click=handle_submit
                ),
            ], alignment=ft.MainAxisAlignment.END),
        ], tight=True)
        
        self.model_form.visible = True
        self.page.update()
    
    def _show_delete_model_form(self, model):
        """显示删除型号表单"""
        def handle_submit(e):
            try:
                self.manager.delete_model(model["id"])
                self.model_form.visible = False
                self._refresh_model_list()  # 刷新型号列表
                self.show_success(f"已删除型号 '{model['name']}'")
            except Exception as ex:
                self.show_error(str(ex))
        
        def handle_cancel(e):
            self.model_form.visible = False
            self.page.update()
        
        self.model_form.content = ft.Column([
            ft.Text("删除型号", size=16, color=ft.colors.ERROR),
            ft.Text(f"确定要删除型号 '{model['name']}' 吗？"),
            ft.Row([
                ft.TextButton(
                    "取消",
                    on_click=handle_cancel
                ),
                ft.FilledButton(
                    "删除",
                    on_click=handle_submit,
                    style=ft.ButtonStyle(
                        color=ft.colors.ON_ERROR,
                        bgcolor=ft.colors.ERROR,
                    ),
                ),
            ], alignment=ft.MainAxisAlignment.END),
        ], tight=True)
        
        self.model_form.visible = True
        self.page.update()
    
    def refresh(self):
        """刷新界面"""
        self.page.update()
    
    def show_error(self, message: str):
        """显示错误提示"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.colors.ERROR,
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def show_success(self, message: str):
        """显示成功提示"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.colors.GREEN,
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def _refresh_brand_dropdown(self):
        """刷新品牌下拉框"""
        try:
            brands = self.manager.get_all_brands()
            
            # 更新下拉选项
            self.brand_dropdown.current.options = [
                ft.dropdown.Option(
                    key=str(brand["id"]),
                    text=brand["name"]
                ) for brand in brands
            ]
            
            # 设置当前选中值
            if self.current_brand_id:
                self.brand_dropdown.current.value = str(self.current_brand_id)
                self.brand_menu_button.current.visible = True
                self.brand_delete_button.current.visible = True
            else:
                self.brand_dropdown.current.value = None
                self.brand_menu_button.current.visible = False
                self.brand_delete_button.current.visible = False
            
            self.page.update()
            
        except Exception as e:
            print(f"[ERROR] 刷新下拉框失败: {str(e)}")
            self.show_error(f"刷新下拉框失败: {str(e)}") 