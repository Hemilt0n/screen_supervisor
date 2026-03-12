"""屏幕监管器主模块"""

import logging
from datetime import datetime

from .capturer import ScreenCapturer
from .config import SupervisorConfig
from .scheduler import IntervalScheduler
from .storage import StorageManager

logger = logging.getLogger(__name__)


class ScreenSupervisor:
    """屏幕监管器，协调截屏、存储和清理"""

    def __init__(self, config: SupervisorConfig):
        """
        初始化监管器

        Args:
            config: 配置对象
        """
        self.config = config
        self.capturer = ScreenCapturer(monitor_index=config.monitor_index)
        self.storage = StorageManager(
            capture_root=config.capture_root,
            image_format=config.image_format,
            image_quality=config.image_quality,
            retention_days=config.retention_days,
        )
        self.scheduler = IntervalScheduler(interval_seconds=config.interval_seconds)
        self._last_cleanup_check = datetime.now()

    def capture_once(self) -> str:
        """
        执行一次截屏并保存

        Returns:
            保存的文件路径
        """
        timestamp = datetime.now()

        # 截取屏幕
        image = self.capturer.capture()

        # 保存图像
        filepath = self.storage.save(image, timestamp)

        logger.info(f"Captured and saved: {filepath}")
        return str(filepath)

    def _run_iteration(self) -> None:
        """单次迭代：截屏、保存、定期清理"""
        # 执行截屏
        self.capture_once()

        # 每小时检查一次清理（避免频繁检查）
        now = datetime.now()
        hours_since_cleanup = (now - self._last_cleanup_check).total_seconds() / 3600

        if hours_since_cleanup >= 1:
            deleted = self.storage.cleanup_old_directories()
            if deleted > 0:
                logger.info(f"Cleaned up {deleted} old directories")
            self._last_cleanup_check = now

    def run(self) -> None:
        """开始监管循环"""
        logger.info(
            f"Starting Screen Supervisor - interval: {self.config.interval_seconds}s, "
            f"root: {self.config.capture_root}, retention: {self.config.retention_days} days"
        )

        # 显示器信息
        monitors = self.capturer.get_monitor_info()
        logger.info(f"Available monitors: {len(monitors) - 1} (using index {self.config.monitor_index})")

        # 运行调度循环
        self.scheduler.start(self._run_iteration)

    def stop(self) -> None:
        """停止监管循环"""
        logger.info("Stopping Screen Supervisor")
        self.scheduler.stop()

    def force_cleanup(self) -> int:
        """强制执行清理"""
        return self.storage.cleanup_old_directories()
