# 海报管理平台

基于 Flask 的轻量海报管理平台，支持：

- 海报数据的创建、编辑、删除（CRUD）
- 基于模板渲染预览（当前内置“大闸蟹价目表”模板）
- 前端一键导出 PNG（html2canvas）

## 本地运行（Windows PowerShell）

1. 建议创建虚拟环境（可选）

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

1. 安装依赖

```powershell
pip install -r requirements.txt
```

1. 启动服务（首次会自动初始化 SQLite 数据库并写入示例海报）

```powershell
python app.py
```

1. 浏览器打开

- 列表页：<http://127.0.0.1:5000/posters>
- 预览页：点击列表卡片上的“预览”

## 目录说明

- `app.py` 后端与路由、数据模型
- `templates/` Jinja 模板（基础布局、列表、编辑、渲染海报）
- `crab_poster.html` 原始静态示例（未被应用运行直接使用，已被模板化为 `templates/poster_crab.html`）
- `static/` 静态资源目录（如需图片等静态资源，可放在这里并以 `/static/...` 引用）。

## 自定义模板数据

编辑/新建时在“模板数据(JSON)”内修改。字段结构示例：

```json
{
  "title": "🦀 精品大闸蟹套餐价格表",
  "highlight": { "badge": "人气", "text": "尝鲜装,2.5公1.5母十只", "price": "108" },
  "sections": [
    { "variant": "mixed-8", "heading": "公母混合 · 8只装", "rows": [ { "spec": "3.0公2.0母（公母各4只）", "price": "168" } ] }
  ],
  "promises": ["...支持多条..."]
}
```

## 后续可扩展点

- 登录与权限、草稿与发布状态
- 多模板选择与可视化编辑器
- 后端导出图片（无头浏览器）
- 批量分享与短链接
