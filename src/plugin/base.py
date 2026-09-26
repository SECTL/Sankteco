from abc import ABC, abstractmethod
from PySide2.QtWidgets import QWidget
from typing import Optional


class SanktecoPlugin(ABC):
    """所有插件必须实现的抽象基类"""

    @abstractmethod
    def register(self, context) -> Optional[QWidget]:
        """
        插件注册函数,与之前的约定保持一致
        :param context: 主程序传递的 PluginContext 对象
        :return: 返回一个 QWidget 实例(作为页面),或者返回 None
        """
        pass
