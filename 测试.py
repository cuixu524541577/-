import flet as ft
from datetime import datetime, timedelta

# 动态计算日期范围（核心修改点）
def get_date_range():
    current_year = datetime.now().year
    start_date = datetime(2015, 1, 1)  # 固定起始年份[6](@ref)
    end_date = datetime(current_year + 15, 12, 31)  # 当前年份+15年[6](@ref)
    return start_date, end_date

def main(page: ft.Page):
    # ==================== 初始化配置 ==================== 
    # 设置默认日期范围（可修改默认跨度）
    start_date, end_date = get_date_range()  # 使用动态计算的日期范围
    # start_date = datetime.now() - timedelta(days=30)  # 默认显示最近30天
    # end_date = datetime.now()                         # 默认结束日期为当天
    
    # 本地化配置（支持中文显示）[5](@ref)
    page.locale_configuration = ft.LocaleConfiguration(
        supported_locales=[ft.Locale("zh", "CN", "Hans")],  # 可添加其他语言
        current_locale=ft.Locale("zh", "CN", "Hans")        # 设置当前语言
    )

    # ==================== 日期选择器配置 ====================
    # 开始日期选择器（可调整时间范围）
    start_picker = ft.DatePicker(
        first_date=get_date_range()[0],  # 2015-01-01
        last_date=datetime.now(),        # 动态结束日期
        current_date=datetime.now() - timedelta(days=30),
        on_change=lambda e: handle_start_date(e)
    )

    # 结束日期选择器（扩展可选范围）
    end_picker = ft.DatePicker(
        first_date=get_date_range()[0],  # 保持与开始选择器同步
        last_date=get_date_range()[1],   # 未来15年的最后一天
        current_date=datetime.now(),
        on_change=lambda e: handle_end_date(e)
    )

    # 必须将选择器添加到页面覆盖层（解决 AssertionError 关键步骤）[4](@ref)
    page.overlay.extend([start_picker, end_picker])

    # ==================== 界面组件构建 ====================
    # 开始日期输入框（可自定义样式参数）
    start_field = ft.TextField(
        label="开始日期",                    # 标签文字可修改
        value=start_date.strftime("%Y-%m-%d"),  # 日期格式可改为 "%Y年%m月%d日"
        width=200,                       # 输入框宽度（建议 200-300px）
        read_only=True,                   # 防止直接输入
        suffix=ft.IconButton(
            icon=ft.icons.CALENDAR_MONTH,  # 图标可替换为 ft.icons.ACCESS_TIME
            tooltip="选择开始日期",        # 鼠标悬停提示
            on_click=lambda e: page.open(start_picker)  # 使用 page.open() 打开选择器
        )
    )

    # 结束日期输入框（配置同上）
    end_field = ft.TextField(
        label="结束日期",
        value=end_date.strftime("%Y-%m-%d"),
        width=200,
        read_only=True,
        suffix=ft.IconButton(
            icon=ft.icons.CALENDAR_MONTH,
            tooltip="选择结束日期",
            on_click=lambda e: page.open(end_picker)  # 使用 page.open() 打开选择器
        )
    )

    # ==================== 事件处理逻辑 ====================
    def handle_start_date(e):
        """处理开始日期变更事件"""
        start_field.value = e.control.value.strftime("%Y-%m-%d")  # 使用 control.value 获取日期
        page.update()  # 强制刷新界面
        print_selected_dates()  # 输出到控制台

    def handle_end_date(e):
        """处理结束日期变更事件""" 
        end_field.value = e.control.value.strftime("%Y-%m-%d")  # 使用 control.value 获取日期
        page.update()
        print_selected_dates()

    def print_selected_dates():
        """打印当前选择的日期范围（可扩展为数据过滤逻辑）"""
        print(f"开始日期: {start_field.value} | 结束日期: {end_field.value}")
        # 可在此添加日期范围校验逻辑（如开始日期不能晚于结束日期）[4](@ref)

    # ==================== 页面布局配置 ====================
    page.add(
        ft.Row(
            controls=[start_field, end_field],  # 控件列表
            alignment=ft.MainAxisAlignment.CENTER,  # 居中布局（可改为 START）
            spacing=20,                      # 控件间距（单位：像素）
            vertical_alignment=ft.CrossAxisAlignment.CENTER  # 垂直居中
        )
    )

# 启动应用程序（可配置窗口参数）
ft.app(
    target=main,
    # view=ft.WEB_BROWSER,  # 以网页模式打开
    # port=8080            # 指定端口号
)