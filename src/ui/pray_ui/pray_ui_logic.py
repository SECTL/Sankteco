"""
子页面:祈福的UI逻辑文件, 
引用时可作 PrayUILogic / pray_ui_logic
"""

from pathlib import Path

from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QListWidgetItem

from ui.pray_ui.pray_ui import PrayUI
from ui.ui_str import PrayUIString
from logic.namelist_registry import namelist_registry
from logic.add_import_export_namelist import AIENamelist
from logic.fair_random import FairRandomPicker
from app_const_var import AssetsPathTXT, LogicFilesString


class PrayUILogic(PrayUI):
    """子页面:祈福的基础逻辑类,
    引用时可作 PrayUILogic / pray_ui_logic"""

    ANIMATION_INTERVAL_MS = 100

    def __init__(self, parent=None):
        super().__init__(parent)

        # 公平随机 picker(跨次累积公平历史)
        self._fair_picker = None

        # 抽选动画相关
        self._anim_candidates: list = []
        self._anim_index: int = 0
        self._anim_item: QListWidgetItem | None = None
        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(self.ANIMATION_INTERVAL_MS)
        self._anim_timer.timeout.connect(self._on_animation_tick)

        # 初始化扫描名单
        namelist_registry.scan()

        # 初始化信号连接函数
        self.signal_connection()

    def signal_connection(self):
        """信号连接函数"""

        pray_sett_gr = self.pray_quick_setting_group

        # 祈福按钮:状态改变
        pray_sett_gr.pray_button.toggled.connect(self.on_pray_button_toggled)

        # 祈福人数水平布局控件:更新数量显示
        pray_sett_gr.pray_number_subtract_button.clicked.connect(
            lambda: pray_sett_gr.update_pray_number_now(False)
        )
        pray_sett_gr.pray_number_plus_button.clicked.connect(
            lambda: pray_sett_gr.update_pray_number_now(True)
        )

        # 订阅名单变化
        namelist_registry.namelists_changed.connect(self._on_namelists_changed)

        # 初始化时同步一次(防止注册表已经扫过)
        self._on_namelists_changed(namelist_registry.get_namelists())

        # 重置抽选
        pray_sett_gr.pray_reset_setting_button.clicked.connect(
            self.on_reset_setting_clicked
        )

        # 换名单 -> 丢弃旧的公平历史
        pray_sett_gr.pray_namelist_choose_combobox.currentTextChanged.connect(
            self.on_namelist_switched
        )

    def _on_namelists_changed(self, namelists):
        """把注册表里的名单同步到祈福页的下拉框"""

        cb = self.pray_quick_setting_group.pray_namelist_choose_combobox
        cb.clear()
        cb.addItems(namelists)
        if namelists:
            cb.setCurrentIndex(0)

    def on_pray_button_toggled(self, checked: bool):
        """祈福按钮:状态改变逻辑函数"""

        if checked:
            self._start_animation()
        else:
            self._stop_animation_and_pick()

    def _start_animation(self):
        """开始抽选动画: 遍历候选人, 不断刷新列表第一行"""

        # 动画期间锁定会影响抽选结果的控件
        self._set_controls_enabled(False)

        # 快照当前候选人, 供动画与后续抽选共用
        candidates = self._load_and_filter_candidates()
        self._anim_candidates = candidates
        self._anim_index = 0

        lw = self.pray_result_show_group.pray_result_show
        lw.clear()

        # 空名单: 显示默认文案, 不启动定时器
        if not candidates:
            lw.addItem(QListWidgetItem(PrayUIString.PRAY_RESULT_LIST_DEFAULT))
            self._anim_item = None
            # 空名单直接解锁
            self._set_controls_enabled(True)
            return

        # 先放一个占位 item, 后面 setText 更新
        self._anim_item = QListWidgetItem(candidates[0])
        lw.addItem(self._anim_item)

        # 启动定时器
        self._anim_timer.start()

    def _on_animation_tick(self):
        """定时器回调: 顺序遍历候选人, 不断改变第一行显示"""

        # 防止 timer 启动后名单被意外清空
        if not self._anim_candidates or self._anim_item is None:
            return

        # 取模 = 走到末尾自动回到开头,无限循环
        self._anim_index = (self._anim_index + 1) % len(self._anim_candidates)
        self._anim_item.setText(self._anim_candidates[self._anim_index])

    def _stop_animation_and_pick(self):
        """停止动画, 抽选并显示结果"""

        self._anim_timer.stop()

        try:
            if not self._anim_candidates:
                # 空名单: 保持默认文案, 不动
                return

            # 取人数, 不超过候选人数
            n = self.pray_quick_setting_group.pray_number_now
            n = min(n, len(self._anim_candidates))

            # 分发到具体算法
            algorithm = (
                self.pray_quick_setting_group.pray_algorithm_combobox.currentText()
            )
            chosen = self._dispatch_algorithm(algorithm, self._anim_candidates, n)

            self._show_results(chosen)
        finally:
            self._set_controls_enabled(True)

    def _set_controls_enabled(self, enabled: bool):
        """动画期间锁定 / 解锁会影响抽选结果的控件,
        注意:不锁 pray_button 自己,否则用户无法再次按下停止
        """

        gr = self.pray_quick_setting_group
        for w in (
            gr.pray_namelist_choose_combobox,
            gr.pray_algorithm_combobox,
            gr.pray_sex_combobox,
            gr.pray_group_combobox,
            gr.pray_tag_combobox,
            gr.pray_number_subtract_button,
            gr.pray_number_plus_button,
            gr.pray_reset_setting_button,
        ):
            w.setEnabled(enabled)

    def _dispatch_algorithm(self, algorithm: str, candidates: list, n: int) -> list:
        """根据下拉框所选算法分发到具体实现"""

        # 默认公平随机算法
        if algorithm == PrayUIString.PRAY_ALGORITHM_LIST_DEFAULT:
            return self._pick_fair(candidates, n)

        # 兜底: 未知算法 -> 公平随机
        return self._pick_fair(candidates, n)

    def _load_and_filter_candidates(self) -> list:
        """读取当前下拉框选中的名单，并按性别/组别/标签过滤"""

        name = self.pray_quick_setting_group.pray_namelist_choose_combobox.currentText()
        if not name:
            return []

        path = str(Path(AssetsPathTXT.APP_NAMELISTS_FOLDER) / name)
        dataset, _ = AIENamelist.import_namelist(path)
        if dataset is None:
            return []

        # 读取过滤条件
        want_sex = self.pray_quick_setting_group.pray_sex_combobox.currentText()
        want_group = self.pray_quick_setting_group.pray_group_combobox.currentText()
        want_tag = self.pray_quick_setting_group.pray_tag_combobox.currentText()

        # 表头索引
        h = LogicFilesString.AIENAMELIST_HEADER
        idx_exist = h.index(LogicFilesString.AIENAMELIST_HEADER_EXIST)
        idx_name = h.index(LogicFilesString.AIENAMELIST_HEADER_NAME)
        idx_sex = h.index(LogicFilesString.AIENAMELIST_HEADER_GENDER)
        idx_group = h.index(LogicFilesString.AIENAMELIST_HEADER_GROUP)
        idx_tip = h.index(LogicFilesString.AIENAMELIST_HEADER_TIP)

        result = []
        for row in dataset:
            if not self._to_bool(row[idx_exist]):
                continue
            if (
                want_sex != PrayUIString.PRAY_SEX_LIST_ALL
                and str(row[idx_sex]) != want_sex
            ):
                continue
            if (
                want_group != PrayUIString.PRAY_GROUP_LIST_DEFAULT
                and str(row[idx_group]) != want_group
            ):
                continue
            if (
                want_tag != PrayUIString.PRAY_TAG_LIST_DEFAULT
                and str(row[idx_tip]) != want_tag
            ):
                continue
            result.append(str(row[idx_name]))
        return result

    @staticmethod
    def _to_bool(v) -> bool:
        """兼容 JSON 里 True/False 与字符串 True/False"""

        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.strip().lower() in ("true", "1", "yes", "是", "启用")
        return bool(v)

    def _pick_fair(self, candidates: list, n: int) -> list:
        """使用 FairRandomPicker 抽选 n 个人(单次不重复)"""

        if self._fair_picker is None or set(self._fair_picker.items) != set(candidates):
            self._fair_picker = FairRandomPicker(candidates)

        chosen = []
        for _ in range(n):
            if not self._fair_picker.items:
                break
            c = self._fair_picker.pick()
            chosen.append(c)
            self._fair_picker.items.remove(c)

        for c in chosen:
            self._fair_picker.items.append(c)

        return chosen

    def _show_results(self, results: list):

        lw = self.pray_result_show_group.pray_result_show
        lw.clear()
        for name in results:
            lw.addItem(QListWidgetItem(str(name)))

    def on_reset_setting_clicked(self):
        """重置抽选(清空公平历史与冷却)"""

        self._fair_picker = None

    def on_namelist_switched(self, name: str):
        """换名单 -> 丢弃旧的公平历史，避免污染"""

        self._fair_picker = None
