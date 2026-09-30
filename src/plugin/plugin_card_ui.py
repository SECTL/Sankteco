"""
插件卡片组件

提供两种卡片:
1. PluginCard - 已安装插件的管理卡片
2. OnlinePluginCard - 在线插件的安装卡片
"""

from __future__ import annotations

from typing import Optional, Dict
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QWidget
from qfluentwidgets import (
    SettingCard,
    FluentIcon,
    PushButton,
    SwitchButton,
    ToolTipFilter,
    PrimaryPushButton,
    BodyLabel,
    ProgressRing,
)


class PluginCard(SettingCard):
    """
    已安装插件信息卡片
    使用 QFW 组件,无固定宽度
    """

    uninstall_requested = Signal(str)
    toggle_requested = Signal(str, bool)

    def __init__(
        self,
        plugin_id: str,
        name: str,
        version: str,
        description: str,
        author: str,
        icon: str,
        is_active: bool = True,
        parent: Optional[QWidget] = None,
    ):
        try:
            icon_enum = getattr(FluentIcon, icon.upper(), FluentIcon.APPLICATION)
        except:
            icon_enum = FluentIcon.APPLICATION

        super().__init__(icon_enum, name, description, parent)

        self.plugin_id = plugin_id
        self.is_active = is_active

        # 版本信息(使用 BodyLabel)
        self.version_label = BodyLabel(f"v{version}")
        self.version_label.setObjectName("plugin_version_label")

        # 作者信息
        self.author_label = BodyLabel(author)
        self.author_label.setObjectName("plugin_author_label")

        # 分隔符
        self.separator_label = BodyLabel(" " + "|" + " ")
        self.separator_label.setObjectName("plugin_separator")

        # 启用/禁用开关
        self.toggle_btn = SwitchButton(self)
        self.toggle_btn.setChecked(is_active)
        self.toggle_btn.checkedChanged.connect(self._on_toggle)

        # 卸载按钮(无固定宽度)
        self.uninstall_btn = PushButton(FluentIcon.DELETE, "卸载", self)
        self.uninstall_btn.clicked.connect(self._on_uninstall)

        # 添加到布局
        self.hBoxLayout.setMargin(16)
        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.version_label)
        self.hBoxLayout.addWidget(self.separator_label)
        self.hBoxLayout.addWidget(self.author_label)
        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.toggle_btn)
        self.hBoxLayout.addWidget(self.uninstall_btn)

        self.installEventFilter(ToolTipFilter(self))

    def _on_toggle(self, checked: bool) -> None:
        self.is_active = checked
        self.toggle_requested.emit(self.plugin_id, checked)

    def _on_uninstall(self) -> None:
        self.uninstall_requested.emit(self.plugin_id)

    def set_active(self, active: bool) -> None:
        self.is_active = active
        self.toggle_btn.setChecked(active)


class OnlinePluginCard(SettingCard):
    """
    在线插件信息卡片
    包含进度环反馈,不使用固定宽度
    """

    install_requested = Signal(str)
    update_requested = Signal(str)

    def __init__(
        self,
        plugin_info: Dict,
        is_installed: bool,
        has_update: bool,
        parent: Optional[QWidget] = None,
    ):
        plugin_id = plugin_info.get("id", "")
        name = plugin_info.get("name", "未命名插件")
        description = plugin_info.get("description", "")
        author = plugin_info.get("author", "未知")
        icon = plugin_info.get("icon", "APPLICATION")
        version = plugin_info.get("version", "1.0.0")

        try:
            icon_enum = getattr(FluentIcon, icon.upper(), FluentIcon.APPLICATION)
        except:
            icon_enum = FluentIcon.APPLICATION

        super().__init__(icon_enum, name, description, parent)

        self.plugin_id = plugin_id
        self.plugin_info = plugin_info
        self.is_installed = is_installed
        self.has_update = has_update
        self._is_installing = False

        # 版本信息
        self.version_label = BodyLabel(f"v{version}")
        self.version_label.setObjectName("plugin_version_label")

        # 作者信息
        self.author_label = BodyLabel(author)
        self.author_label.setObjectName("plugin_author_label")

        # 分隔符
        self.separator_label = BodyLabel(" " + "|" + " ")
        self.separator_label.setObjectName("plugin_separator")

        # 进度环(默认隐藏)
        self.progress_ring = ProgressRing(self)
        self.progress_ring.setVisible(False)
        self.progress_ring.setFixedSize(24, 24)

        # 操作按钮(无固定宽度)
        self.action_btn = self._create_action_button()

        # 添加到布局
        self.hBoxLayout.setMargin(16)
        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.version_label)
        self.hBoxLayout.addWidget(self.separator_label)
        self.hBoxLayout.addWidget(self.author_label)
        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.progress_ring)
        self.hBoxLayout.addWidget(self.action_btn)

        self.installEventFilter(ToolTipFilter(self))

    def _create_action_button(self):
        """根据状态创建操作按钮"""
        if self.has_update:
            btn = PrimaryPushButton("更新", self)
            btn.clicked.connect(self._on_update)
            return btn
        elif self.is_installed:
            btn = PushButton("已安装", self)
            btn.setEnabled(False)
            return btn
        else:
            btn = PrimaryPushButton("安装", self)
            btn.clicked.connect(self._on_install)
            return btn

    def _on_install(self) -> None:
        if self._is_installing:
            return
        self._is_installing = True
        self.action_btn.setVisible(False)
        self.progress_ring.setVisible(True)
        self.progress_ring.setValue(0)
        self.install_requested.emit(self.plugin_id)

    def _on_update(self) -> None:
        if self._is_installing:
            return
        self._is_installing = True
        self.action_btn.setVisible(False)
        self.progress_ring.setVisible(True)
        self.progress_ring.setValue(0)
        self.update_requested.emit(self.plugin_id)

    def update_progress(self, value: int) -> None:
        """
        更新进度环
        :param value: 0-100
        """
        if value < 0:
            # 安装失败,恢复按钮状态
            self._is_installing = False
            self.progress_ring.setVisible(False)
            self.action_btn.setVisible(True)
            return
        elif value >= 100:
            # 安装完成,恢复按钮状态
            self._is_installing = False
            self.progress_ring.setVisible(False)
            self.action_btn.setVisible(True)
            # 更新为"已安装"状态
            self.is_installed = True
            self.has_update = False
            self.action_btn = PushButton("已安装", self)
            self.action_btn.setEnabled(False)
            # 替换布局中的按钮
            self._replace_action_button()
        else:
            self.progress_ring.setValue(value)

    def _replace_action_button(self) -> None:
        """替换操作按钮(安装完成后由进度环切换为"已安装"按钮)"""
        # 移除旧的按钮
        self.hBoxLayout.removeWidget(self.action_btn)
        self.action_btn.deleteLater()
        # 创建新按钮
        new_btn = PushButton("已安装", self)
        new_btn.setEnabled(False)
        self.action_btn = new_btn
        # 插入到进度环后面
        idx = self.hBoxLayout.indexOf(self.progress_ring)
        self.hBoxLayout.insertWidget(idx + 1, new_btn)

    def set_installing_state(self, is_installing: bool) -> None:
        """外部设置安装状态(用于恢复)"""
        self._is_installing = is_installing
