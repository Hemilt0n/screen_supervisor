"""存储管理模块"""

import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from PIL import Image

logger = logging.getLogger(__name__)


class StorageManager:
    """存储管理器，负责保存截图和清理过期文件"""

    def __init__(
        self,
        capture_root: str,
        image_format: str = "jpg",
        image_quality: int = 90,
        retention_days: int = 7,
    ):
        """
        初始化存储管理器

        Args:
            capture_root: 截图保存根目录
            image_format: 图像格式
            image_quality: 图像压缩质量（1-100），仅对 JPEG/WEBP 有效
            retention_days: 保留天数，<=0 表示不清理
        """
        self.capture_root = Path(capture_root)
        self.image_format = image_format
        self.image_quality = image_quality
        self.retention_days = retention_days

        # 确保根目录存在
        self.capture_root.mkdir(parents=True, exist_ok=True)

    def save(self, image: Image.Image, timestamp: datetime | None = None) -> Path:
        """
        保存截图到按日期归档的目录

        Args:
            image: 要保存的图像
            timestamp: 时间戳，默认为当前时间

        Returns:
            保存的文件路径
        """
        if timestamp is None:
            timestamp = datetime.now()

        # 创建日期目录
        date_dir = self.capture_root / timestamp.strftime("%Y-%m-%d")
        date_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名（年月日时分秒格式）
        filename = f"{timestamp.strftime('%Y%m%d%H%M%S')}.{self.image_format}"
        filepath = date_dir / filename

        # 保存图像（JPEG格式需要特殊处理）
        format_name = self.image_format.upper()
        if format_name == "JPG":
            format_name = "JPEG"

        # 根据格式决定是否使用压缩质量参数
        save_kwargs = {"format": format_name}
        if format_name in ("JPEG", "WEBP"):
            save_kwargs["quality"] = self.image_quality

        image.save(filepath, **save_kwargs)
        logger.debug(f"Saved screenshot: {filepath}")

        return filepath

    def cleanup_old_directories(self) -> int:
        """
        清理超过保留天数的日期目录

        Returns:
            删除的目录数量
        """
        if self.retention_days <= 0:
            logger.debug("Retention cleanup is disabled")
            return 0

        cutoff_date = datetime.now().date() - timedelta(days=self.retention_days)
        deleted_count = 0

        for date_dir in self.capture_root.iterdir():
            if not date_dir.is_dir():
                continue

            try:
                # 尝试解析目录名为日期
                dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d").date()

                if dir_date < cutoff_date:
                    logger.info(f"Deleting old directory: {date_dir}")
                    shutil.rmtree(date_dir)
                    deleted_count += 1
            except ValueError:
                # 目录名不是日期格式，跳过
                logger.warning(f"Skipping non-date directory: {date_dir}")
                continue

        return deleted_count

    def get_storage_stats(self) -> dict:
        """
        获取存储统计信息

        Returns:
            包含目录数、文件数和总大小的字典
        """
        total_files = 0
        total_size = 0
        dir_count = 0

        for date_dir in self.capture_root.iterdir():
            if date_dir.is_dir():
                dir_count += 1
                for f in date_dir.iterdir():
                    if f.is_file():
                        total_files += 1
                        total_size += f.stat().st_size

        return {
            "directories": dir_count,
            "files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }
