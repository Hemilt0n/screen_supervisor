"""存储模块测试"""

from datetime import datetime, timedelta
from pathlib import Path

import pytest
from PIL import Image

from screen_supervisor.storage import StorageManager


class TestStorageManager:
    """存储管理器测试"""

    def test_init_creates_directory(self, tmp_path: Path):
        """测试初始化时创建目录"""
        capture_root = tmp_path / "screenshots"
        assert not capture_root.exists()

        StorageManager(str(capture_root))
        assert capture_root.exists()

    def test_save_creates_date_directory(self, tmp_path: Path):
        """测试保存时创建日期目录"""
        storage = StorageManager(str(tmp_path / "captures"))
        image = Image.new("RGB", (100, 100), color="red")

        timestamp = datetime(2024, 6, 15, 10, 30, 45)
        filepath = storage.save(image, timestamp)

        assert filepath.exists()
        assert "2024-06-15" in str(filepath)
        assert filepath.name == "20240615103045.jpg"

    def test_save_with_different_format(self, tmp_path: Path):
        """测试不同图像格式"""
        storage = StorageManager(str(tmp_path / "captures"), image_format="jpg")
        image = Image.new("RGB", (100, 100), color="blue")

        filepath = storage.save(image)
        assert filepath.suffix == ".jpg"

    def test_cleanup_old_directories(self, tmp_path: Path):
        """测试清理过期目录"""
        storage = StorageManager(str(tmp_path / "captures"), retention_days=7)

        # 创建过期目录
        old_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        old_dir = storage.capture_root / old_date
        old_dir.mkdir(parents=True)
        (old_dir / "old.png").touch()

        # 创建新目录
        new_date = datetime.now().strftime("%Y-%m-%d")
        new_dir = storage.capture_root / new_date
        new_dir.mkdir(parents=True)
        (new_dir / "new.png").touch()

        deleted = storage.cleanup_old_directories()

        assert deleted == 1
        assert not old_dir.exists()
        assert new_dir.exists()

    def test_cleanup_disabled(self, tmp_path: Path):
        """测试禁用清理"""
        storage = StorageManager(str(tmp_path / "captures"), retention_days=0)
        deleted = storage.cleanup_old_directories()
        assert deleted == 0

    def test_get_storage_stats(self, tmp_path: Path):
        """测试存储统计"""
        storage = StorageManager(str(tmp_path / "captures"))
        image = Image.new("RGB", (10, 10), color="green")

        # 使用不同时间戳确保文件不会覆盖
        timestamp1 = datetime(2024, 6, 15, 10, 0, 0)
        timestamp2 = datetime(2024, 6, 15, 10, 0, 1)
        storage.save(image, timestamp1)
        storage.save(image, timestamp2)

        stats = storage.get_storage_stats()
        assert stats["directories"] == 1
        assert stats["files"] == 2
        assert stats["total_size_bytes"] > 0
