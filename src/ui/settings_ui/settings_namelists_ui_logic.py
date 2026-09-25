"""
子页面: 名单管理( 首选项 的子页面)的UI逻辑文件, 
引用时可作 SettNLUILogic / settings_namelists_ui_logic
"""

import tablib
from PySide2.QtWidgets import QFileDialog

from ui.settings_ui.settings_namelists_ui import (
    AskNewNamelistID,
    SettNLUI,
    nlsignals,
)
from logic.add_import_export_namelist import AIENamelist
from logic.namelist_registry import namelist_registry
from ui.ui_str import SettNLUIString
from app_const_var import LogicFilesString, AssetsPathTXT


class SettNLUILogic(SettNLUI):
    """子页面: 名单管理( 首选项 的子页面)的UI基础逻辑类,
    引用时可作 SettNLUILogic / settings_namelists_ui_logic"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 初始化信号连接函数
        self.signal_connection()

        # 初始化读取名单列表
        self.load_namelists_list()

    def load_namelists_list(self):
        """导入名单并设置列表"""

        ui = self.now_namelist_card
        namelists = namelist_registry.scan()

        # 添加名单列表到下拉框
        ui.now_namelist_card_list_item = list(namelists)
        ui.now_namelist_card_list.clear()
        ui.now_namelist_card_list.addItems(namelists)

        # 默认选中第一项 (如果存在), 会触发 currentIndexChanged 信号 -> 自动加载
        if ui.now_namelist_card_list.count() > 0:
            ui.now_namelist_card_list.setCurrentIndex(0)

    def signal_connection(self):
        """信号连接函数"""

        now_namelist_card_list = self.now_namelist_card.now_namelist_card_list

        # 当前名单下拉框
        now_namelist_card_list.currentIndexChanged.connect(  # type: ignore
            lambda: self.load_namelist_from_json(
                f"{AssetsPathTXT.APP_NAMELISTS_FOLDER}{now_namelist_card_list.currentText()}"
            )
        )

        # 刷新名单
        nlsignals.refresh_namelist.connect(self.name_table_widget.refresh_items)

        # 新建名单
        nlsignals.add_new_namelist.connect(self.add_new_namelist)

        # 导入名单
        nlsignals.import_namelist.connect(self.import_namelist)

        # 导出名单
        nlsignals.export_namelist.connect(self.export_namelist)

        # 下拉框选择变化 → 通知注册表
        now_namelist_card_list.currentIndexChanged.connect(
            lambda: namelist_registry.set_current(now_namelist_card_list.currentText())
        )

        # 注册表名单列表变化 → 刷新下拉框（用于新建/导入后统一刷新）
        namelist_registry.namelists_changed.connect(self._on_namelists_changed)

    def _on_namelists_changed(self, namelists):
        ui = self.now_namelist_card
        ui.now_namelist_card_list_item = list(namelists)
        ui.now_namelist_card_list.clear()
        ui.now_namelist_card_list.addItems(namelists)
        if ui.now_namelist_card_list.count() > 0:
            ui.now_namelist_card_list.setCurrentIndex(0)

    def add_new_namelist(self):
        """新建名单"""

        new_namelist_ID = None
        ui = self.now_namelist_card

        # 调用新名单标识符对话框
        ask_ID_msg = AskNewNamelistID(self)
        if ask_ID_msg.exec_():
            new_namelist_ID = ask_ID_msg.input_lineedit.text()

            # 调用 AIENamelist.add_namelist 创建新名单
            new_namelist_path, new_namelist_data = AIENamelist.add_namelist(
                new_namelist_ID
            )

            # 执行刷新流程
            namelist_registry.scan()
            namelist_registry.set_current(new_namelist_path)

            # 加载名单
            self.load_namelist_from_dataset(new_namelist_data)

    def import_namelist(self):
        """导入名单"""

        ui = self.now_namelist_card

        # 创建对话框实例
        import_namelist_dialog = QFileDialog(self)
        import_namelist_dialog.setWindowTitle(
            SettNLUIString.IMPORT_NAMELIST_DIALOG_TITLE
        )

        # 设置文件过滤器
        import_namelist_dialog.setNameFilters(
            [
                f"{SettNLUIString.NAMELIST_DIALOG_FILTER_TXT} (*.txt)",
                f"{SettNLUIString.NAMELIST_DIALOG_FILTER_JSON} (*.json)",
                f"{SettNLUIString.NAMELIST_DIALOG_FILTER_YAML} (*.yaml)",
                f"{SettNLUIString.NAMELIST_DIALOG_FILTER_CSV} (*.csv)",
                f"{SettNLUIString.NAMELIST_DIALOG_FILTER_XLSX_XLS_ODS} (*.xlsx *.xls *.ods)",
                f"{SettNLUIString.NAMELIST_DIALOG_FILTER_QR} (*.png)",
            ]
        )

        # 设置为 "打开" 模式
        import_namelist_dialog.setAcceptMode(QFileDialog.AcceptOpen)  # type: ignore

        # 显示对话框并获取名单路径
        if import_namelist_dialog.exec_():
            selected_files = import_namelist_dialog.selectedFiles()
            if selected_files:
                namelist_path = selected_files[0]
                dataset, saved_path = AIENamelist.import_namelist(namelist_path)
                if dataset is not None:
                    # 类型保护
                    assert saved_path is not None

                    namelist_registry.scan()
                    namelist_registry.set_current(saved_path)
                    self.load_namelist_from_dataset(dataset)
                else:
                    print("导入失败：文件格式不支持或无有效表头")

    def export_namelist(self):
        """导出名单"""

        ui = self.now_namelist_card
        now_namelist = ui.now_namelist_card_list_item[
            ui.now_namelist_card_list.currentIndex()
        ]
        now_namelist_data = AIENamelist.json_to_dataset(now_namelist)

        # 创建对话框实例
        export_namelist_dialog = QFileDialog(self)
        export_namelist_dialog.setWindowTitle(
            SettNLUIString.EXPORT_NAMELIST_DIALOG_TITLE
        )

        # 设置文件过滤器
        export_namelist_dialog.setNameFilters(
            [
                f"{SettNLUIString.NAMELIST_DIALOG_FILTER_TXT} (*.txt)",
                f"{SettNLUIString.NAMELIST_DIALOG_FILTER_JSON} (*.json)",
                f"{SettNLUIString.NAMELIST_DIALOG_FILTER_YAML} (*.yaml)",
                f"{SettNLUIString.NAMELIST_DIALOG_FILTER_CSV} (*.csv)",
                f"{SettNLUIString.NAMELIST_DIALOG_FILTER_XLSX} (*.xlsx)",
                f"{SettNLUIString.NAMELIST_DIALOG_FILTER_XLS} (*.xls)",
                f"{SettNLUIString.NAMELIST_DIALOG_FILTER_ODS} (*.ods)",
                f"{SettNLUIString.NAMELIST_DIALOG_FILTER_QR} (*.png)",
            ]
        )

        # 设置默认后缀
        export_namelist_dialog.setDefaultSuffix("json")

        # 设置为 "导出" 模式
        export_namelist_dialog.setAcceptMode(QFileDialog.AcceptSave)  # type: ignore

        # 显示对话框并获取名单路径
        if export_namelist_dialog.exec_():
            selected_files = (
                export_namelist_dialog.selectedFiles()[0]
                if export_namelist_dialog.selectedFiles()
                else ""
            )
            if not selected_files:
                return
            selected_ext = self.get_ext_from_filter(
                export_namelist_dialog.selectedNameFilter()
            )
            # FIXME:判断是否无后缀
            if selected_ext and not selected_files.endswith(f".{selected_ext}"):
                namelist_path = selected_files + f".{selected_ext}"
            namelist_path = selected_files
            AIENamelist.export_namelist(now_namelist_data, namelist_path)

    def load_namelist_from_dataset(self, namelist_data: tablib.Dataset):
        """从 tablib.Dataset 中加载名单"""

        ui = self.name_table_widget

        # 先清空表格内容
        ui.name_table_widget.setRowCount(0)
        ui.name_table_widget_row = 0
        ui.name_table_widget_data = []

        # 循环获取并添加值进入UI
        namelist_names_num = len(
            namelist_data[LogicFilesString.AIENAMELIST_HEADER_EXIST]
        )
        ui.name_table_widget.setRowCount(namelist_names_num)
        for i in range(namelist_names_num):
            data_i = namelist_data[i]
            ui.add_item(
                data_i[1],
                data_i[2],
                data_i[3],
                data_i[4],
                data_i[5],
                data_i[0],
            )

    def load_namelist_from_json(self, namelist_path: str):
        """从 JSON 文件中加载名单"""
        ui = self.name_table_widget

        # 先清空表格
        ui.name_table_widget.setRowCount(0)
        ui.name_table_widget_row = 0
        ui.name_table_widget_data = []

        # 导入数据，解包获得 Dataset
        dataset, _ = AIENamelist.import_namelist(namelist_path)
        if dataset is not None:
            try:
                # 获取有效行数（假设列 EXIST 存在）
                row_count = len(dataset[LogicFilesString.AIENAMELIST_HEADER_EXIST])
                ui.name_table_widget.setRowCount(row_count)
                for i in range(row_count):
                    row_data = dataset[i]
                    ui.add_item(
                        row_data[1],  # 编号
                        row_data[2],  # 姓名
                        row_data[3],  # 性别
                        row_data[4],  # 年龄
                        row_data[5],  # 备注
                        row_data[0],  # 是否启用
                    )
            except Exception as e:
                print(f"加载名单数据出错: {e}")
        else:
            print(f"无法加载文件: {namelist_path}")

    def get_ext_from_filter(self, filter: str) -> str:
        """从过滤器提取扩展名"""
        import re

        # 匹配过滤器后缀并取首个
        match = re.search(r"\(\*\.([^)\s]+)", filter)
        if match:
            ext = match.group(1).split(";")[0]
            return ext
        return ""
