"""配置管理模块"""

import os
from pathlib import Path
from typing import Any

import tomllib
from pydantic import BaseModel, Field, field_validator


class SupervisorConfig(BaseModel):
    """截屏监管器配置"""

    interval_seconds: float = Field(default=1.0, gt=0, description="截屏间隔（秒）")
    capture_root: str = Field(default="captures", description="截图保存根目录")
    image_format: str = Field(default="jpg", description="图像格式")
    image_quality: int = Field(default=90, ge=1, le=100, description="图像压缩质量（1-100）")
    monitor_index: int = Field(default=0, ge=0, description="显示器索引，0表示所有显示器")
    retention_days: int = Field(default=7, ge=0, description="数据保留天数，0表示不清理")
    log_level: str = Field(default="INFO", description="日志级别")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v_upper

    @field_validator("image_format")
    @classmethod
    def validate_image_format(cls, v: str) -> str:
        return v.lower()


def load_config(config_path: str | Path | None = None) -> SupervisorConfig:
    """加载配置，优先级：环境变量 > 配置文件 > 默认值"""
    config_data: dict[str, Any] = {}

    # 从配置文件加载
    if config_path is not None:
        path = Path(config_path)
        if path.exists():
            with open(path, "rb") as f:
                config_data = tomllib.load(f)

    # 环境变量覆盖
    env_mappings = {
        "SCREEN_SUP_INTERVAL": ("interval_seconds", float),
        "SCREEN_SUP_CAPTURE_ROOT": ("capture_root", str),
        "SCREEN_SUP_IMAGE_FORMAT": ("image_format", str),
        "SCREEN_SUP_IMAGE_QUALITY": ("image_quality", int),
        "SCREEN_SUP_MONITOR": ("monitor_index", int),
        "SCREEN_SUP_RETENTION_DAYS": ("retention_days", int),
        "SCREEN_SUP_LOG_LEVEL": ("log_level", str),
    }

    for env_key, (config_key, type_fn) in env_mappings.items():
        env_value = os.environ.get(env_key)
        if env_value is not None:
            config_data[config_key] = type_fn(env_value)

    return SupervisorConfig(**config_data)
