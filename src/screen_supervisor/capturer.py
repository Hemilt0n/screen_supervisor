"""屏幕截取模块"""

import logging
from typing import Any

import mss
from PIL import Image

logger = logging.getLogger(__name__)


class ScreenCapturer:
    """屏幕截取器，基于 mss 实现"""

    def __init__(self, monitor_index: int = 0):
        """
        初始化截取器

        Args:
            monitor_index: 显示器索引
                - 0: 所有显示器的虚拟屏幕（整屏）
                - 1: 第一个显示器
                - 2: 第二个显示器，以此类推
        """
        self.monitor_index = monitor_index

    def capture(self) -> Image.Image:
        """
        截取屏幕并返回 Pillow 图像

        Returns:
            PIL.Image: 截取的图像
        """
        with mss.mss() as sct:
            # 获取指定显示器的区域
            monitor = sct.monitors[self.monitor_index]
            logger.debug(f"Capturing monitor {self.monitor_index}: {monitor}")

            # 截取屏幕
            screenshot = sct.grab(monitor)

            # 转换为 Pillow 图像
            img = Image.frombytes(
                "RGB",
                (screenshot.width, screenshot.height),
                screenshot.rgb,
            )

            logger.debug(f"Captured image: {img.size}")
            return img

    def get_monitor_info(self) -> list[dict[str, Any]]:
        """
        获取所有显示器信息

        Returns:
            显示器信息列表
        """
        with mss.mss() as sct:
            return sct.monitors
