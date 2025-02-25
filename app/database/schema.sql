-- 创建必要的数据表
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 项目类型定义
CREATE TABLE IF NOT EXISTS project_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,  -- 类型标识：simple/complex
    description TEXT,     -- 类型描述
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 预设项目类型
INSERT OR IGNORE INTO project_types (name, description) VALUES 
    ('simple', '简易项目 - 基础文件夹结构管理'),
    ('complex', '大型项目 - 高级文件夹模板管理');

-- 文件夹模板表
CREATE TABLE IF NOT EXISTS folder_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_type_id INTEGER NOT NULL,
    parent_id INTEGER,
    name TEXT NOT NULL,
    description TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_type_id) REFERENCES project_types(id),
    FOREIGN KEY (parent_id) REFERENCES folder_templates(id)
);

-- 文件夹历史版本表（仅用于大型项目）
CREATE TABLE IF NOT EXISTS folder_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 改为 INTEGER 自增主键
    template_id INTEGER NOT NULL,  -- 关联的模板ID
    version TEXT NOT NULL,      -- 版本号
    snapshot TEXT NOT NULL,     -- JSON格式的快照数据
    comment TEXT,              -- 版本说明
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES folder_templates(id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_folder_templates_parent ON folder_templates(parent_id);
CREATE INDEX IF NOT EXISTS idx_folder_templates_project ON folder_templates(project_type_id);
CREATE INDEX IF NOT EXISTS idx_folder_history_template ON folder_history(template_id);

-- 创建唯一约束（同一项目类型下，同级目录文件夹名称唯一）
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_folder 
ON folder_templates(project_type_id, parent_id, name);

-- 删除旧的触发器（如果存在）
DROP TRIGGER IF EXISTS trig_folder_templates_timestamp;

-- 相机品牌表
CREATE TABLE IF NOT EXISTS camera_brands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 相机型号表
CREATE TABLE IF NOT EXISTS camera_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (brand_id) REFERENCES camera_brands(id),
    UNIQUE(brand_id, name)
);

-- 历史工程相关表
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    disk_id TEXT NOT NULL,
    project_date TEXT NOT NULL,
    project_name TEXT NOT NULL,
    backup_status INTEGER DEFAULT 0,
    notes TEXT,
    project_path TEXT NOT NULL,
    filename TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS project_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    color TEXT DEFAULT '#FFFFFF'
);

CREATE TABLE IF NOT EXISTS project_tag_relations (
    project_id INTEGER,
    tag_id INTEGER,
    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES project_tags (id) ON DELETE CASCADE,
    PRIMARY KEY (project_id, tag_id)
);

-- 可以添加更多表结构... 