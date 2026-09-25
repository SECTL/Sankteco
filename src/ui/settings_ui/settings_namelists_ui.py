"""
子页面: 名单管理( 首选项 的子页面), 
此页面包含了名单的相关管理与设置,
引用时可作 SettNLUI / settings_namelists_ui
"""

from typing import Union, List

from PySide2.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PySide2.QtCore import Signal, QObject
import qfluentwidgets as qfw
from qfluentwidgets import FluentIcon as FI

from ui.ui_str import SettNLUIString


class NLSignals(QObject):
    """初始化名单操作信号"""

    refresh_namelist = Signal()
    add_new_namelist = Signal()
    rename_namelist = Signal()
    del_namelist = Signal()
    import_namelist = Signal()
    export_namelist = Signal()


nlsignals = NLSignals()


class AskNewNamelistID(qfw.MessageBoxBase):
    """询问新名单的标识符, 继承自 对话框基类 MessageBoxBase,
    引用时可作 AskNewID"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 标题
        self.title_label = qfw.SubtitleLabel(SettNLUIString.ASK_NEW_ID_MSG_TITLE, self)

        # 输入框
        self.input_lineedit = qfw.LineEdit(self)
        self.input_lineedit.setPlaceholderText(
            SettNLUIString.ASK_NEW_ID_MSG_LINEEDIT_TEXT
        )
        self.input_lineedit.setClearButtonEnabled(True)

        # 添加控件进布局
        self.viewLayout.addWidget(self.title_label)
        self.viewLayout.addWidget(self.input_lineedit)
        self.widget.setMinimumWidth(450)


class NowNamelistCard(qfw.SettingCard):
    """当前名单 卡片, 从属于 名单 部分,
    继承自 设置卡基类 SettingCard,
    引用时可作 NowNamelistCard"""

    def __init__(self, parent=None):
        super().__init__(
            FI.PEOPLE,
            SettNLUIString.NOW_NAMELIST_CARD_TITLE,
            SettNLUIString.NOW_NAMELIST_CARD_CONTEXT,
            parent,
        )

        # 下拉框
        self.now_namelist_card_list = qfw.ComboBox()
        self.now_namelist_card_list_item: List[str] = []
        self.now_namelist_card_list.addItems(self.now_namelist_card_list_item)

        # 调整布局边距、添加控件进布局
        self.hBoxLayout.setMargin(16)
        self.hBoxLayout.addWidget(self.now_namelist_card_list)


class NamelistSettingCard(qfw.SimpleCardWidget):
    """名单操作 卡片, 从属于 名单 部分,
    继承自 简单卡片组件 SimpleCardWidget,
    引用时可作 NamelistSettCard"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 初始化布局
        self.hboxlayout = QHBoxLayout(self)

        # 初始化控件
        self.init_widgets()

        # 添加控件进布局
        self.hboxlayout.addStretch(1)
        self.hboxlayout.addWidget(self.refresh_namelist_button)
        self.hboxlayout.addWidget(self.add_new_namelist_button)
        self.hboxlayout.addWidget(self.rename_namelist_button)
        self.hboxlayout.addWidget(self.del_namelist_button)
        self.hboxlayout.addWidget(self.import_namelist_button)
        self.hboxlayout.addWidget(self.export_namelist_button)
        self.hboxlayout.addStretch(1)

    def init_widgets(self):
        """初始化控件"""

        # 刷新名单
        self.refresh_namelist_button = qfw.PushButton(
            FI.SYNC,
            SettNLUIString.REFRESH_NAMELIST_BUTTON_TEXT,
        )

        # 新建名单
        self.add_new_namelist_button = qfw.PushButton(
            FI.ADD,
            SettNLUIString.ADD_NEW_NAMELIST_BUTTON_TEXT,
        )

        # 重命名名单
        self.rename_namelist_button = qfw.PushButton(
            FI.PENCIL_INK,
            SettNLUIString.RENAME_NAMELIST_BUTTON_TEXT,
        )

        # 删除名单
        self.del_namelist_button = qfw.PushButton(
            FI.DELETE,
            SettNLUIString.DEL_NAMELIST_BUTTON_TEXT,
        )

        # 导入名单
        self.import_namelist_button = qfw.PrimaryPushButton(
            FI.SEARCH,
            SettNLUIString.IMPORT_NAMELIST_BUTTON_TEXT,
        )

        # 导出名单
        self.export_namelist_button = qfw.PrimaryPushButton(
            FI.SAVE_AS,
            SettNLUIString.EXPORT_NAMELIST_BUTTON_TEXT,
        )


