"""调度器模块"""

import logging
import threading
import time
from collections.abc import Callable

logger = logging.getLogger(__name__)


class IntervalScheduler:
    """固定间隔调度器，使用线程安全的事件控制"""

    def __init__(self, interval_seconds: float):
        """
        初始化调度器

        Args:
            interval_seconds: 执行间隔（秒）
        """
        self.interval_seconds = interval_seconds
        self._stop_event = threading.Event()
        self._running = False

    def start(self, task: Callable[[], None]) -> None:
        """
        开始调度循环

        Args:
            task: 要执行的任务函数
        """
        self._stop_event.clear()
        self._running = True

        logger.info(f"Starting scheduler with interval {self.interval_seconds}s")

        while not self._stop_event.is_set():
            start_time = time.monotonic()

            try:
                task()
            except Exception as e:
                logger.error(f"Task execution failed: {e}")

            # 计算剩余等待时间
            elapsed = time.monotonic() - start_time
            sleep_time = self.interval_seconds - elapsed

            if sleep_time > 0:
                # 使用 wait 而不是 sleep，以便能响应停止信号
                if self._stop_event.wait(timeout=sleep_time):
                    break
            else:
                logger.warning(
                    f"Task took longer than interval: {elapsed:.2f}s > {self.interval_seconds}s"
                )

        self._running = False
        logger.info("Scheduler stopped")

    def stop(self) -> None:
        """停止调度循环"""
        logger.debug("Stopping scheduler")
        self._stop_event.set()

    def is_running(self) -> bool:
        """检查调度器是否在运行"""
        return self._running
