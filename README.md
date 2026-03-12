# Screen Supervisor

全天候屏幕监管器，每秒截取整个显示区域，按天归档截图文件，方便审计、留存或排查问题。项目围绕 uv 管理环境，提供可配置的截屏频率、存储目录和自动清理能力。

## ✨ 特性
- 每秒截屏一次（可配置），自动归档到 captures/YYYY-MM-DD/ 目录
- 支持自定义保存根目录、图像格式、日志级别
- 内置日志记录与磁盘清理，防止截图持续堆积
- Typer 命令行工具，便捷运行、调试与健康检查

## 📦 环境准备（基于 uv）
1. 安装 uv（任选其一）：
   ~~~bash
   pip install uv
   # 或访问 https://github.com/astral-sh/uv 获取二进制安装方式
   ~~~
2. 在项目根目录同步依赖：
   ~~~bash
   uv sync
   ~~~
3. 如需固定 Python，执行 uv python install 3.11（可选）。

## 🚀 快速开始
1. 复制并编辑配置：
   ~~~bash
   cp configs/config.example.toml config.toml
   ~~~
2. 使用 Typer CLI 运行：
   ~~~bash
   uv run screen-supervisor run --config config.toml
   ~~~
3. 停止：Ctrl+C，或使用系统服务托管（见下方）。

## ⚙️ 配置
配置文件采用 TOML，可通过 CLI 参数或环境变量覆盖。

| 键 | 默认值 | 说明 |
| --- | --- | --- |
| interval_seconds | 1.0 | 截屏间隔（秒） |
| capture_root | captures | 截图根目录，子目录为 YYYY-MM-DD |
| image_format | png | 保存格式（Pillow 支持格式） |
| retention_days | 7 | 自动清理超过 N 天的日期文件夹（<=0 表示禁用） |
| log_level | INFO | 日志级别 |

也支持以下环境变量（优先级最高）：
- SCREEN_SUP_INTERVAL
- SCREEN_SUP_CAPTURE_ROOT
- SCREEN_SUP_IMAGE_FORMAT
- SCREEN_SUP_RETENTION_DAYS
- SCREEN_SUP_LOG_LEVEL

## 📁 目录结构
~~~
.
├── configs/                # 配置示例
├── docs/                   # 架构、配置、运维等文档
├── scripts/                # 启动/辅助脚本
├── src/screen_supervisor/  # 核心代码
├── tests/                  # pytest 测试
├── captures/               # 运行时生成，按日归档
├── logs/                   # 运行日志
└── README.md
~~~

## 🧪 测试
~~~bash
uv run pytest
~~~

## 🛠️ 作为服务运行
- Linux systemd：创建服务文件，执行 uv run screen-supervisor run --config /path/to/config.toml
- Windows 任务计划：通过 PowerShell Register-ScheduledTask，触发脚本 scripts/run_supervisor.py

## 🗂️ 日志与数据
- 截图：默认写入 captures/YYYY-MM-DD/HHMMSSffffff.png
- 日志：日志默认输出到终端，后续可在配置中设置 logs/
- 清理：screen-supervisor clean 或运行时自动根据 retention_days 清理过期目录

## 🤝 贡献
1. Fork/新建分支
2. uv sync && uv run pytest
3. 遵循 ruff/pytest 检查

## ❓ 常见问题
更多细节见 docs/：
- docs/README.arch.md：架构说明
- docs/README.config.md：配置详解
- docs/README.ops.md：部署运维
- docs/README.troubleshoot.md：故障排查
