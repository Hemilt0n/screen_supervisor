"""命令行接口模块"""

import logging
import signal
import sys
from pathlib import Path

import typer
from rich.console import Console

from .config import load_config
from .supervisor import ScreenSupervisor

app = typer.Typer(
    name="screen-supervisor",
    help="全天候屏幕监管器，每秒截取屏幕并按日期归档",
)
console = Console()


def setup_logging(level: str) -> None:
    """配置日志"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# 全局变量，用于信号处理
_supervisor: ScreenSupervisor | None = None


def signal_handler(signum, frame):
    """信号处理器，优雅退出"""
    if _supervisor is not None:
        _supervisor.stop()
    sys.exit(0)


@app.command()
def run(
    config: Path = typer.Option(
        "config.toml",
        "--config",
        "-c",
        help="配置文件路径",
        exists=False,
    ),
) -> None:
    """启动屏幕监管服务"""
    global _supervisor

    # 加载配置
    try:
        cfg = load_config(config)
    except Exception as e:
        console.print(f"[red]加载配置失败: {e}[/red]")
        raise typer.Exit(1)

    # 配置日志
    setup_logging(cfg.log_level)

    # 创建监管器
    _supervisor = ScreenSupervisor(cfg)

    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 运行
    try:
        _supervisor.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]收到中断信号，正在停止...[/yellow]")
        _supervisor.stop()


@app.command()
def clean(
    config: Path = typer.Option(
        "config.toml",
        "--config",
        "-c",
        help="配置文件路径",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="仅显示将要删除的目录，不实际删除",
    ),
) -> None:
    """手动清理过期的截图目录"""
    try:
        cfg = load_config(config)
    except Exception as e:
        console.print(f"[red]加载配置失败: {e}[/red]")
        raise typer.Exit(1)

    if cfg.retention_days <= 0:
        console.print("[yellow]保留天数设置为0，清理功能已禁用[/yellow]")
        return

    from .storage import StorageManager

    storage = StorageManager(
        capture_root=cfg.capture_root,
        image_format=cfg.image_format,
        retention_days=cfg.retention_days,
    )

    if dry_run:
        from datetime import datetime, timedelta

        cutoff_date = datetime.now().date() - timedelta(days=cfg.retention_days)
        console.print(f"[blue]将删除 {cutoff_date} 之前的目录:[/blue]")

        for date_dir in storage.capture_root.iterdir():
            if date_dir.is_dir():
                try:
                    dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d").date()
                    if dir_date < cutoff_date:
                        console.print(f"  - {date_dir}")
                except ValueError:
                    pass
    else:
        deleted = storage.cleanup_old_directories()
        console.print(f"[green]已清理 {deleted} 个过期目录[/green]")


@app.command()
def info(
    config: Path = typer.Option(
        "config.toml",
        "--config",
        "-c",
        help="配置文件路径",
    ),
) -> None:
    """显示当前配置和存储统计"""
    try:
        cfg = load_config(config)
    except Exception as e:
        console.print(f"[red]加载配置失败: {e}[/red]")
        raise typer.Exit(1)

    console.print("[bold]当前配置:[/bold]")
    console.print(f"  截屏间隔: {cfg.interval_seconds} 秒")
    console.print(f"  保存目录: {cfg.capture_root}")
    console.print(f"  图像格式: {cfg.image_format}")
    console.print(f"  显示器索引: {cfg.monitor_index}")
    console.print(f"  保留天数: {cfg.retention_days}")
    console.print(f"  日志级别: {cfg.log_level}")

    from .storage import StorageManager

    storage = StorageManager(
        capture_root=cfg.capture_root,
        image_format=cfg.image_format,
        retention_days=cfg.retention_days,
    )

    stats = storage.get_storage_stats()
    console.print("\n[bold]存储统计:[/bold]")
    console.print(f"  日期目录数: {stats['directories']}")
    console.print(f"  截图文件数: {stats['files']}")
    console.print(f"  总大小: {stats['total_size_mb']} MB")


if __name__ == "__main__":
    app()
