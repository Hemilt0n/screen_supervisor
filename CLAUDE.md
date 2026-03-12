# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Screen Supervisor 是一个全天候屏幕监管器，每秒截取整个显示区域，按天归档截图文件。使用 uv 管理 Python 环境和依赖。

## 常用命令

```bash
# 同步依赖
uv sync

# 运行截屏服务（需要先复制配置文件）
cp configs/config.example.toml config.toml
uv run screen-supervisor run --config config.toml

# 运行测试
uv run pytest

# 运行单个测试文件
uv run pytest tests/test_config.py -v

# 代码检查
uv run ruff check src/

# 格式化代码
uv run ruff format src/
```

## 架构

项目由四个核心组件组成：

1. **Config** (`config.py`): 加载 TOML 配置文件和环境变量，生成 `SupervisorConfig`
2. **ScreenCapturer** (`capturer.py`): 基于 mss 截取屏幕，返回 Pillow 图像对象
3. **StorageManager** (`storage.py`): 创建日期目录、保存图像、按保留策略清理旧目录
4. **IntervalScheduler** (`scheduler.py`): 线程安全的固定间隔循环
5. **ScreenSupervisor** (`supervisor.py`): 绑定上述组件，实现捕获→保存→清理流程
6. **CLI** (`cli.py`): Typer 命令行入口，提供 `run` 和 `clean` 子命令

## 配置优先级

1. CLI 参数
2. 环境变量（`SCREEN_SUP_*` 前缀）
3. config.toml 文件
4. 默认值

## 环境变量

- `SCREEN_SUP_INTERVAL`: 截屏间隔（秒）
- `SCREEN_SUP_CAPTURE_ROOT`: 截图根目录
- `SCREEN_SUP_IMAGE_FORMAT`: 图像格式
- `SCREEN_SUP_IMAGE_QUALITY`: 图像压缩质量（1-100）
- `SCREEN_SUP_MONITOR`: 显示器索引
- `SCREEN_SUP_RETENTION_DAYS`: 保留天数
- `SCREEN_SUP_LOG_LEVEL`: 日志级别
