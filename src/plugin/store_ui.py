"""
插件商店页面

提供插件管理界面,包含两个标签页:
1. 已安装:显示本地已安装的插件列表,支持启用/禁用/卸载
2. 在线插件:从远程索引获取可用插件列表,支持安装/更新
"""

from __future__ import annotations

from typing import Optional, List, Dict
from PySide2.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from PySide2.QtCore import Qt, Signal
from qfluentwidgets import (
    FluentIcon,
    SubtitleLabel,
    SubtitleLabel,
    PrimaryPushButton,
    InfoBar,
    ScrollArea,
    Pivot,
)
from .signals import plugin_signals

from .loader import PluginLoader
from .plugin_card_ui import PluginCard, OnlinePluginCard


class PluginStorePage(QWidget):
    """
    插件商店页面
    展示已安装的插件列表和在线插件列表
    """

    # ===== 信号定义 =====
    plugin_toggle_requested = Signal(str, bool)  # 启用/禁用请求
    plugin_uninstall_requested = Signal(str)  # 卸载请求
    plugin_install_requested = Signal(str)  # 安装请求
    plugin_update_requested = Signal(str)  # 更新请求

    def __init__(self, loader: PluginLoader, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.loader = loader
        self._cards: Dict[str, PluginCard] = {}
        self._online_cards: Dict[str, OnlinePluginCard] = {}
        self._remote_plugins: List[Dict] = []
        self._online_loaded = False  # 在线插件是否已加载

        self._setup_ui()
        self._refresh_plugin_list()

    def _setup_ui(self) -> None:
        """初始化UI布局"""
        from PySide2.QtWidgets import QHBoxLayout

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 30, 40, 30)
        self.main_layout.setSpacing(20)

        # 标题行(标题 + 刷新按钮)
        title_layout = QHBoxLayout()
        self.title_label = SubtitleLabel("插件商店", self)
        self.title_label.setObjectName("store_title")
        title_layout.addWidget(self.title_label)

        title_layout.addStretch()

        self.global_refresh_btn = PrimaryPushButton(FluentIcon.UPDATE, "刷新全部", self)
        self.global_refresh_btn.clicked.connect(self._on_global_refresh)
        title_layout.addWidget(self.global_refresh_btn)

        self.main_layout.addLayout(title_layout)

        # Pivot 导航
        self.pivot = Pivot(self)
        self.stacked_widget = QStackedWidget(self)

        # 创建两个标签页
        self.installed_tab = self._create_installed_tab()
        self.online_tab = self._create_online_tab()

        self.stacked_widget.addWidget(self.installed_tab)
        self.stacked_widget.addWidget(self.online_tab)

        # 添加到 Pivot
        self.pivot.addItem(
            routeKey="installed",
            text="已安装",
            onClick=lambda: self.stacked_widget.setCurrentWidget(self.installed_tab),
        )
        self.pivot.addItem(
            routeKey="online", text="在线插件", onClick=self._on_online_tab_selected
        )

        # 默认选中已安装
        self.stacked_widget.setCurrentWidget(self.installed_tab)
        self.pivot.setCurrentItem("installed")

        # 连接切换信号(更新副标题)
        self.stacked_widget.currentChanged.connect(self._on_tab_changed)

        self.main_layout.addWidget(self.pivot)
        self.main_layout.addWidget(self.stacked_widget)

    def _create_installed_tab(self) -> QWidget:
        """创建"已安装"标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 10, 0, 10)

        self.subtitle_label = SubtitleLabel("已安装的插件", self)
        layout.addWidget(self.subtitle_label)

        self.scroll_area = ScrollArea(self)
        self.scroll_area.setObjectName("plugin_store_scroll_area")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(
            "QScrollArea{background: transparent; border: none}"
        )

        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("plugin_store_scroll_content")
        self.scroll_content.setStyleSheet("QWidget{background: transparent}")

        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(12)
        self.scroll_layout.setContentsMargins(0, 10, 0, 20)
        self.scroll_layout.addStretch()

        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)

        return widget

    def _create_online_tab(self) -> QWidget:
        """创建"在线插件"标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 10, 0, 10)

        self.online_subtitle_label = SubtitleLabel("在线插件", self)
        layout.addWidget(self.online_subtitle_label)

        self.online_scroll_area = ScrollArea(self)
        self.online_scroll_area.setObjectName("online_plugin_scroll_area")
        self.online_scroll_area.setWidgetResizable(True)
        self.online_scroll_area.setStyleSheet(
            "QScrollArea{background: transparent; border: none}"
        )

        self.online_scroll_content = QWidget()
        self.online_scroll_content.setObjectName("online_plugin_scroll_content")
        self.online_scroll_content.setStyleSheet("QWidget{background: transparent}")

        self.online_scroll_layout = QVBoxLayout(self.online_scroll_content)
        self.online_scroll_layout.setSpacing(12)
        self.online_scroll_layout.setContentsMargins(0, 10, 0, 20)
        self.online_scroll_layout.addStretch()

        self.online_scroll_area.setWidget(self.online_scroll_content)
        layout.addWidget(self.online_scroll_area)

        return widget

    def _on_online_tab_selected(self) -> None:
        """在线标签被选中时触发,延迟加载远程索引"""
        if not self._online_loaded:
            self._fetch_online_plugins()
        # 切换到在线标签页
        self.stacked_widget.setCurrentWidget(self.online_tab)

    def _on_tab_changed(self, index: int) -> None:
        """标签切换时更新副标题"""
        if index == 0:
            count = len(self.loader.get_all_plugin_ids())
            self.subtitle_label.setText(f"已安装的插件 ({count})")
        else:
            count = len(self._remote_plugins)
            self.online_subtitle_label.setText(f"在线插件 ({count})")

    def _on_global_refresh(self) -> None:
        """全局刷新:刷新已安装列表和在线列表"""
        self._refresh_plugin_list()
        self._online_loaded = False  # 重置状态,强制重新拉取
        self._fetch_online_plugins()
        InfoBar.success(
            title="刷新完成", content="已更新插件列表", parent=self, duration=1500
        )

    def _refresh_plugin_list(self) -> None:
        """刷新已安装插件列表"""
        self._cards.clear()
        while self.scroll_layout.count() > 1:
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        plugin_ids = self.loader.get_all_plugin_ids()

        if not plugin_ids:
            empty_label = SubtitleLabel("暂无已安装的插件", self)
            empty_label.setAlignment(Qt.AlignCenter)  # type: ignore
            empty_label.setObjectName("empty_label")
            self.scroll_layout.insertWidget(0, empty_label)
            self.subtitle_label.setText("已安装的插件 (0)")
            return

        self.subtitle_label.setText(f"已安装的插件 ({len(plugin_ids)})")

        for plugin_id in plugin_ids:
            meta = self.loader.get_plugin_meta(plugin_id)
            is_enabled = self.loader.is_plugin_enabled(plugin_id)

            if is_enabled is None:
                is_enabled = True

            card = PluginCard(
                plugin_id=plugin_id,
                name=meta.get("name", plugin_id),
                version=meta.get("version", "1.0.0"),
                description=meta.get("description", ""),
                author=meta.get("author", "未知"),
                icon=meta.get("icon", "APPLICATION"),
                is_active=is_enabled,
                parent=self,
            )
            card.uninstall_requested.connect(self._on_uninstall_requested)
            card.toggle_requested.connect(self._on_toggle_requested)

            self._cards[plugin_id] = card
            self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, card)

        self._sync_all_card_states()

    def _fetch_online_plugins(self) -> None:
        """拉取远程插件列表并显示"""
        self._remote_plugins = self.loader.fetch_remote_index()
        self._online_loaded = True

        self._online_cards.clear()
        while self.online_scroll_layout.count() > 1:
            item = self.online_scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self._remote_plugins:
            empty_label = SubtitleLabel("无法获取在线插件列表", self)
            empty_label.setAlignment(Qt.AlignCenter)  # type: ignore
            empty_label.setObjectName("empty_label")
            self.online_scroll_layout.insertWidget(0, empty_label)
            self.online_subtitle_label.setText("在线插件 (0)")
            InfoBar.warning(
                title="提示",
                content="获取在线插件列表失败,请检查网络连接",
                parent=self,
                duration=3000,
            )
            return

        self.online_subtitle_label.setText(f"在线插件 ({len(self._remote_plugins)})")

        installed_ids = set(self.loader.get_all_plugin_ids())

        for plugin_info in self._remote_plugins:
            plugin_id = plugin_info.get("id")
            if not plugin_id:
                continue

            is_installed = plugin_id in installed_ids
            has_update = False
            if is_installed:
                local_meta = self.loader.get_plugin_meta(plugin_id)
                local_gen = local_meta.get("generation", 0)
                remote_gen = plugin_info.get("generation", 0)
                has_update = remote_gen > local_gen

            card = OnlinePluginCard(
                plugin_info=plugin_info,
                is_installed=is_installed,
                has_update=has_update,
                parent=self,
            )
            card.install_requested.connect(self._on_install_requested)
            card.update_requested.connect(self._on_update_requested)

            self._online_cards[plugin_id] = card
            self.online_scroll_layout.insertWidget(
                self.online_scroll_layout.count() - 1, card
            )

    # ===== 状态同步 =====

    def _sync_all_card_states(self) -> None:
        """强制同步所有卡片状态"""
        for plugin_id, card in self._cards.items():
            is_enabled = self.loader.is_plugin_enabled(plugin_id)
            if is_enabled is None:
                is_enabled = True
            card.set_active(is_enabled)

    def _update_card_state(self, plugin_id: str, is_active: bool) -> None:
        """更新指定卡片的状态"""
        card = self._cards.get(plugin_id)
        if card:
            card.set_active(is_active)

    def refresh_online_list(self) -> None:
        """外部调用刷新在线列表"""
        self._online_loaded = False
        self._fetch_online_plugins()

    # ===== 信号转发 =====

    def _on_toggle_requested(self, plugin_id: str, enable: bool) -> None:
        """转发启用/禁用请求"""
        self.plugin_toggle_requested.emit(plugin_id, enable)

    def _on_uninstall_requested(self, plugin_id: str) -> None:
        """转发卸载请求"""
        self.plugin_uninstall_requested.emit(plugin_id)

    def _on_update_requested(self, plugin_id: str) -> None:
        """处理更新请求"""
        # 先卸载
        self.loader.uninstall_plugin(plugin_id)
        # 再安装(复用安装逻辑)
        self._on_install_requested(plugin_id)

    def _on_install_requested(self, plugin_id: str) -> None:
        """处理安装请求,进度反馈融入卡片"""
        plugin_info = None
        for p in self._remote_plugins:
            if p.get("id") == plugin_id:
                plugin_info = p
                break

        if not plugin_info:
            InfoBar.error(
                title="错误", content="未找到插件信息", parent=self, duration=2000
            )
            return

        # 获取对应的卡片
        card = self._online_cards.get(plugin_id)
        if card:
            card.set_installing_state(True)

        # 连接进度信号
        def on_progress(value: int):
            if card:
                card.update_progress(value)
            if value < 0:
                # 错误处理
                InfoBar.error(
                    title="安装失败",
                    content=f"无法安装插件「{plugin_info.get('name')}」",
                    parent=self,
                    duration=3000,
                )
                plugin_signals.install_progress.disconnect(on_progress)

        plugin_signals.install_progress.connect(on_progress)

        try:
            success = self.loader.install_remote_plugin(plugin_info)
            if success:
                InfoBar.success(
                    title="安装成功",
                    content=f"插件「{plugin_info.get('name')}」已安装",
                    parent=self,
                    duration=2000,
                )
                self._refresh_plugin_list()
                self._online_loaded = False
                self._fetch_online_plugins()
                self.plugin_install_requested.emit(plugin_id)
            else:
                InfoBar.error(
                    title="安装失败",
                    content=f"无法安装插件「{plugin_info.get('name')}」",
                    parent=self,
                    duration=3000,
                )
        finally:
            plugin_signals.install_progress.disconnect(on_progress)
