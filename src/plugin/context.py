"""
插件上下文:安全的API接口
"""

from typing import Optional, Any, Dict
from pathlib import Path
from PySide2.QtCore import QObject, Signal, QStandardPaths
from PySide2.QtWidgets import QWidget
from qfluentwidgets import FluentIcon


class PluginContext(QObject):
    """
    插件安全上下文,只暴露必要的主程序功能
    """

    # 全局信号(插件可监听或发射)
    student_selected = Signal(str)  # 点名完成
    theme_changed = Signal(bool)  # 主题切换(True=暗色)

    def __init__(self, main_window: "MainWindow", config: "AppConfig"):  # type: ignore
        super().__init__()
        self._main_window = main_window
        self._config = config
        self._plugin_id: Optional[str] = None  # 新增:当前插件ID
        self._plugin_data: Dict[str, Any] = {}  # 插件私有数据存储

    # ---------- 插件 ID 管理 ----------
    def set_plugin_id(self, plugin_id: str) -> None:
        """
        设置当前操作的插件ID(由主程序在调用 register 前调用)
        """
        self._plugin_id = plugin_id

    def get_plugin_id(self) -> Optional[str]:
        """获取当前插件的ID"""
        return self._plugin_id

    # ---------- 数据目录管理 ----------
    def get_plugin_data_dir(self) -> Optional[Path]:
        """
        获取当前插件的数据存储目录
        需要先调用 set_plugin_id 设置插件ID
        """
        if not self._plugin_id:
            return None

        # 使用 QStandardPaths 获取应用数据目录
        data_root = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation))  # type: ignore
        plugin_data_dir = data_root / "Sankteco" / "plugins" / "data" / self._plugin_id
        plugin_data_dir.mkdir(parents=True, exist_ok=True)
        return plugin_data_dir

    # ---------- 页面管理 API ----------
    def add_page(
        self,
        widget: QWidget,
        icon: str,
        text: str,
        position: str = "top",
        parent_route: Optional[str] = None,
    ):
        """
        添加插件页面到主窗口导航栏
        """
        from qfluentwidgets import NavigationItemPosition

        # 确保 widget 有唯一的 objectName(用于路由)
        if not widget.objectName():
            widget.setObjectName(f"plugin_{id(widget)}")

        # 转换位置参数
        pos_map = {
            "top": NavigationItemPosition.TOP,
            "bottom": NavigationItemPosition.BOTTOM,
        }
        position_enum = pos_map.get(position, NavigationItemPosition.BOTTOM)

        # 尝试从 FluentIcon 获取图标
        try:
            icon_enum = getattr(FluentIcon, icon.upper(), FluentIcon.APPLICATION)
        except:
            icon_enum = FluentIcon.APPLICATION

        # 调用主窗口的 addSubInterface
        self._main_window.addSubInterface(
            widget, icon_enum, text, position_enum, parent_route
        )

    def switch_to(self, widget: QWidget):
        """切换到指定页面"""
        self._main_window.switchTo(widget)

    # ---------- 配置访问 API ----------
    def get_config_value(self, key: str):
        """安全地读取配置值(只读)"""
        return getattr(self._config, key, None)

    # ---------- 日志 API ----------
    def log(self, message: str, level: str = "INFO"):
        """记录插件日志"""
        print(f"[Plugin] {level}: {message}")

    # ---------- 插件私有存储 ----------
    def set_data(self, key: str, value: Any):
        """存储插件私有数据(不会持久化)"""
        self._plugin_data[key] = value

    def get_data(self, key: str, default=None):
        """获取插件私有数据"""
        return self._plugin_data.get(key, default)
