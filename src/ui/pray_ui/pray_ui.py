"""
子页面:祈福, 
此页面包含了基本点名功能的GUI, 是程序启动时的默认页面, 
包含三大部分:一言显示, 点名结果显示, 点名快捷设置,
引用时可作 PrayUI / subpage_pray
"""

from PySide2.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QWidget,
    QLayout,
    QListWidgetItem,
)
import qfluentwidgets as qfw
from ui.ui_str import PrayUIString


def set_widget_to_layout(wlist: list, layout: QLayout):
    """设置布局的通用函数(控件到布局)"""
    for widget in wlist:
        layout.addWidget(widget)


class HitokotoShowGroup(QWidget):
    """一言显示 部分, 继承自 QWidget,
    引用时可作 HitokotoShowGr"""

    def __init__(self):
        super().__init__()

        # 初始化垂直布局
        self.vboxlayout = QVBoxLayout(self)

        # 初始化控件
        self.init_widgets()

        # 控件列表
        self.widget_list = [self.hitokoto_show]

        # 设置布局
        set_widget_to_layout(self.widget_list, self.vboxlayout)

    def init_widgets(self):
        """初始化控件"""
        from PySide2.QtGui import QColor

        # 一言显示
        self.hitokoto_show = qfw.StrongBodyLabel(
            PrayUIString.HITOKOTO_SHOW_LABEL_DEFAUT
        )
        self.hitokoto_show.setTextColor(QColor(0, 0, 0), QColor(255, 255, 255))  # type: ignore


class PrayResultShowGroup(QWidget):
    """点名结果显示 部分, 继承自 QWidget,
    引用时可作 PrayResShowGr"""

    def __init__(self):
        super().__init__()

        # 初始化垂直布局
        self.vboxlayout = QVBoxLayout(self)

        # 初始化控件
        self.init_widgets()

        # 控件列表
        self.widget_list = [self.pray_result_show]

        # 设置布局
        set_widget_to_layout(self.widget_list, self.vboxlayout)

    def init_widgets(self):
        """初始化控件"""

        # 点名结果显示
        self.pray_result_show = qfw.ListWidget()
        self.pray_result_list = [PrayUIString.PRAY_RESULT_LIST_DEFAULT]
        if not (self.pray_result_list == []):
            self.bind_list_to_widget()

    def bind_list_to_widget(self):
        """将点名结果列表与控件绑定"""

        for i in self.pray_result_list:
            item = QListWidgetItem(i)
            self.pray_result_show.addItem(item)


