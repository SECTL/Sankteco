"""
页面:文档阅读,
此页面用于在程序内阅读文档,
引用时可作 DocsRUI / docs_reader_ui
"""

from PySide2.QtWidgets import QVBoxLayout
import qfluentwidgets as qfw
from qfluentwidgets import FluentIcon as FI
from ui.ui_str import DocsRUIString


class NowDocCard(qfw.SettingCard):
    """当前文档 卡片, 从属于 文档阅读 部分,
    继承自 设置卡基类 SettingCard,
    引用时可作 NowDocCard"""

    def __init__(self, parent=None):
        super().__init__(
            FI.DOCUMENT,
            DocsRUIString.NOW_DOC_CARD_TITLE,
            DocsRUIString.NOW_DOC_CARD_CONTEXT,
            parent,
        )

        # 下拉框
        self.now_doc_card_list = qfw.ComboBox()

        # 调整布局边距、添加控件进布局
        self.hBoxLayout.setMargin(16)
        self.hBoxLayout.addWidget(self.now_doc_card_list)


class DocsRUI(qfw.FluentWidget):
    """页面:文档阅读的基础UI类,
    此页面用于在程序内阅读文档,
    引用时可作 DocsRUI / docs_reader_ui"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 页面布局
        self.vboxlayout = QVBoxLayout(self)

        # 初始化控件
        self.init_widgets()

        # 添加控件进布局
        self.vboxlayout.addWidget(self.docs_combobox)
        self.vboxlayout.addWidget(self.docs_browser)
        self.setLayout(self.vboxlayout)

        # 留出标题栏的空间
        self.vboxlayout.setContentsMargins(8, self.titleBar.height(), 8, 8)  # type: ignore

        # 设置窗口属性
        self.resize(640, 480)
        self.setWindowTitle(DocsRUIString.DOCSRUI_TITLE)

    def init_widgets(self):
        """初始化控件"""

        # 文档选择下拉框
        self.docs_combobox = NowDocCard(self)

        # 绑定文本与预留值
        self.docs_combobox.now_doc_card_list.addItem("README", userData="README")

        # 文档阅读多行编辑器
        self.docs_browser = qfw.TextBrowser()