class NamelistSettingBar(qfw.CommandBar):
    """名单操作 卡片,
    继承自 命令栏 CommandBar,
    引用时可作 NamelistSettBar"""

    def __init__(self, parent=None):
        super().__init__(parent)
        from PySide2.QtCore import Qt

        # 右侧显示文本
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)  # type: ignore

        # 添加动作
        self.addActions(
            [
                qfw.Action(
                    FI.SYNC,
                    SettNLUIString.REFRESH_NAMELIST_BUTTON_TEXT,
                    triggered=lambda: nlsignals.refresh_namelist.emit(),
                ),
                qfw.Action(
                    FI.ADD,
                    SettNLUIString.ADD_NEW_NAMELIST_BUTTON_TEXT,
                    triggered=lambda: nlsignals.add_new_namelist.emit(),
                ),
                qfw.Action(
                    FI.PENCIL_INK,
                    SettNLUIString.RENAME_NAMELIST_BUTTON_TEXT,
                    triggered=lambda: nlsignals.rename_namelist.emit(),
                ),
                qfw.Action(
                    FI.DELETE,
                    SettNLUIString.DEL_NAMELIST_BUTTON_TEXT,
                    triggered=lambda: nlsignals.del_namelist.emit(),
                ),
                qfw.Action(
                    FI.SEARCH,
                    SettNLUIString.IMPORT_NAMELIST_BUTTON_TEXT,
                    triggered=lambda: nlsignals.import_namelist.emit(),
                ),
                qfw.Action(
                    FI.SAVE_AS,
                    SettNLUIString.EXPORT_NAMELIST_BUTTON_TEXT,
                    triggered=lambda: nlsignals.export_namelist.emit(),
                ),
            ]
        )


class NameTableWidget(QWidget):
    """名单表格, 从属于 名单 部分,
    引用时可作 NameTableWidget"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 初始化控件
        self.init_widgets()

        # 初始化布局
        self.hboxlayout = QHBoxLayout(self)

        # 添加控件进布局
        self.hboxlayout.addWidget(self.name_table_widget)

    def init_widgets(self):
        """初始化控件"""

        # 初始化表格、起用边框、设置圆角、禁止换行、右键响应
        self.name_table_widget = qfw.TableWidget(self)
        self.name_table_widget.setBorderVisible(True)
        self.name_table_widget.setBorderRadius(8)
        self.name_table_widget.setWordWrap(False)
        self.name_table_widget.setSelectRightClickedRow(True)

        # 设置列数与初始行数
        self.name_table_widget_row = 0
        self.name_table_widget_column = 6
        self.name_table_widget.setRowCount(self.name_table_widget_row)
        self.name_table_widget.setColumnCount(self.name_table_widget_column)

        # 设置水平表头并隐藏垂直表头
        self.name_table_widget.setHorizontalHeaderLabels(
            [
                SettNLUIString.NAMETABLE_HEADER_LABEL_EXIST,
                SettNLUIString.NAMETABLE_HEADER_LABEL_NO,
                SettNLUIString.NAMETABLE_HEADER_LABEL_NAME,
                SettNLUIString.NAMETABLE_HEADER_LABEL_GENDER,
                SettNLUIString.NAMETABLE_HEADER_LABEL_GROUP,
                SettNLUIString.NAMETABLE_HEADER_LABEL_TIP,
            ]
        )
        self.name_table_widget.verticalHeader().hide()

        # 表格数据
        self.name_table_widget_data = []

    def add_item(
        self,
        no: Union[str, int],
        name: str,
        gender: str,
        group: Union[str, int],
        tip: str,
        is_exist: bool = True,
    ):
        """添加单项数据"""

        # 判断数据并转为文本
        exist = "True" if is_exist else "False"
        no = str(no)
        group = str(group)

        self.name_table_widget_row += 1
        self.name_table_widget_data.append([exist, no, name, gender, group, tip])

        self.refresh_items()

    def refresh_items(self):
        """刷新表格数据"""

        # 先清除表格行数以清空数据, 再设置新行数
        self.name_table_widget.setRowCount(0)
        self.name_table_widget.setRowCount(self.name_table_widget_row)

        # 添加数据到表格
        for i, data in enumerate(self.name_table_widget_data):
            for j in range(self.name_table_widget_column):
                self.name_table_widget.setItem(i, j, QTableWidgetItem(data[j]))

        self.refresh_table_column_width()

    def refresh_table_column_width(self):
        """刷新表格列宽"""

        # 获取表格列宽模式
        header = self.name_table_widget.horizontalHeader()

        # 设置所有列先根据内容调整宽度
        header.setSectionResizeMode(QHeaderView.ResizeToContents)  # type: ignore

        # 开启 "拉伸最后一列" 功能
        header.setStretchLastSection(True)

        # 重新计算第3列
        self.name_table_widget.resizeColumnToContents(2)


class SettNLUI(QFrame):
    """子页面: 名单管理( 首选项 的子页面)的基础UI类,
    此页面包含了名单的相关管理与设置,
    引用时可作 SettNLUI / settings_namelists_ui"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 初始化垂直布局
        self.vboxlayout = QVBoxLayout(self)
        self.vboxlayout.setMargin(32)

        # 初始化各控件
        self.frame_title = qfw.SubtitleLabel(SettNLUIString.FRAME_TITLE)
        self.now_namelist_card = NowNamelistCard(self)
        self.namelist_setting_card = NamelistSettingBar(self)
        self.name_table_widget = NameTableWidget(self)

        # 添加控件进布局
        self.vboxlayout.addWidget(self.frame_title)
        self.vboxlayout.addWidget(self.now_namelist_card)
        self.vboxlayout.addWidget(self.namelist_setting_card)
        self.vboxlayout.addWidget(self.name_table_widget)
        self.setLayout(self.vboxlayout)
