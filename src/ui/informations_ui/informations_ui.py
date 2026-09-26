"""
子页面：信息,
此页面包含了本项目的相关信息,包含两部分：信息板、支持,
引用时可作 InfoUI / information_ui
"""

from PySide2.QtWidgets import (
    QFrame,
    QVBoxLayout,
)
from PySide2.QtCore import Qt
import qfluentwidgets as qfw
from qfluentwidgets import FluentIcon as FI
from app_const_var import AssetsPathTXT
from ui.ui_str import InfoUIString, BasicString


class ShowInfobar:
    """初始化并显示消息条的类"""

    def offline_button_infobar(self, parent=None):
        """离线帮助文档被点击消息条"""

        self.infobar_offline = qfw.InfoBar.error(
            InfoUIString.SHOWINFOBAR_OFFLINE_TITLE,
            InfoUIString.SHOWINFOBAR_OFFLINE_CONTENT,
            Qt.Horizontal,
            True,
            -1,
            qfw.InfoBarPosition.TOP,
            parent,
        )

    def online_button_infobar(self, parent=None):
        """在线帮助文档被点击消息条"""

        self.infobar_online = qfw.InfoBar.warning(
            InfoUIString.SHOWINFOBAR_ONLINE_TITLE,
            InfoUIString.SHOWINFOBAR_ONLINE_CONTENT,
            Qt.Horizontal,
            True,
            -1,
            qfw.InfoBarPosition.TOP,
            parent,
        )


class InformationBoardCardGroup(qfw.ElevatedCardWidget):
    """信息板 部分,继承自 卡片组件 ElevatedCardWidget
    引用时可作 InfoBodCard"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 项目详细图
        self.app_detailed_image = qfw.ImageLabel(
            AssetsPathTXT.APP_DETAILEDIMAGE_DARK_PATH
        )
        self.app_detailed_image.setBorderRadius(8, 8, 8, 8)
        # 按比例缩放到指定的宽度
        self.app_detailed_image.scaledToWidth(640)

        # 项目信息
        self.infotext_bodylabel = qfw.StrongBodyLabel(BasicString.APP_NAME, self)
        self.infotext_captionlabel = qfw.CaptionLabel(BasicString.APP_COPYTYPE, self)

        # 组件布局
        self.vboxlayout = QVBoxLayout(self)
        self.vboxlayout.addWidget(self.app_detailed_image)
        self.vboxlayout.setAlignment(self.app_detailed_image, Qt.AlignCenter)  # type: ignore
        self.vboxlayout.addWidget(self.infotext_bodylabel)
        self.vboxlayout.addWidget(self.infotext_captionlabel)


class SupportCardGroup(qfw.GroupHeaderCardWidget):
    """支持 部分,继承自 上下分组布局卡片 GroupHeaderCardWidget
    引用时可作 SupptCard"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 选项卡组基本设置
        self.setTitle(InfoUIString.SUPPTCARD_TITLE)
        self.setBorderRadius(8)

        # 帮助文档按钮
        self.offline_document_button = qfw.PushButton(
            icon=FI.DOCUMENT, text=InfoUIString.SUPPTCARD_OFFLINEDOCBUTTON
        )
        self.online_document_button = qfw.PushButton(
            icon=FI.SEARCH, text=InfoUIString.SUPPTCARD_ONLINEDOCBUTTON
        )

        # 添加分组到组件中
        self.addGroup(
            FI.DOCUMENT,
            InfoUIString.SUPPTCARD_OFFLINEDOCGROUPTITLE,
            InfoUIString.SUPPTCARD_OFFLINEDOCGROUPCONTEXT,
            self.offline_document_button,
        )
        group = self.addGroup(
            FI.GLOBE,
            InfoUIString.SUPPTCARD_ONLINEDOCGROUPTITLE,
            InfoUIString.SUPPTCARD_ONLINEDOCGROUPCONTEXT,
            self.online_document_button,
        )
        group.setSeparatorVisible(True)


class InformationUI(QFrame):
    """子页面基础ui类"""

    def __init__(self, parent=None):
        """初始化子页面"""
        super().__init__(parent)

        # 初始化标题与卡片组件
        self.frame_title = qfw.SubtitleLabel(InfoUIString.FRAME_TITLE)
        self.information_board_card = InformationBoardCardGroup(self)
        self.support_card = SupportCardGroup(self)

        # 组件布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setMargin(32)
        self.main_layout.addWidget(self.frame_title)
        self.main_layout.addWidget(self.information_board_card)
        self.main_layout.addWidget(self.support_card)
        self.main_layout.addStretch(1)
