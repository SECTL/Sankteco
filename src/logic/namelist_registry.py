"""
全局名单注册表,
负责扫描名单目录、维护名单列表与当前名单,
引用时可作 NamelistRegistry / namelist_registry
"""

from pathlib import Path
from typing import List, Optional

from PySide2.QtCore import QObject, Signal

from app_const_var import AssetsPathTXT


class NamelistRegistry(QObject):
    """全局名单注册表"""

    # 名单列表发生变化（新建/导入/删除/刷新后发出）
    namelists_changed = Signal(list)  # list[str] 名单文件名列表

    # 当前选中的名单发生变化
    current_namelist_changed = Signal(str)  # 名单文件名

    def __init__(self):
        super().__init__()

        self._namelists: List[str] = []
        self._current: Optional[str] = None

    # ---------- 扫描 ----------
    def scan(self) -> List[str]:
        """扫描名单文件夹，更新内部列表并发出信号"""

        folder = Path(AssetsPathTXT.APP_NAMELISTS_FOLDER)

        self._namelists = sorted(p.name for p in folder.glob("*.json"))
        self.namelists_changed.emit(self._namelists)

        return list(self._namelists)

    # ---------- 读取 ----------
    def get_namelists(self) -> List[str]:

        return list(self._namelists)

    def get_current(self) -> Optional[str]:

        return self._current

    def get_current_path(self) -> Optional[str]:

        if self._current is None:
            return None
        return f"{AssetsPathTXT.APP_NAMELISTS_FOLDER}{self._current}"

    # ---------- 设置 ----------
    def set_current(self, name: str):

        if not name or name == self._current:
            return

        self._current = name
        self.current_namelist_changed.emit(name)


# 全局单例
namelist_registry = NamelistRegistry()
