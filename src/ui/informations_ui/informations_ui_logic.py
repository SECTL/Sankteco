"""
子页面信息的UI逻辑文件, 
引用时可作 InfoUILogic / information_ui_logic
"""

from PySide2.QtCore import Qt

from ui.informations_ui.informations_ui import ShowInfobar, InformationUI
from ui.docs_reader_ui.docs_reader_ui_logic import DocsRUILogic


class InformationUILogic(InformationUI):
    """孙页面:基本( 首选项 的子页面)的UI基础逻辑类,
    引用时可作 SettBasicUILogic / subsubpage_setting_basic_ui_logic"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 保存引用
        self.docs_reader_ui = None

        # 初始化信号连接函数
        self.signal_connection()

    def signal_connection(self):
        """信号连接函数"""

        # 连接 支持 部分帮助文档按钮点击信号
        self.support_card.offline_document_button.clicked.connect(  # type: ignore
            self.open_docs_reader_ui
        )
        self.support_card.online_document_button.clicked.connect(  # type: ignore
            lambda: ShowInfobar.online_button_infobar(self, self)  # type: ignore
        )

    def open_docs_reader_ui(self):
        """打开文档阅读器UI"""

        # 如果窗口已经存在且未关闭, 则激活它
        if self.docs_reader_ui is not None:
            self.docs_reader_ui.raise_()
            self.docs_reader_ui.activateWindow()
            return

        # 创建时不传入父对象
        docs_reader_ui = DocsRUILogic()

        # 设为独立无边框窗口
        docs_reader_ui.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)  # type: ignore

        # 关闭时自动删除
        docs_reader_ui.setAttribute(Qt.WA_DeleteOnClose)  # type: ignore

        # 窗口销毁时清空引用
        docs_reader_ui.destroyed.connect(self._on_docs_reader_destroyed)  # type: ignore

        # 初始化图标
        docs_reader_ui.setWindowIcon(self.windowIcon())

        # 保存引用
        self.docs_reader_ui = docs_reader_ui

        # 显示窗口
        docs_reader_ui.show()

    def _on_docs_reader_destroyed(self):
        """文档阅读器UI销毁时清空引用"""

        self.docs_reader_ui = None
