"""
子页面:更新( 首选项 的子页面),
此页面包含了程序版本更新的入口和设置项,
引用时可作 SettUpdateUI / settings_update_ui
"""

from PySide2.QtWidgets import (
    QFrame,
    QWidget,
    QLayout,
    QVBoxLayout,
    QHBoxLayout,
)
from qfluentwidgets import (
    TitleLabel,
    SubtitleLabel,
    PrimaryPushButton,
    IndeterminateProgressBar,
    ComboBoxSettingCard,
    OptionsSettingCard,
    IconWidget,
    InfoBarIcon,
)

# from ui.ui_str import SettThemeUIString
from app_config import AppConfig
from fluent_icons import FluentIcons as FI


def set_widget_to_layout(wlist: list, layout: QLayout):
    """设置布局的通用函数"""
    for widget in wlist:
        layout.addWidget(widget)


class UpdateMainArea(QWidget):
    """更新业务主要操作区域, 继承自 QWidget ,
    引用时可作 UpdateArea"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 初始化控件
        self.init_widgets()

        # 初始化垂直布局和内部水平布局
        self.inner_hboxlayout = QHBoxLayout()
        self.vboxlayout = QVBoxLayout()
        self.main_layout = QHBoxLayout(self)

        # 添加控件进布局
        self.inner_hboxlayout.addWidget(self.update_state_indicator)
        self.inner_hboxlayout.addStretch(1)
        self.inner_hboxlayout.addWidget(self.check_update_button)

        self.vboxlayout.addLayout(self.inner_hboxlayout)
        self.vboxlayout.addWidget(self.update_progress)

        # 把所有组件和布局加入总布局
        self.main_layout.addWidget(self.update_state_icon)
        self.main_layout.addLayout(self.vboxlayout)

    def init_widgets(self):
        """初始化控件"""

        # 初始化左侧大号图标
        self.update_state_icon = IconWidget(InfoBarIcon.SUCCESS)
        self.update_state_icon.setFixedSize(64, 64)
        self.update_state_icon.setContentsMargins(4, 4, 4, 4)

        # 初始化状态指示器
        self.update_state_indicator = SubtitleLabel("就绪。")

        # 初始化检查更新按钮
        self.check_update_button = PrimaryPushButton(FI.icon("arrow_sync"), "检查更新")

        # 初始化更新进度条(默认状态为完成)
        self.update_progress = IndeterminateProgressBar(start=False)


class UpdateOptionsArea(QWidget):
    """更新选项, 继承自 QWidget ,
    引用时可作 UpdateOptArea"""

    def __init__(self, cfg: AppConfig, parent=None):
        super().__init__(parent)

        # 初始化配置项
        self.cfg = cfg

        # 初始化控件
        self.init_widgets()

        # 初始化布局
        self.vboxlayout = QVBoxLayout(self)

        # 控件列表
        widgets_list = [self.update_channel_card, self.auto_update_card]

        # 添加控件进布局
        set_widget_to_layout(widgets_list, self.vboxlayout)

    def init_widgets(self):
        """初始化控件"""

        # 首选更新渠道
        self.update_channel_card = OptionsSettingCard(
            self.cfg.UpdateChannel,
            FI.icon("channel"),
            "首选更新渠道",
            "选择更新时检查的渠道",
            ["正式版", "测试版"],
        )

        # 自动更新
        self.auto_update_card = ComboBoxSettingCard(
            self.cfg.AutoUpdateMode,
            FI.icon("cloud_sync"),
            "自动更新",
            "配置自动更新模式",
            ["从不", "仅通知", "下载", "下载并安装"],
        )


class SettUpdateUI(QFrame):
    """子页面: 更新( 首选项 的子页面)的基础UI类,
    此页面包含了程序版本更新的入口和设置项,
    引用时可作 SettUpdateUI / settings_update_ui"""

    def __init__(self, cfg: AppConfig, parent=None):
        super().__init__(parent)

        # 初始化配置项
        self.cfg = cfg

        # 初始化布局
        self.vboxlayout = QVBoxLayout(self)
        self.vboxlayout.setMargin(32)
        self.setLayout(self.vboxlayout)

        # 初始化各控件
        self.frame_title = TitleLabel("Sankteco 更新")
        self.update_main_area = UpdateMainArea(self)
        self.update_options_area = UpdateOptionsArea(self.cfg, self)

        # 控件列表
        widgets_list = [
            self.frame_title,
            self.update_main_area,
            self.update_options_area,
        ]

        # 添加控件进布局
        set_widget_to_layout(widgets_list, self.vboxlayout)
        self.vboxlayout.addStretch(1)
