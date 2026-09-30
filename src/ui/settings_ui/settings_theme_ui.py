"""
子页面:主题( 首选项 的子页面),
此页面包含了程序显示主题的所有可调整设置选项,
引用时可作 SettThemeUI / settings_theme_ui
"""

from PySide2.QtWidgets import (
    QFrame,
    QLayout,
    QVBoxLayout,
)
from qfluentwidgets import (
    SubtitleLabel,
    ComboBoxSettingCard,
    ColorSettingCard,
    qconfig,
)
from qfluentwidgets import FluentIcon as FI
from ui.ui_str import SettThemeUIString
from app_config import AppConfig


def set_widget_to_layout(wlist: list, layout: QLayout):
    """设置布局的通用函数"""
    for widget in wlist:
        layout.addWidget(widget)


class SettThemeUI(QFrame):
    """子页面: 主题( 首选项 的子页面)的基础UI类,
    此页面包含了程序显示主题的所有可调整设置选项,
    引用时可作 SettThemeUI / settings_theme_ui"""

    def __init__(self, cfg: AppConfig, parent=None):
        super().__init__(parent)

        # 初始化配置项
        self.cfg = cfg

        # 初始化垂直布局
        self.vboxlayout = QVBoxLayout(self)
        self.vboxlayout.setMargin(32)

        # 初始化各控件
        self.init_widgets()

        # 控件列表
        self.widget_list = [
            self.frame_title,
            self.theme_card,
            self.theme_color_card,
        ]

        # 设置布局
        set_widget_to_layout(self.widget_list, self.vboxlayout)
        self.vboxlayout.addStretch(1)

    def init_widgets(self):
        """初始化控件"""

        # 页面标题
        self.frame_title = SubtitleLabel(SettThemeUIString.FRAME_TITLE)

        # 显示主题
        self.theme_card = ComboBoxSettingCard(
            qconfig.themeMode,
            FI.CONSTRACT,
            SettThemeUIString.THEME_CARD_TITLE,
            SettThemeUIString.THEME_CARD_CONTEXT,
            texts=[
                SettThemeUIString.THEME_CARD_TEXT_LIGHT,
                SettThemeUIString.THEME_CARD_TEXT_DARK,
                SettThemeUIString.THEME_CARD_TEXT_AUTO,
            ],
        )
        
        # 主题色
        self.theme_color_card = ColorSettingCard(
            qconfig.themeColor,
            FI.BRUSH,
            SettThemeUIString.THEME_COLOR_CARD_TITLE,
            SettThemeUIString.THEME_COLOR_CARD_CONTEXT,
        )