class PrayQuickSettingGroup(QWidget):
    """点名快捷设置 部分, 继承自 QWidget,
    引用时可作 PraySettGr"""

    def __init__(self):
        super().__init__()

        # 初始化栅格布局
        self.gridlayout = QGridLayout(self)

        # 初始化各控件与布局
        self.init_widgets_layouts()

        # 添加控件进布局
        self.add_widgets_layouts_to_layout()

    def init_widgets_layouts(self):
        """初始化各控件与布局"""

        # 第一行
        self.pray_button_method()
        self.pray_namelist_choose_combobox_method()
        self.set_pray_algorithm_combobox_method()
        self.set_pray_number_layout_method()

        # 第二行
        self.set_pray_sex_combobox_method()
        self.set_pray_group_combobox_method()
        self.set_pray_tag_combobox_method()
        self.reset_pray_setting_button_method()

    def add_widgets_layouts_to_layout(self):
        """添加控件与布局进总布局"""

        # 第一行
        self.gridlayout.addWidget(self.pray_button, 0, 0, 1, 1)  # type: ignore
        self.gridlayout.addWidget(self.pray_namelist_choose_combobox, 0, 1, 1, 1)  # type: ignore
        self.gridlayout.addWidget(self.pray_algorithm_combobox, 0, 2, 1, 1)  # type: ignore
        self.gridlayout.addWidget(self.spnum_widget, 0, 3, 1, 1)  # type: ignore

        # 第二行
        self.gridlayout.addWidget(self.pray_sex_combobox, 1, 0, 1, 1)  # type: ignore
        self.gridlayout.addWidget(self.pray_group_combobox, 1, 1, 1, 1)  # type: ignore
        self.gridlayout.addWidget(self.pray_tag_combobox, 1, 2, 1, 1)  # type: ignore
        self.gridlayout.addWidget(self.pray_reset_setting_button, 1, 3, 1, 1)  # type: ignore

    def pray_button_method(self):
        """祈福按钮"""

        # 初始化祈福按钮
        self.pray_button = qfw.TogglePushButton(PrayUIString.PRAY_BUTTON_TEXT)

    def pray_namelist_choose_combobox_method(self):
        """祈福名单选择下拉框"""

        # 初始化祈福名单选择下拉框
        self.pray_namelist_choose_combobox = qfw.ComboBox()

        # 初始化祈福名单选项
        self.pray_namelist_choose_list = []

        # 绑定列表到下拉框
        self.pray_namelist_choose_combobox.addItems(self.pray_namelist_choose_list)

    def set_pray_algorithm_combobox_method(self):
        """设置祈福算法下拉框"""

        # 初始化祈福算法下拉框
        self.pray_algorithm_combobox = qfw.ComboBox()

        # 初始化祈福算法选项
        self.pray_algorithm_list = [
            PrayUIString.PRAY_ALGORITHM_LIST_DEFAULT,
        ]

        # 绑定列表到下拉框
        self.pray_algorithm_combobox.addItems(self.pray_algorithm_list)

    def set_pray_number_layout_method(self):
        """设置祈福人数水平布局控件"""

        # 初始化控件
        self.spnum_widget = QWidget()

        # 初始化水平布局
        self.spnum_hboxlayout = QHBoxLayout(self)

        # 初始化减少按钮
        self.pray_number_subtract_button = qfw.PushButton(
            PrayUIString.PRAY_NUMBER_SUBTRACT_BUTTON_TEXT
        )

        # 初始化增加按钮
        self.pray_number_plus_button = qfw.PushButton(
            PrayUIString.PRAY_NUMBER_PLUS_BUTTON_TEXT
        )

        # 初始化当前数量
        self.pray_number_now = 1

        # 初始化当前数量显示
        self.pray_number_now_label = qfw.TitleLabel(str(self.pray_number_now))

        # 控件列表
        self.spnum_widget_list = [
            self.pray_number_subtract_button,
            self.pray_number_now_label,
            self.pray_number_plus_button,
        ]

        # 设置布局
        set_widget_to_layout(self.spnum_widget_list, self.spnum_hboxlayout)
        self.spnum_widget.setLayout(self.spnum_hboxlayout)

    def update_pray_number_now(self, is_plus: bool):
        """更新当前祈福人数"""

        # 判断是否为加
        if is_plus:
            self.pray_number_now += 1
        # 判断是否为减
        else:
            # 判断当前祈福人数是否大于等于2, 防止出现祈福0人的情况
            if self.pray_number_now >= 2:
                self.pray_number_now -= 1

        # 更新文本显示
        self.pray_number_now_label.setText(str(self.pray_number_now))

    def set_pray_sex_combobox_method(self):
        """选择特定性别进行祈福"""

        # 初始化下拉框
        self.pray_sex_combobox = qfw.ComboBox()

        # 初始化下拉框选项
        self.pray_sex_list = [
            PrayUIString.PRAY_SEX_LIST_ALL,
            PrayUIString.PRAY_SEX_LIST_MALE,
            PrayUIString.PRAY_SEX_LIST_FEMALE,
            PrayUIString.PRAY_SEX_LIST_NOTBINARY,
        ]

        # 绑定列表到下拉框
        self.pray_sex_combobox.addItems(self.pray_sex_list)

    def set_pray_group_combobox_method(self):
        """选择特定组别进行祈福"""

        # 初始化下拉框
        self.pray_group_combobox = qfw.ComboBox()

        # 初始化下拉框选项
        self.pray_group_list = [PrayUIString.PRAY_GROUP_LIST_DEFAULT]

        # 绑定列表到下拉框
        self.pray_group_combobox.addItems(self.pray_group_list)

    def set_pray_tag_combobox_method(self):
        """选择特定标签进行祈福"""

        # 初始化下拉框
        self.pray_tag_combobox = qfw.ComboBox()

        # 初始化下拉框选项
        self.pray_tag_list = [PrayUIString.PRAY_TAG_LIST_DEFAULT]

        # 绑定列表到下拉框
        self.pray_tag_combobox.addItems(self.pray_tag_list)

    def reset_pray_setting_button_method(self):
        """重置抽选临时名单"""

        # 初始化按钮
        self.pray_reset_setting_button = qfw.PushButton(
            PrayUIString.PRAY_RESET_SETTING_BUTTON_TEXT
        )


class PrayUI(QFrame):
    """子页面:祈福的基础UI类,
    此页面包含了基本点名功能的GUI, 是程序启动时的默认页面,
    包含三大部分:一言显示, 点名结果显示, 点名快捷设置,
    引用时可作 PrayUI / pray_ui"""

    def __init__(self, parent=None):
        super().__init__(parent)
        from PySide2.QtCore import QMargins

        # 页面布局
        self.vboxlayout = QVBoxLayout(self)

        # 初始化控件
        self.init_widgets()

        # 控件列表
        self.widgets_list = [
            self.hitokoto_show_group,
            self.pray_result_show_group,
            self.pray_quick_setting_group,
        ]

        # 设置布局
        set_widget_to_layout(self.widgets_list, self.vboxlayout)

        # 调整布局
        self.vboxlayout.setContentsMargins(QMargins(30, 30, 30, 30))

    def init_widgets(self):
        """初始化控件"""

        # 初始化各组控件
        self.hitokoto_show_group = HitokotoShowGroup()
        self.pray_result_show_group = PrayResultShowGroup()
        self.pray_quick_setting_group = PrayQuickSettingGroup()
