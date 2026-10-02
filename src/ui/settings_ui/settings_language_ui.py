"""
子页面:语言( 首选项 的子页面),
此页面包含了程序显示语言的可调整设置选项,
引用时可作 SettLangUI / settings_language_ui
"""

from PySide2.QtWidgets import (
    QFrame,
    QLayout,
)
from qfluentwidgets import (
    SubtitleLabel,
    ComboBoxSettingCard,
    HyperlinkCard,
)
from qfluentwidgets import FluentIcon as FI
from app_const_var import WebUrl
from ui.ui_str import SettLangUIString
from app_config import AppConfig


def set_widget_to_layout(wlist: list, layout: QLayout):
    """设置布局的通用函数"""
    for widget in wlist:
        layout.addWidget(widget)


class SettLangUI(QFrame):
    """子页面: 语言( 首选项 的子页面)的基础UI类,
    此页面包含了程序显示语言的可调整设置选项,
    引用时可作 SettLangUI / settings_language_ui"""

    def __init__(self, cfg: AppConfig, parent=None):
        super().__init__(parent)

        from PySide2.QtWidgets import QVBoxLayout
        
        # 初始化配置项
        self.cfg = cfg

        # 初始化垂直布局
        self.vboxlayout = QVBoxLayout(self)
        self.vboxlayout.setMargin(32)

        # 初始化控件
        self.init_widgets()

        # 控件列表
        self.widget_list = [
            self.frame_title,
            self.screen_language,
            self.join_translation,
        ]

        # 设置布局
        set_widget_to_layout(self.widget_list, self.vboxlayout)
        self.vboxlayout.addStretch(1)

    def init_widgets(self):
        """初始化控件"""

        # 页面标题
        self.frame_title = SubtitleLabel(SettLangUIString.FRAME_TITLE)

        # 语言选择
        self.screen_language = ComboBoxSettingCard(
            self.cfg.Language,
            FI.LANGUAGE,
            SettLangUIString.SCREEN_LANGUAGE_TITLE,
            SettLangUIString.SCREEN_LANGUAGE_CONTEXT,
            [
                SettLangUIString.SCREEN_LANGUAGE_TEXT_ZH_CN,
                SettLangUIString.SCREEN_LANGUAGE_TEXT_EO,
            ],
        )

        # 加入翻译计划
        self.join_translation = HyperlinkCard(
            WebUrl.JOIN_TRANSLATION_LINK,
            SettLangUIString.JOIN_TRANSLATION_HYPERLINK_TEXT,
            FI.CLOUD,
            SettLangUIString.JOIN_TRANSLATION_TITLE,
            SettLangUIString.JOIN_TRANSLATION_CONTEXT,
        )
