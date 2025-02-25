import flet as ft
import sqlite3
from datetime import datetime
import os
from typing import Optional, List, Dict
import pandas as pd
from pathlib import Path
import platform
from app.utils.project_manager import ProjectManager

class HistoryView:
    def __init__(self, page: ft.Page, settings: dict):
        self.page = page
        self.manager = None
        
        # 添加析构标记
        self._destroyed = False
        
        try:
            # 从 settings 中获取数据库路径
            db_dir = settings.get("database_path", "")
            if not db_dir:
                db_dir = os.path.join(settings.get("project_path", ""), "database")
            
            if not db_dir:
                raise ValueError("数据库路径未设置")
            
            # 构建数据库文件完整路径
            db_path = os.path.join(db_dir, "app.db")
            
            # 确保数据库目录存在
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            # 初始化项目管理器
            self.manager = ProjectManager(db_path)
            print(f"[DEBUG] 项目管理器初始化成功: {db_path}")
            
        except Exception as e:
            print(f"[ERROR] 初始化项目管理器失败: {str(e)}")
            self.show_error(f"初始化失败: {str(e)}")
        
        # 自动保存定时器
        self.auto_save_timer = None
        self.last_save_time = datetime.now()
        
        # 表格引用
        self.data_table = None
        
        # 过滤器状态
        self.filters = {
            "disk_id": None,
            "backup_status": None, 
            "date_from": None,
            "date_to": None,
            "tags": [],
            "search_text": ""
        }
        
        # 选中的项目
        self.selected_items = set()
        
        # 创建 FilePicker 并添加到页面
        self.import_picker = ft.FilePicker(
            on_result=self._handle_import_result
        )
        self.export_picker = ft.FilePicker(
            on_result=self._handle_export_result
        )
        self.page.overlay.extend([self.import_picker, self.export_picker])
        
        # 添加页面关闭事件处理
        self.page.on_view_pop = self._on_view_pop
        
        # 添加窗口关闭事件处理
        def on_window_event(e):
            if e.data == "close":
                self._cleanup()
        
        self.page.window_prevent_close = True
        self.page.on_window_event = on_window_event
        
        # 分页相关
        self.page_size = 20  # 每页显示数量设置为10
        self.current_page = 1  # 当前页码
        
        # 同时修改分页控件的初始化
        self.pagination_row = ft.Row(
            [ft.Text("")],  # 初始为空的分页控件
            alignment=ft.MainAxisAlignment.CENTER,
        )
        
    def build(self):
        """构建界面"""
        # 顶部栏
        toolbar = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Text("历史工程", size=20, weight=ft.FontWeight.BOLD),
                        alignment=ft.alignment.center_left,
                        padding=ft.padding.only(left=10),  # 添加左边距
                    ),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.icons.ADD,
                                    tooltip="新增",
                                    on_click=self._show_add_dialog
                                ),
                                ft.IconButton(
                                    icon=ft.icons.UPLOAD_FILE,
                                    tooltip="导入Excel",
                                    on_click=self._import_excel
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DOWNLOAD,
                                    tooltip="导出Excel",
                                    on_click=self._export_excel
                                ),
                                ft.IconButton(
                                    icon=ft.icons.REFRESH,
                                    tooltip="刷新",
                                    on_click=self.refresh_data
                                ),
                                ft.IconButton(
                                    icon=ft.icons.SETTINGS,
                                    tooltip="设置",
                                    on_click=self._show_settings
                                ),
                            ],
                            spacing=0,
                            alignment=ft.MainAxisAlignment.END,  # 按钮靠右对齐
                        ),
                        alignment=ft.alignment.center_right,
                        padding=ft.padding.only(right=10),  # 添加右边距
                        expand=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=10,
            border_radius=8,
        )

        # 过滤工具栏
        filter_bar = ft.Container(
            content=ft.Row(
                [
                    # 左侧控件组
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Dropdown(
                                    label="磁盘编号",
                                    options=[
                                        ft.dropdown.Option("全部"),
                                        *[ft.dropdown.Option(str(i)) for i in range(1, 11)]
                                    ],
                                    width=150,
                                    on_change=self._handle_filter_change,
                                ),
                                ft.Dropdown(
                                    label="备份状态",
                                    options=[
                                        ft.dropdown.Option("全部"),
                                        ft.dropdown.Option("已备份"),
                                        ft.dropdown.Option("未备份"),
                                    ],
                                    width=150,
                                    on_change=self._handle_filter_change,
                                ),
                                ft.Container(
                                    content=ft.Column([
                                        ft.TextField(
                                            label="开始日期",
                                            value=self.filters.get("date_from", ""),
                                            on_change=lambda e: self._handle_date_input(e, "start"),
                                            width=150,
                                        ),
                                    ]),
                                    width=150,
                                ),
                                ft.Container(
                                    content=ft.Column([
                                        ft.TextField(
                                            label="结束日期",
                                            value=self.filters.get("date_to", ""),
                                            on_change=lambda e: self._handle_date_input(e, "end"),
                                            width=150,
                                        ),
                                    ]),
                                    width=150,
                                ),
                            ],
                            spacing=20,
                        ),
                    ),
                    # 右侧搜索框
                    ft.Container(
                        content=ft.TextField(
                            label="搜索",
                            prefix_icon=ft.icons.SEARCH,
                            on_change=self._handle_search,
                            width=200,  # 设置固定宽度
                            border_radius=20,
                        ),
                        alignment=ft.alignment.center_right,
                        expand=True,  # 占用剩余空间，使搜索框靠右
                    ),
                ],
                spacing=20,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,  # 两端对齐
            ),
            padding=ft.padding.only(left=10, right=10, top=7, bottom=7),
            margin=ft.margin.only(left=18, right=18),
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=8,
        )

        # 数据表格
        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("磁盘号")),
                ft.DataColumn(ft.Text("日期")),
                ft.DataColumn(ft.Text("项目名称")),
                ft.DataColumn(ft.Text("备份")),
                ft.DataColumn(ft.Text("操作")),
            ],
            rows=[],
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=8,
            vertical_lines=ft.border.BorderSide(1, ft.colors.OUTLINE),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.OUTLINE),
            sort_ascending=True, 
            sort_column_index=0,
            heading_row_height=40,
            data_row_min_height=40,
            width=1180, 
        )

        # 初始加载数据
        self.refresh_data()

        return ft.Column(
            [
                toolbar,
                filter_bar,
                ft.Container(
                    content=ft.Column(
                        [
                            self.data_table,
                            self.pagination_row,  # 添加分页控件
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                        scroll=ft.ScrollMode.AUTO
                    ),
                    expand=True,
                    padding=20,  # 添加内边距
                ),
            ],
            expand=True,
        )

    def refresh_data(self, e=None):
        """刷新数据显示"""
        try:
            # 获取总数据
            all_projects = self.manager.get_projects(self.filters)
            
            # 按照磁盘编号排序
            all_projects.sort(key=lambda x: int(x['disk_id']) if x['disk_id'].isdigit() else float('inf'))
            
            # 计算总页数
            total_pages = (len(all_projects) + self.page_size - 1) // self.page_size
            
            # 分页处理
            start_idx = (self.current_page - 1) * self.page_size
            end_idx = start_idx + self.page_size
            
            current_projects = all_projects[start_idx:end_idx]
            
            # 更新表格数据
            rows = []
            for project in current_projects:
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(project['disk_id'])),
                        ft.DataCell(ft.Text(project['project_date'])),
                        ft.DataCell(ft.Text(project['project_name'])),
                        ft.DataCell(ft.Icon(
                            ft.icons.CHECK_CIRCLE if project['backup_status'] else ft.icons.CANCEL,
                            color=ft.colors.GREEN if project['backup_status'] else ft.colors.RED,
                            size=20,
                        )),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.icons.EDIT,
                                        tooltip="编辑",
                                        data=project,
                                        on_click=lambda e: self._show_edit_dialog(e.control.data),
                                        icon_size=20,
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        tooltip="删除",
                                        data=project,
                                        on_click=lambda e: self._delete_project(e.control.data['id']),
                                        icon_size=20,
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.FOLDER_OPEN,
                                        tooltip="打开路径",
                                        data=project,
                                        on_click=lambda e: self._open_project_path(e.control.data),
                                        icon_size=20,
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.INFO,
                                        tooltip="详情",
                                        data=project,
                                        on_click=lambda e: self._show_detail_dialog(e.control.data),
                                        icon_size=20,
                                    ),
                                ],
                                spacing=5,
                            )
                        ),
                    ]
                )
                rows.append(row)

            self.data_table.rows = rows
            self._update_pagination(total_pages)  # 更新分页控件
            
            self.page.update()
        except Exception as e:
            print(f"[ERROR] 刷新数据显示失败: {str(e)}")
            self.show_error(f"刷新数据显示失败: {str(e)}")

    def _handle_row_select(self, project):
        """处理行选择"""
        if project:
            self._show_detail_dialog(project)

    def _show_add_dialog(self, e=None):
        """显示新增项目对话框"""
        try:
            # 创建对话框内容
            disk_id = ft.TextField(
                label="磁盘编号",
                value="",
                keyboard_type=ft.KeyboardType.NUMBER,
            )
            project_date = ft.TextField(
                label="项目时间",
                value=datetime.now().strftime("%Y%m%d"),
            )
            project_name = ft.TextField(
                label="项目名称",
                value="",
                hint_text="必填项",
            )
            backup_status = ft.Checkbox(label="已备份")
            notes = ft.TextField(
                label="项目备注",
                value="",
                multiline=True,
                min_lines=2,
                max_lines=5,
            )
            project_path = ft.TextField(
                label="项目路径",
                value="",
                suffix=ft.IconButton(
                    icon=ft.icons.FOLDER_OPEN,
                    on_click=lambda _: self._pick_folder(project_path),
                ),
            )
            filename = ft.TextField(
                label="文件名称",
                value="",
            )

            def save_project(_):
                try:
                    if not project_name.value.strip():
                        self.show_error("项目名称不能为空")
                        return
                    
                    self.manager.add_project({
                        'disk_id': disk_id.value or '0',
                        'project_date': project_date.value,
                        'project_name': project_name.value,
                        'backup_status': 1 if backup_status.value else 0,
                        'notes': notes.value,
                        'project_path': project_path.value,
                        'filename': filename.value,
                    })
                    add_dlg.open = False  # 关闭对话框
                    self.refresh_data()  # 刷新数据
                    self.show_success("添加成功")
                except Exception as e:
                    self.show_error(f"添加失败: {str(e)}")

            # 创建新增项目对话框
            add_dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("新增项目"),
                content=ft.Column([
                    disk_id,
                    project_date,
                    project_name,
                    backup_status,
                    notes,
                    project_path,
                    filename,
                ], scroll=ft.ScrollMode.AUTO, spacing=10),
                actions=[
                    ft.TextButton("取消", on_click=lambda e: self.page.close(add_dlg)),  # 使用 page.close
                    ft.FilledButton("保存", on_click=save_project),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                content_padding=ft.padding.all(20),  # 添加内容填充
                actions_padding=ft.padding.all(10),  # 添加操作按钮填充
                inset_padding=ft.padding.all(20),  # 添加对话框边距
            )
            
            self.page.dialog = add_dlg  # 将对话框添加到页面
            self.page.open(add_dlg)  # 使用 open 方法打开对话框
        except Exception as e:
            print(f"[ERROR] 显示新增对话框失败: {str(e)}")
            self.show_error(str(e))

    def _pick_folder(self, text_field: ft.TextField):
        """选择文件夹"""
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            
            folder_path = filedialog.askdirectory()
            if folder_path:
                text_field.value = folder_path
                self.page.update()
                
        except Exception as e:
            print(f"[ERROR] 选择文件夹失败: {str(e)}")
            self.show_error(str(e))

    def _show_edit_dialog(self, project):
        """显示编辑项目对话框"""
        try:
            disk_id = ft.TextField(
                label="磁盘编号",
                value=project['disk_id'],
                keyboard_type=ft.KeyboardType.NUMBER,
            )
            project_date = ft.TextField(
                label="项目时间",
                value=project['project_date'],
            )
            project_name = ft.TextField(
                label="项目名称",
                value=project['project_name'],
                hint_text="必填项",
            )
            backup_status = ft.Checkbox(
                label="已备份",
                value=bool(project['backup_status']),
            )
            notes = ft.TextField(
                label="项目备注",
                value=project['notes'],
                multiline=True,
                min_lines=2,
                max_lines=5,
            )
            project_path = ft.TextField(
                label="项目路径",
                value=project['project_path'],
                suffix=ft.IconButton(
                    icon=ft.icons.FOLDER_OPEN,
                    on_click=lambda _: self._pick_folder(project_path),
                ),
            )
            filename = ft.TextField(
                label="文件名称",
                value=project['filename'],
            )

            def save_changes(_):
                try:
                    if not project_name.value.strip():
                        self.show_error("项目名称不能为空")
                        return
                    
                    self.manager.update_project(project['id'], {
                        'disk_id': disk_id.value or '0',
                        'project_date': project_date.value,
                        'project_name': project_name.value,
                        'backup_status': 1 if backup_status.value else 0,
                        'notes': notes.value,
                        'project_path': project_path.value,
                        'filename': filename.value,
                    })
                    edit_dlg.open = False  # 关闭对话框
                    self.refresh_data()  # 刷新数据
                    self.show_success("更新成功")
                except Exception as e:
                    self.show_error(f"更新失败: {str(e)}")

            # 创建编辑项目对话框
            edit_dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("编辑项目"),
                content=ft.Column([
                    disk_id,
                    project_date,
                    project_name,
                    backup_status,
                    notes,
                    project_path,
                    filename,
                ], scroll=ft.ScrollMode.AUTO, spacing=10),
                actions=[
                    ft.TextButton("取消", on_click=lambda e: self.page.close(edit_dlg)),  # 使用 page.close
                    ft.FilledButton("保存", on_click=save_changes),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                content_padding=ft.padding.all(20),  # 添加内容填充
                actions_padding=ft.padding.all(10),  # 添加操作按钮填充
                inset_padding=ft.padding.all(20),  # 添加对话框边距
            )
            
            self.page.dialog = edit_dlg  # 将对话框添加到页面
            self.page.open(edit_dlg)  # 使用 open 方法打开对话框
            self.page.update()
        except Exception as e:
            print(f"[ERROR] 显示编辑对话框失败: {str(e)}")
            self.show_error(str(e))

    def _show_detail_dialog(self, project):
        """显示项目详情对话框"""
        try:
            content = ft.Column(
                [
                    ft.Text(f"磁盘编号: {project['disk_id']}", size=14),
                    ft.Text(f"项目时间: {project['project_date']}", size=14),
                    ft.Text(f"项目名称: {project['project_name']}", size=14),
                    ft.Text(f"备份状态: {'已备份' if project['backup_status'] else '未备份'}", size=14),
                    ft.Text(f"项目路径: {project['project_path']}", size=14),
                    ft.Text(f"文件名称: {project['filename']}", size=14),
                    ft.Text(f"项目备注: {project['notes']}", size=14),
                ],
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
                height=300,
            )
            
            # 创建项目详情对话框
            detail_dlg = ft.AlertDialog(
                title=ft.Text("项目详情"),
                content=content,
                actions=[
                    ft.TextButton("关闭", on_click=lambda e: self.page.close(detail_dlg)),  # 使用 page.close
                    ft.TextButton("编辑", on_click=lambda _: self._show_edit_dialog(project)),
                    ft.TextButton("打开路径", on_click=lambda _: self._open_project_path(project)),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                content_padding=ft.padding.all(20),  # 添加内容填充
                actions_padding=ft.padding.all(10),  # 添加操作按钮填充
                inset_padding=ft.padding.all(20),  # 添加对话框边距
            )
            
            self.page.dialog = detail_dlg
            self.page.open(detail_dlg)  # 使用 open 方法打开对话框
            self.page.update()
            
        except Exception as e:
            print(f"[ERROR] 显示详情对话框失败: {str(e)}")
            self.show_error(str(e))

    def _delete_project(self, project_id):
        """删除项目"""
        def confirm_delete(_):
            try:
                self.manager.delete_project(project_id)
                delete_dlg.open = False  # 关闭对话框
                self.refresh_data()  # 刷新数据
                self.show_success("删除成功")
            except Exception as e:
                self.show_error(f"删除失败: {str(e)}")

        # 创建删除确认对话框
        delete_dlg = ft.AlertDialog(
            modal=True,  # 添加模态属性
            title=ft.Text("确认删除"),
            content=ft.Text("确定要删除这个项目吗？"),
            actions=[
                ft.TextButton("取消", on_click=lambda e: self.page.close(delete_dlg)),  # 使用 page.close
                ft.TextButton("删除", on_click=confirm_delete),
            ],
        )
        self.page.dialog = delete_dlg  # 将对话框添加到页面
        self.page.open(delete_dlg)  # 使用 open 方法打开对话框

    def _show_settings(self, e=None):
        """显示设置对话框"""
        try:
            auto_save_switch = ft.Switch(
                label="启用自动保存",
                value=bool(self.auto_save_timer),
            )
            
            def handle_submit(e):
                try:
                    # 更新自动保存设置
                    if auto_save_switch.value:
                        self._start_auto_save()
                    else:
                        self._stop_auto_save()
                    
                    settings_dlg.open = False  # 关闭对话框
                    self.show_success("设置已更新")
                    self.page.update()
                    
                except Exception as ex:
                    self.show_error(str(ex))
            
            def handle_cancel(e):
                settings_dlg.open = False  # 关闭对话框
                self.page.update()
            
            # 创建设置对话框
            settings_dlg = ft.AlertDialog(
                title=ft.Text("设置"),
                content=ft.Column([
                    auto_save_switch,
                ], tight=True, spacing=10),
                actions=[
                    ft.TextButton("取消", on_click=handle_cancel),
                    ft.FilledButton("保存", on_click=handle_submit),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            self.page.dialog = settings_dlg  # 将对话框添加到页面
            self.page.open(settings_dlg)  # 使用 open 方法打开对话框
            self.page.update()
            
        except Exception as e:
            print(f"[ERROR] 显示设置对话框失败: {str(e)}")
            self.show_error(str(e))

    def _start_auto_save(self):
        """启动自动保存"""
        if not self.auto_save_timer:
            try:
                from threading import Timer
                
                def auto_save_callback():
                    try:
                        # 不再创建新的定时器，而是使用一次性定时器
                        if hasattr(self, 'auto_save_timer'):  # 检查对象是否还存在
                            self._auto_save()
                            # 如果对象还存在，创建新的一次性定时器
                            if hasattr(self, 'auto_save_timer'):
                                self.auto_save_timer = Timer(300, auto_save_callback)
                                self.auto_save_timer.start()
                    except Exception as e:
                        print(f"[ERROR] 自动保存回调失败: {str(e)}")
                
                self.auto_save_timer = Timer(300, auto_save_callback)
                self.auto_save_timer.daemon = True  # 设置为守护线程
                self.auto_save_timer.start()
                print("[DEBUG] 自动保存定时器已启动")
                
            except Exception as e:
                print(f"[ERROR] 启动自动保存失败: {str(e)}")

    def _stop_auto_save(self):
        """停止自动保存"""
        try:
            if hasattr(self, 'auto_save_timer') and self.auto_save_timer:
                print("[DEBUG] 正在停止自动保存定时器...")
                self.auto_save_timer.cancel()
                self.auto_save_timer = None
                print("[DEBUG] 自动保存定时器已停止")
        except Exception as e:
            print(f"[ERROR] 停止自动保存失败: {str(e)}")

    def _auto_save(self):
        """执行自动保存"""
        try:
            # 这里可以添加自动保存的逻辑
            print("[DEBUG] 执行自动保存")
            self.last_save_time = datetime.now()
        except Exception as e:
            print(f"[ERROR] 自动保存失败: {str(e)}")

    def show_error(self, message: str):
        """显示错误提示"""
        try:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.colors.ERROR_CONTAINER,
            )
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as e:
            print(f"[ERROR] 显示错误提示失败: {str(e)}")

    def show_success(self, message: str):
        """显示成功提示"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.colors.SURFACE_VARIANT,
        )
        self.page.snack_bar.open = True
        self.page.update()

    def _on_view_pop(self, view):
        """处理页面关闭事件"""
        try:
            print("[DEBUG] 正在清理历史工程视图...")
            # 停止自动保存定时器
            self._stop_auto_save()
            # 清理其他资源
            if hasattr(self, 'manager'):
                self.manager = None
            if hasattr(self, 'data_table'):
                self.data_table = None
            print("[DEBUG] 历史工程视图清理完成")
        except Exception as e:
            print(f"[ERROR] 清理历史工程视图失败: {str(e)}")

    def _cleanup(self):
        """清理资源"""
        try:
            if not self._destroyed:
                print("[DEBUG] 开始清理历史工程视图资源...")
                self._stop_auto_save()
                
                # 移除 FilePicker
                if hasattr(self, 'import_picker'):
                    self.page.overlay.remove(self.import_picker)
                if hasattr(self, 'export_picker'):
                    self.page.overlay.remove(self.export_picker)
                
                # 清理其他资源
                self.manager = None
                self.data_table = None
                self._destroyed = True
                print("[DEBUG] 历史工程视图资源清理完成")
        except Exception as e:
            print(f"[ERROR] 清理资源失败: {str(e)}")

    def _handle_import_result(self, e: ft.FilePickerResultEvent):
        """处理导入结果"""
        try:
            if e.files:
                file_path = e.files[0].path
                # 显示进度对话框
                progress_dialog = ft.AlertDialog(
                    title=ft.Text("导入中..."),
                    content=ft.ProgressBar(width=400),
                )
                self.page.dialog = progress_dialog
                progress_dialog.open = True
                self.page.update()
                
                # 导入数据
                self.manager.import_from_excel(file_path)
                
                progress_dialog.open = False
                self.refresh_data()
                self.show_success("Excel导入成功")
                self.page.update()
        except Exception as ex:
            self.show_error(f"导入失败: {str(ex)}")

    def _handle_export_result(self, e: ft.FilePickerResultEvent):
        """处理导出结果"""
        try:
            if e.path:
                # 显示进度对话框
                progress_dialog = ft.AlertDialog(
                    title=ft.Text("导出中..."),
                    content=ft.ProgressBar(width=400),
                )
                self.page.dialog = progress_dialog
                progress_dialog.open = True
                self.page.update()
                
                # 导出数据
                self.manager.export_to_excel(e.path)
                
                progress_dialog.open = False
                self.show_success("Excel导出成功")
                self.page.update()
        except Exception as ex:
            self.show_error(f"导出失败: {str(ex)}")

    def _import_excel(self, e=None):
        """导入Excel数据"""
        try:
            self.import_picker.allowed_extensions = ["xlsx"]
            self.import_picker.pick_files()
        except Exception as e:
            print(f"[ERROR] 导入Excel失败: {str(e)}")
            self.show_error(str(e))

    def _export_excel(self, e=None):
        """导出Excel数据"""
        try:
            self.export_picker.allowed_extensions = ["xlsx"]
            self.export_picker.dialog_title = "保存Excel文件"
            self.export_picker.file_name = "项目列表.xlsx"
            self.export_picker.save_file()
        except Exception as e:
            print(f"[ERROR] 导出Excel失败: {str(e)}")
            self.show_error(str(e))

    def _handle_filter_change(self, e):
        """处理过滤条件变化"""
        try:
            # 更新过滤器状态
            if isinstance(e.control, ft.Dropdown):
                if e.control.label == "磁盘编号":
                    self.filters["disk_id"] = None if e.control.value == "全部" else e.control.value
                elif e.control.label == "备份状态":
                    if e.control.value == "全部":
                        self.filters["backup_status"] = None
                    elif e.control.value == "已备份":
                        self.filters["backup_status"] = 1
                    else:
                        self.filters["backup_status"] = 0
            elif isinstance(e.control, ft.TextField):
                # 通过父容器的文本来判断是哪个日期输入框
                label = e.control.parent.controls[0].value
                if label == "开始日期":
                    self.filters["date_from"] = e.control.value
                elif label == "结束日期":
                    self.filters["date_to"] = e.control.value

            # 刷新数据显示
            self.refresh_data()
        except Exception as e:
            print(f"[ERROR] 处理过滤条件变化失败: {str(e)}")
            self.show_error(str(e))

    def _handle_search(self, e):
        """处理搜索"""
        try:
            self.filters["search_text"] = e.control.value
            self.refresh_data()
        except Exception as e:
            print(f"[ERROR] 处理搜索失败: {str(e)}")
            self.show_error(str(e))

    def _open_project_path(self, project):
        """打开项目路径"""
        try:
            if project['project_path']:
                import os
                import platform
                import subprocess
                
                path = project['project_path']
                
                if platform.system() == "Windows":
                    os.startfile(path)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", path])
                else:  # Linux
                    subprocess.run(["xdg-open", path])
        except Exception as e:
            print(f"[ERROR] 打开路径失败: {str(e)}")
            self.show_error(f"打开路径失败: {str(e)}")

    def _update_pagination(self, total_pages):
        """更新分页控件"""
        pagination = ft.Row(
            [
                ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    on_click=lambda _: self._change_page(self.current_page - 1),
                    disabled=self.current_page <= 1,
                ),
                ft.Text(f"第 {self.current_page} 页 / 共 {total_pages} 页"),
                ft.IconButton(
                    icon=ft.icons.ARROW_FORWARD,
                    on_click=lambda _: self._change_page(self.current_page + 1),
                    disabled=self.current_page >= total_pages,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        # 更新分页控件
        self.pagination_row.controls = [pagination]

    def _change_page(self, new_page):
        """切换页码"""
        self.current_page = new_page
        self.refresh_data()

    def _handle_date_input(self, e, date_type):
        """处理日期输入变化"""
        if date_type == "start":
            self.filters["date_from"] = e.control.value
        elif date_type == "end":
            self.filters["date_to"] = e.control.value
        
        # 刷新数据显示
        self.refresh_data()