# 流影工坊 (LynionWorks)

## 项目简介
流影工坊是一个专业的媒体资产管理工具，用于管理和组织视频、音频、AE模板、LUT等多种媒体资源。

## 主要功能

### 1. 资产管理
- **AE模板管理**：管理和组织After Effects模板
- **视频素材管理**：管理各类视频素材
- **音效素材管理**：管理音频和音效文件
- **LUT管理**：管理调色查找表(LUT)文件

### 2. 资产设置
每种资产类型都支持以下设置：
- 分类管理
- 标签系统
- 评分系统
- 颜色标记

### 3. 工作流管理
- 项目文件夹模板
- 相机品牌和型号管理
- 路径设置
- 备份管理

## 技术栈
- Python 3.x
- Flet (UI框架)
- SQLite (数据存储)

## 项目结构 
lxgf/
├── app/
│ ├── controllers/
│ ├── database/
│ ├── utils/
│ └── views/
├── assets/
├── config/
└── main.py

## 数据库设计
主要包含以下数据表：
- asset_types (资产类型)
- categories (分类)
- tags (标签)
- color_marks (颜色标记)
- rating_settings (评分设置)
- camera_brands (相机品牌)
- camera_models (相机型号)
- folder_templates (文件夹模板)

## 开发说明

### 环境要求
- Python 3.8+
- flet
- sqlite3

### 安装依赖
```bash
pip install flet sqlite3
```

### 运行项目
```bash
python main.py
```

### 项目结构说明
- app/：主应用目录


### 配置说明
项目配置文件位于 `config/workflow_settings.json`，包含：
- 数据库路径
- 项目路径
- 模板路径
- 主题设置

## 特性
- 跨平台支持 (Windows, macOS, Linux)
- 中文界面
- 深色/浅色主题
- 响应式布局

## 注意事项
- 首次运行需要配置必要的路径设置
- 数据库文件会自动创建在配置的路径下
- 建议定期备份数据库文件

## 贡献指南
欢迎提交 Issue 和 Pull Request
