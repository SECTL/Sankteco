"""
Fluent UI regular 图标加载器,
只读取 microsoft/fluentui-system-icons 的 regular SVG,
通过 QIconEngine 让所有已分发的 QIcon 自动跟随主题.
使用方式 (任意文件,免初始化):\n
    from fluent_icons import FluentIcons as FI\n
    button.setIcon(FI.icon("add"))
"""

import re
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple

from PySide2.QtCore import QByteArray, QSize, Qt
from PySide2.QtGui import QIcon, QIconEngine, QPainter, QPixmap
from PySide2.QtSvg import QSvgRenderer


# 匹配 SVG 中除 fill="none" 之外的填充色属性
_FILL_RE = re.compile(r'fill="(?!none)([^"]*)"')


def _default_theme_provider() -> bool:
    """默认主题探测,优先使用 QFW 的 isDarkTheme,失败时退化为浅色"""
    try:
        # 延迟导入,避免模块级硬依赖 QFW
        from qfluentwidgets import isDarkTheme

        return bool(isDarkTheme())
    except Exception:
        # QFW 不可用时按浅色处理
        return False


class _FluentIconEngine(QIconEngine):
    """主题感知的 QIconEngine,
    持有同一 engine 的所有 QIcon 自动共享 pixmap 缓存,
    主题切换后 QIcon 无需重新 setIcon 即可在下一次重绘时自动生效"""

    def __init__(self, loader: "FluentIconLoader", name: str) -> None:
        """记录 loader 与图标名,并初始化按主题分组的 pixmap 缓存"""
        super().__init__()
        self._loader = loader
        self._name = name
        # 缓存键为:(宽,高,是否深色)
        self._cache: Dict[Tuple[int, int, bool], QPixmap] = {}

    def clone(self) -> "QIconEngine":
        """QIcon 复制时调用,返回同等 engine"""
        return _FluentIconEngine(self._loader, self._name)

    def pixmap(self, size: QSize, mode, state) -> QPixmap:
        """按当前主题渲染指定尺寸的 pixmap 并写入缓存"""
        # 每次重绘都重新查询主题,保证自动跟随
        is_dark = self._loader.current_theme()
        key = (size.width(), size.height(), is_dark)
        pm = self._cache.get(key)
        if pm is None:
            pm = self._loader._render(self._name, size, is_dark)
            self._cache[key] = pm
        return pm

    def paint(self, painter: QPainter, rect, mode, state) -> None:
        """把当前 pixmap 绘制到目标矩形上"""
        painter.drawPixmap(rect, self.pixmap(rect.size(), mode, state))

    def actualSize(self, size: QSize, mode, state) -> QSize:
        """返回请求的原始尺寸,不做任何放大"""
        return size

    def clear_cache(self) -> None:
        """清空该 engine 的 pixmap 缓存"""
        self._cache.clear()


class FluentIconLoader:
    """Fluent regular 图标加载器,
    读取目录下的 ic_fluent_{name}_24_regular.svg,
    根据当前主题 (浅色 / 深色) 替换填充色后用 QSvgRenderer 渲染成 QPixmap,
    再封装为跟随主题自动变化的 QIcon.
    支持两种主题来源:\n
       theme_provider 为 None (默认) 时,自动查询 qfluentwidgets.isDarkTheme,\n
        也可以传入自定义的可调用对象,返回 True 表示深色主题"""

    def __init__(
        self,
        icon_dir: Path = Path(__file__).parent.parent / "assets" / "icons",
        theme_provider: Optional[Callable[[], bool]] = None,
        light_color: str = "#212121",
        dark_color: str = "#ffffff",
    ) -> None:
        """建立加载器并保存主题与颜色配置"""

        self.icon_dir = Path(icon_dir)
        self.theme_provider = theme_provider or _default_theme_provider
        self.light_color = light_color
        self.dark_color = dark_color
        # 为 None 表示自动跟随 theme_provider
        self._forced_theme: Optional[bool] = None
        # 同一图标名复用同一 engine 避免重复创建
        self._engines: Dict[str, _FluentIconEngine] = {}

    def current_theme(self) -> bool:
        """返回当前是否处于深色主题"""

        # 优先返回手动强制值
        if self._forced_theme is not None:
            return self._forced_theme
        return bool(self.theme_provider())

    def set_theme(self, is_dark: Optional[bool]) -> None:
        """强制指定主题 (True 深色 / False 浅色),传入 None 恢复自动跟随"""

        self._forced_theme = is_dark
        # 强制切换后旧缓存失效
        self.clear_cache()

    def icon(self, name: str) -> QIcon:
        """返回一个会自动跟随主题变化的 QIcon,同一名称复用同一 engine"""

        engine = self._engines.get(name)
        if engine is None:
            engine = _FluentIconEngine(self, name)
            self._engines[name] = engine
        return QIcon(engine)

    def clear_cache(self) -> None:
        """清空所有 engine 的 pixmap 缓存"""

        for engine in self._engines.values():
            engine.clear_cache()

    def _render(self, name: str, size: QSize, is_dark: bool) -> QPixmap:
        """按当前主题颜色,把 regular SVG 渲染成指定尺寸的 QPixmap"""

        # 统一按 24 尺寸的 regular SVG 命名定位
        path = self.icon_dir / "ic_fluent_{}_24_regular.svg".format(name)
        if not path.exists():
            raise FileNotFoundError("未找到 Fluent regular 图标: {}".format(path))

        # 依主题选择填充色
        color = self.dark_color if is_dark else self.light_color
        svg_text = path.read_text(encoding="utf-8")
        # 把非 none 的 fill 统一替换为主题色
        recolored = _FILL_RE.sub('fill="{}"'.format(color), svg_text)
        renderer = QSvgRenderer(QByteArray(recolored.encode("utf-8")))

        # 至少保证 1 像素,避免空 QPixmap
        w = max(1, size.width())
        h = max(1, size.height())
        pm = QPixmap(w, h)
        pm.fill(Qt.transparent)

        # 开启抗锯齿与平滑缩放,保证小尺寸下边缘干净
        painter = QPainter(pm)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        renderer.render(painter)
        painter.end()
        return pm


class FluentIcons:
    """全局 Fluent regular 图标入口,
    所有 API 均为类方法 通过 cls._loader 访问单例"""

    _loader = FluentIconLoader()

    @classmethod
    def icon(cls, name: str) -> QIcon:
        """返回跟随主题自动变化的 Fluent regular 图标"""

        return cls._loader.icon(name)

    @classmethod
    def set_theme(cls, is_dark: Optional[bool]) -> None:
        """全局强制主题,传入 None 恢复自动跟随 QFW"""

        cls._loader.set_theme(is_dark)

    @classmethod
    def clear_cache(cls) -> None:
        """清空全局图标 pixmap 缓存"""

        cls._loader.clear_cache()

    @classmethod
    def configure_loader(cls, loader: "FluentIconLoader") -> None:
        """替换全局 loader 便于测试或多环境切换"""

        cls._loader = loader
