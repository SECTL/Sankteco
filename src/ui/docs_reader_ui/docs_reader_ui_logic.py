"""
页面：文档阅读的UI逻辑文件, 
引用时可作 DocsRUILogic / docs_reader_ui_logic
"""

from ui.docs_reader_ui.docs_reader_ui import DocsRUI


class DocsRUILogic(DocsRUI):
    """页面：文档阅读的UI逻辑类
    引用时可作 DocsRUILogic / docs_reader_ui_logic"""

    def __init__(self, parent=None):
        super().__init__(parent)
        from PySide2.QtCore import QTimer

        # 初始化信号连接
        self.signal_connection()

        # 延迟加载,确保所有控件就绪
        QTimer.singleShot(200, self.load_first_doc)  # type: ignore

    def signal_connection(self):
        """信号连接函数"""

        now_doc_list = self.docs_combobox.now_doc_card_list

        # 显式指定 int 重载
        now_doc_list.currentIndexChanged[int].connect(self.on_now_doc_changed)  # type: ignore

    def load_first_doc(self):
        """加载第一个文档"""

        now_doc_list = self.docs_combobox.now_doc_card_list

        if now_doc_list.count() > 0:
            # 先设为 -1 再设 0,强制触发
            now_doc_list.setCurrentIndex(-1)
            now_doc_list.setCurrentIndex(0)

    def on_now_doc_changed(self, index: int):
        """文档切换事件处理函数"""
        import json, os
        from app_const_var import AssetsPathTXT

        try:
            now_doc_list = self.docs_combobox.now_doc_card_list
            now_doc_id = now_doc_list.itemData(index)

            # 读取配置
            config_path = os.path.join(os.getcwd(), "config", "app_config.json")

            with open(config_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
                language_config = json_data["Language"]["Language"]

            # 文档路径
            docs_dir = os.path.abspath(AssetsPathTXT.APP_DOCS_FOLDER)
            now_doc_path = os.path.join(docs_dir, f"{now_doc_id}-{language_config}.md")

            if not os.path.exists(now_doc_path):
                raise FileNotFoundError(f"文件不存在: {now_doc_path}")

            with open(now_doc_path, "r", encoding="utf-8") as f:
                docs_content = f.read()
            self.docs_browser.setMarkdown(docs_content)

        except Exception as e:
            error_msg = f"# 加载失败\n\n**错误**：{e}"
            self.docs_browser.setMarkdown(error_msg)
            print(f"异常: {e}")
