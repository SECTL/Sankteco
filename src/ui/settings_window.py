"""
首选项 页面,
现在作为独立窗口运行, 包含了所有可操控的设置项,
引用时可作 SettWindow
"""

import asyncio

from qfluentwidgets import FluentWindow
from qfluentwidgets import FluentIcon as FI

from app_config import cfg
from ui.ui_str import SettWindowString


class SettWindow(FluentWindow):
    """首选项窗口, 继承自FluentWindow"""

    def __init__(self) -> None:
        """初始化窗口"""
        super().__init__()

        # 加载配置文件
        self.cfg = cfg

        # 运行导入子页面的asyncio程序
        asyncio.run(self.import_ui())

        # 初始化窗口设置
        self.init_window()

        # 初始化导航栏
        self.init_navigation()

    # ========== 异步导入子页面 ==========

    async def import_namelists_ui(self) -> None:
        """导入并重命名 名单管理 子页面的协程"""
        from ui.settings_ui.settings_namelists_ui_logic import SettNLUILogic

        self.namelists_ui = SettNLUILogic(self)
        self.namelists_ui.setObjectName(SettWindowString.NAMELISTS_UI_OBJNAME)

    async def import_theme_ui(self) -> None:
        """导入并重命名 主题 子页面的协程"""
        from ui.settings_ui.settings_theme_ui import SettThemeUI

        self.theme_ui = SettThemeUI(self.cfg, self)
        self.theme_ui.setObjectName(SettWindowString.THEME_UI_OBJNAME)

    async def import_language_ui(self) -> None:
        """导入并重命名 语言 子页面的协程"""
        from ui.settings_ui.settings_language_ui import SettLangUI

        self.language_ui = SettLangUI(self.cfg, self)
        self.language_ui.setObjectName(SettWindowString.LANGUAGE_UI_OBJNAME)

    async def import_debug_ui(self) -> None:
        """导入并重命名 调试 子页面的协程"""
        from ui.settings_ui.settings_debug_ui import SettDebugUI

        self.debug_ui = SettDebugUI(self.cfg, self)
        self.debug_ui.setObjectName(SettWindowString.DEBUG_UI_OBJNAME)

    async def import_ui(self) -> None:
        """导入子页面的基础函数"""
        await asyncio.gather(
            self.import_namelists_ui(),
            self.import_theme_ui(),
            self.import_language_ui(),
            self.import_debug_ui(),
        )

    # ========== 导航栏初始化 ==========

    def init_navigation(self) -> None:
        """初始化导航栏, 添加各个子界面"""
        from qfluentwidgets import NavigationItemPosition

        # 名单管理
        self.addSubInterface(
            self.namelists_ui,
            FI.PEOPLE,
            SettWindowString.NAMELISTS_UI_NAVNAME,
            NavigationItemPosition.TOP,
        )

        # 主题
        self.addSubInterface(
            self.theme_ui,
            FI.CONSTRACT,
            SettWindowString.THEME_UI_NAVNAME,
            NavigationItemPosition.TOP,
        )

        # 语言
        self.addSubInterface(
            self.language_ui,
            FI.LANGUAGE,
            SettWindowString.LANGUAGE_UI_NAVNAME,
            NavigationItemPosition.TOP,
        )

        # 调试
        self.addSubInterface(
            self.debug_ui,
            FI.IOT,
            SettWindowString.DEBUG_UI_NAVNAME,
            NavigationItemPosition.BOTTOM,
        )

    # ========== 窗口设置 ==========

    def init_window(self) -> None:
        """初始化窗口设置"""

        self.resize(1080, 768)
        self.setWindowTitle(SettWindowString.SETTWINDOW_TITLE)
