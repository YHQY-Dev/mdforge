# MdForge

将 PDF 转为 Markdown 的桌面工具（PySide6 + uv），支持三种解析引擎：

| 解析器 | 说明 | Token |
|--------|------|-------|
| **MarkItDown** | 本地转换，无需网络 | 不需要 |
| **MinerU** | 云端高精度解析 | 需在设置中填写 |
| **PaddleOCR** | 云端 OCR 解析 | 需在设置中填写 |

## 环境

- Python 3.12+
- [uv](https://github.com/astral-sh/uv)

```bash
uv sync
uv sync --group dev
```

## 运行

```bash
uv run python main.py
# 或
uv run mdforge
```

## 测试

使用 `examples/` 下的样例 PDF（若本地存在）：

```bash
uv run pytest tests/ -v
```

开发时可在项目根目录放置 `.env`（勿提交），用于自动填充 Token：

```
MinerU_TOKEN=...
PaddleOCR_TOKEN=...
```

## 项目结构（MVC）

```
src/mdforge/
  core/          # 设置、日志、批量文件收集
  parsers/       # 三种解析器（独立模块，便于扩展）
  services/      # 转换业务逻辑
  models/        # 请求/结果数据类
  controllers/   # 界面与业务桥接
  views/         # PySide6 界面
  workers/       # 后台线程
```

日志目录：`%USERPROFILE%\.mdforge\logs\`

设置保存在系统 QSettings。
