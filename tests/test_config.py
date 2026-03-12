"""配置模块测试"""

import os
from pathlib import Path

import pytest

from screen_supervisor.config import SupervisorConfig, load_config


class TestSupervisorConfig:
    """配置模型测试"""

    def test_default_values(self):
        """测试默认值"""
        config = SupervisorConfig()
        assert config.interval_seconds == 1.0
        assert config.capture_root == "captures"
        assert config.image_format == "jpg"
        assert config.image_quality == 90
        assert config.monitor_index == 0
        assert config.retention_days == 7
        assert config.log_level == "INFO"

    def test_log_level_validation(self):
        """测试日志级别验证"""
        config = SupervisorConfig(log_level="debug")
        assert config.log_level == "DEBUG"

        with pytest.raises(ValueError):
            SupervisorConfig(log_level="INVALID")

    def test_image_format_lowercase(self):
        """测试图像格式转换为小写"""
        config = SupervisorConfig(image_format="PNG")
        assert config.image_format == "png"

    def test_interval_must_be_positive(self):
        """测试间隔必须为正数"""
        with pytest.raises(ValueError):
            SupervisorConfig(interval_seconds=0)

        with pytest.raises(ValueError):
            SupervisorConfig(interval_seconds=-1)


class TestLoadConfig:
    """配置加载测试"""

    def test_load_from_file(self, tmp_path: Path):
        """测试从文件加载配置"""
        config_file = tmp_path / "config.toml"
        config_file.write_text("""
interval_seconds = 2.5
capture_root = "custom_captures"
image_format = "jpg"
retention_days = 14
log_level = "DEBUG"
""")

        config = load_config(config_file)
        assert config.interval_seconds == 2.5
        assert config.capture_root == "custom_captures"
        assert config.image_format == "jpg"
        assert config.retention_days == 14
        assert config.log_level == "DEBUG"

    def test_env_override(self, tmp_path: Path, monkeypatch):
        """测试环境变量覆盖"""
        config_file = tmp_path / "config.toml"
        config_file.write_text("interval_seconds = 1.0")

        monkeypatch.setenv("SCREEN_SUP_INTERVAL", "3.5")
        monkeypatch.setenv("SCREEN_SUP_LOG_LEVEL", "ERROR")

        config = load_config(config_file)
        assert config.interval_seconds == 3.5
        assert config.log_level == "ERROR"

    def test_missing_file_uses_defaults(self, tmp_path: Path):
        """测试缺失配置文件时使用默认值"""
        config = load_config(tmp_path / "nonexistent.toml")
        assert config.interval_seconds == 1.0
