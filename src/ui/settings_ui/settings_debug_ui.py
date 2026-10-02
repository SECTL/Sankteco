"""
子页面:调试选项( 首选项 的子页面),
此页面提供了在程序运行时临时调试部分功能、查看实时日志的门户,
引用时可作 SettDebugUI / settings_debug_ui
"""

from loguru import logger
from PySide2.QtWidgets import (
    QFrame,
    QLayout,
    QVBoxLayout,
)
from PySide2.QtCore import Qt
from qfluentwidgets import (
    qconfig,
    SubtitleLabel,
    TextEdit,
    LineEdit,
    SettingCardGroup,
    SettingCard,
)
from qfluentwidgets import FluentIcon as FI

from ui.ui_str import SettDebugUIString
from ui.log_panel import QtLogSink
from app_config import AppConfig


def set_widget_to_layout(wlist: list, layout: QLayout):
    """设置布局的通用函数"""
    for widget in wlist:
        layout.addWidget(widget)


class IntSettingCard(SettingCard):
    """带单行输入框的设置卡，绑定到整数类型的 ConfigItem"""

    def __init__(self, configItem, icon: FI, title: str, content=None, parent=None):
        super().__init__(icon, title, content, parent)

        self.configItem = configItem

        # 创建输入框
        self.lineEdit = LineEdit(self)
        self.lineEdit.setFixedWidth(120)
        self.lineEdit.setClearButtonEnabled(True)

        # 插入到卡片右侧
        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.lineEdit, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        # 双向绑定
        # 配置 -> UI:配置值变化时更新输入框
        self.configItem.valueChanged.connect(self.setValue)
        # UI -> 配置:用户编辑后写回配置项
        self.lineEdit.textChanged.connect(self._onTextChanged)

        # 用当前配置值初始化 UI
        self.setValue(self.configItem.value)

    def setValue(self, value):
        """配置值变化时更新输入框显示（阻止信号循环）"""
        self.lineEdit.blockSignals(True)
        self.lineEdit.setText(str(value))
        self.lineEdit.blockSignals(False)

    def _onTextChanged(self, text: str):
        """用户编辑后写回配置项"""
        if text.strip():
            try:
                qconfig.set(self.configItem, int(text))
            except ValueError:
                pass  # 非法输入暂不写回，由 validator 在保存时修正


class SettDebugUI(QFrame):
    """子页面:调试选项( 首选项 的子页面)的基础UI类,
    此页面提供了在程序运行时临时调试部分功能、查看实时日志的门户,
    引用时可作 SettDebugUI / settings_debug_ui"""

    def __init__(self, cfg: AppConfig, parent=None):
        super().__init__(parent)

        # 初始化配置项
        self.cfg = cfg

        # 用于管理 sink 的引用(初始为 None)
        self.qt_sink: QtLogSink = None  # type: ignore

        # 初始化垂直布局
        self.vboxlayout = QVBoxLayout(self)
        self.vboxlayout.setMargin(32)

        # 初始化各控件
        self.init_widgets()

        # 控件列表
        self.widget_list = [
            self.frame_title,
            self.log_display,
            self.log_settcard_group,
        ]

        # 设置布局
        set_widget_to_layout(self.widget_list, self.vboxlayout)
        self.vboxlayout.addStretch(1)

        # 控件就绪后挂载 UI sink
        self._attach_sink()

        # 对象销毁时卸载 sink,避免往已销毁的控件写日志
        self.destroyed.connect(self._detach_sink)
        
        # 链接信号
        self.cfg.LogFileRetention.valueChanged.connect(self._on_log_retention_changed)
        self.cfg.ErrorLogFileRetention.valueChanged.connect(self._on_log_retention_changed)

    def init_widgets(self):
        """初始化控件"""

        # 页面标题
        self.frame_title = SubtitleLabel(SettDebugUIString.FRAME_TITLE)

        # 日志实时窗口
        self.log_display = TextEdit()
        self.log_display.setReadOnly(True)

        # 日志 组
        # 日志文件保留时长(天)
        self.log_file_retention = IntSettingCard(
            self.cfg.LogFileRetention,
            FI.HISTORY,
            "日志文件保留时长(天)",
            "键入一个整数以确定一般日志文件的最大保留时长(以天为单位)",
        )

        # 错误日志文件保留时长(天)
        self.error_log_file_retention = IntSettingCard(
            self.cfg.ErrorLogFileRetention,
            FI.HISTORY,
            "错误日志文件保留时长(天)",
            "键入一个整数以确定错误日志文件的最大保留时长(以天为单位)",
        )

        # 日志卡片组
        self.log_settcard_group = SettingCardGroup("日志")
        self.log_settcard_group.addSettingCards(
            [self.log_file_retention, self.error_log_file_retention]
        )

    def _attach_sink(self):
        """挂载 Qt sink,开始接收实时日志"""

        self.qt_sink = QtLogSink(self.log_display)
        self.qt_sink.attach(level="DEBUG")  # 调试页面放开到 DEBUG
        logger.info("调试页面已打开,开始接收实时日志")

    def _detach_sink(self, *_):
        """卸载 Qt sink(在控件销毁时调用)"""

        if self.qt_sink is not None:
            self.qt_sink.detach()
            self.qt_sink = None
            logger.info("调试页面已销毁,停止接收实时日志")
            
    def _on_log_retention_changed(self, *_):
        """配置变化后,重建文件 sink"""
        
        from logger_config import reconfigure_file_sinks
        reconfigure_file_sinks(
            log_days=self.cfg.get(self.cfg.LogFileRetention),
            err_days=self.cfg.get(self.cfg.ErrorLogFileRetention),
        )
