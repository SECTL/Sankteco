"""
主页面, 
此页面是本项目的主要GUI界面, 包含与各子页面的交互逻辑, 控件响应等, 
引用时可作 MainUI
"""

import asyncio

from PySide2.QtWidgets import QWidget
from PySide2.QtGui import QColor
from qfluentwidgets import FluentWindow, qconfig, Theme, setTheme, setThemeColor, isDarkTheme
from qfluentwidgets import FluentIcon as FI

from app_const_var import AssetsPathTXT
from app_config import AppConfig
from ui.ui_str import MainUIString, BasicString

# 插件相关导入
from plugin.loader import PluginLoader
from plugin.context import PluginContext
from plugin.store_ui import PluginStorePage
from plugin.signals import plugin_signals


class MainWindow(FluentWindow):
    """应用程序主窗口, 继承自FluentWindow"""

    def __init__(self) -> None:
        """初始化主窗口"""
        super().__init__()

        # 加载配置文件
        self.cfg = AppConfig()
        qconfig.load(AssetsPathTXT.APP_CONFIG, self.cfg)

        # 声明插件相关属性
        self.plugin_context = None
        self.plugin_loader = None
        self.plugin_store_page = None
        self.plugin_widgets = {}

        # 初始化首选项引用
        self.settings_window = None

        # 运行导入子页面的asyncio程序
        asyncio.run(self.import_ui())

        # 初始化窗口设置
        self.init_window()

        # 插件系统集成(包含初始化侧边栏)
        self._init_plugin_system()

        # 初始化信号连接函数
        self.signal_connection()

    # ========== 异步导入子页面 ==========

    async def import_pray_ui(self) -> None:
        """导入并重命名 祈福 子页面的协程"""
        from ui.pray_ui.pray_ui_logic import PrayUILogic

        self.pray_ui = PrayUILogic(self)
        self.pray_ui.setObjectName(MainUIString.SUBPAGE_PRAY_OBJNAME)

    async def import_information_ui(self) -> None:
        """导入并重命名 信息 子页面的协程"""
        from ui.informations_ui.informations_ui_logic import InformationUILogic

        self.information_ui = InformationUILogic(self)
        self.information_ui.setObjectName(MainUIString.SUBPAGE_INFORMATION_OBJNAME)

        if self.information_ui.docs_reader_ui is not None:
            self.information_ui.docs_reader_ui.setWindowIconText(self.windowIconText())

    async def import_settings_window(self) -> None:
        """创建打开 首选项窗口 按钮的协程"""
        from qfluentwidgets import NavigationPushButton

        # 创建一个按钮
        self.settings_button = NavigationPushButton(
            FI.SETTING,
            MainUIString.SUBPAGE_SETTINGS_NAVNAME,
            isSelectable=False,  # 不可选中(因为不切换页面)
            parent=self.navigationInterface,
        )
        # 绑定点击事件
        self.settings_button.clicked.connect(self.open_settings_window)

    async def import_ui(self) -> None:
        """导入子页面的基础函数"""
        await asyncio.gather(
            self.import_pray_ui(),
            self.import_information_ui(),
            self.import_settings_window(),
        )

    # ========== 导航栏初始化 ==========

    def init_navigation(self) -> None:
        """初始化导航栏, 添加各个子界面"""
        from qfluentwidgets import NavigationItemPosition

        self.addSubInterface(
            self.pray_ui,
            FI.QUESTION,
            MainUIString.SUBPAGE_PRAY_NAVNAME,
            NavigationItemPosition.TOP,
        )
        self.addSubInterface(
            self.plugin_store_page,  # type: ignore
            FI.APPLICATION,
            "插件商店",
            NavigationItemPosition.BOTTOM,
        )
        self.navigationInterface.addWidget(
            "settings_button",
            self.settings_button,
            position=NavigationItemPosition.BOTTOM,
        )
        self.addSubInterface(
            self.information_ui,
            FI.INFO,
            MainUIString.SUBPAGE_INFORMATION_NAVNAME,
            NavigationItemPosition.BOTTOM,
        )

    # ========== 窗口设置 ==========

    def init_window(self) -> None:
        """初始化窗口设置"""
        self._apply_theme()
        self.resize(1080, 768)
        self.setWindowTitle(BasicString.APP_MAINWINDOW_TITLE)

    def _apply_theme(self, theme: Theme = None) -> None:  # type: ignore
        """读取内置配置项并应用主题 + 同步图标"""
        from PySide2.QtGui import QIcon

        # 获取当前主题(Theme 枚举)
        if theme is None:
            theme = qconfig.get(qconfig.themeMode)

        # 切换主题
        setTheme(theme)

        # 同步图标
        icon_path = (
            AssetsPathTXT.APP_ICON_DARK_PATH
            if isDarkTheme()
            else AssetsPathTXT.APP_ICON_LIGHT_PATH
        )
        self.setWindowIcon(QIcon(icon_path))
        if self.information_ui.docs_reader_ui is not None:
            self.information_ui.docs_reader_ui.setWindowIcon(QIcon(icon_path))
        if self.settings_window is not None:
            self.settings_window.setWindowIcon(QIcon(icon_path))
            
    def _apply_theme_color(self, color: QColor) -> None:
        """读取内置配置项并应用主题色"""
        
        # 获取当前主题(Theme 枚举)
        if color is None:
            color = qconfig.get(qconfig.themeMode)
            
        # 切换主题色
        setThemeColor(color)

    # ========== 信号连接 ==========

    def signal_connection(self) -> None:
        """信号连接函数"""

        # 主题更改信号
        qconfig.themeChanged.connect(self._apply_theme)
        
        # 主题色更改信号
        qconfig.themeColorChanged.connect(self._apply_theme_color)

        # 插件信号(如果插件商店已创建)
        if self.plugin_store_page is not None:
            self.plugin_store_page.plugin_toggle_requested.connect(
                self._on_plugin_toggle
            )
            self.plugin_store_page.plugin_uninstall_requested.connect(
                self._on_plugin_uninstall
            )
            # 安装和更新信号(后续实现)
            self.plugin_store_page.plugin_install_requested.connect(
                self._on_plugin_install
            )
            self.plugin_store_page.plugin_update_requested.connect(
                self._on_plugin_update
            )
            print("插件信号已连接")

        # 全局插件信号(用于跨组件通信)
        plugin_signals.plugin_installed.connect(self._on_plugin_installed)
        plugin_signals.plugin_uninstalled.connect(self._on_plugin_uninstalled)
        plugin_signals.plugin_enabled.connect(self._on_plugin_enabled)
        plugin_signals.plugin_disabled.connect(self._on_plugin_disabled)
        plugin_signals.refresh_store_requested.connect(self._refresh_store)

    # ========== 首选项窗口初始化 ==========

    def open_settings_window(self):
        """打开独立的设置窗口(单例模式)"""
        from PySide2.QtCore import Qt
        from ui.settings_window import SettWindow

        if self.settings_window is None:
            self.settings_window = SettWindow()
            # 设置窗口关闭后自动销毁,并清空引用
            self.settings_window.setAttribute(Qt.WA_DeleteOnClose, True)  # type: ignore
            # 连接窗口的 destroyed 信号,以便在窗口关闭后清空引用
            self.settings_window.destroyed.connect(self._on_settings_closed)
            # 更新一次主题以应用图标
            self._apply_theme()
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def _on_settings_closed(self):
        """当设置窗口被关闭时,清空引用"""

        self.settings_window = None

    # ========== 插件系统初始化 ==========

    def _init_plugin_system(self) -> None:
        """初始化插件系统(加载插件、创建商店页面、注册插件)"""

        # 1. 创建插件上下文
        self.plugin_context = PluginContext(self, self.cfg)

        # 2. 加载所有插件
        loader = PluginLoader()
        loaded_count = loader.load_all_plugins()
        self.plugin_loader = loader

        # 3. 创建插件商店页面并添加到导航栏
        self.plugin_store_page = PluginStorePage(loader, self)
        self.plugin_store_page.setObjectName("plugin_store_page")

        # 4. 初始化导航栏(包含商店页面)
        self.init_navigation()

        # 5. 如果没有插件,提前返回
        if loaded_count == 0:
            print("没有发现任何插件")
            return

        # 6. 注册每个已启用的插件到主窗口
        for plugin_id in loader.get_all_plugin_ids():
            register_func = loader.get_register_func(plugin_id)
            if not register_func:
                continue

            self.plugin_context.set_plugin_id(plugin_id)

            try:
                widget = register_func(self.plugin_context)
                if widget is not None and isinstance(widget, QWidget):
                    meta = loader.get_plugin_meta(plugin_id)
                    icon = meta.get("icon", "APPLICATION")
                    name = meta.get("name", plugin_id)

                    widget.setObjectName(f"plugin_page_{plugin_id}")
                    self.plugin_context.add_page(widget, icon, name)
                    self.plugin_widgets[plugin_id] = widget
                    print(f"插件 '{name}' 已添加到导航栏")
                else:
                    print(f"插件 {plugin_id} 未返回有效的 QWidget(可能为后台插件)")
            except Exception as e:
                print(f"注册插件 {plugin_id} 时发生错误: {e}")
                import traceback

                traceback.print_exc()

        # 7. 同步插件商店卡片状态
        self.plugin_store_page._sync_all_card_states()

    # ========== 插件核心操作 ==========

    def _enable_plugin(self, plugin_id: str, plugin_name: str) -> None:
        """启用插件:加载并添加到导航栏"""

        try:
            register_func = self.plugin_loader.enable_plugin(
                plugin_id, self.plugin_context
            )
            if not register_func:
                self._show_plugin_info(f"插件「{plugin_name}」加载失败", "error")
                self._update_card_state(plugin_id, False)
                return

            self.plugin_context.set_plugin_id(plugin_id)
            widget = register_func(self.plugin_context)

            if widget is not None and isinstance(widget, QWidget):
                meta = self.plugin_loader.get_plugin_meta(plugin_id)
                icon = meta.get("icon", "APPLICATION")
                name = meta.get("name", plugin_id)

                widget.setObjectName(f"plugin_page_{plugin_id}")
                self.plugin_widgets[plugin_id] = widget

                from qfluentwidgets import NavigationItemPosition, FluentIcon

                try:
                    icon_enum = getattr(
                        FluentIcon, icon.upper(), FluentIcon.APPLICATION
                    )
                except:
                    icon_enum = FluentIcon.APPLICATION

                self.addSubInterface(
                    widget, icon_enum, name, NavigationItemPosition.TOP
                )
                self._show_plugin_info(f"插件「{plugin_name}」已启用", "success")
            else:
                self._show_plugin_info(f"插件「{plugin_name}」已启用(后台插件)", "info")

        except Exception as e:
            self._show_plugin_info(f"启用插件出错: {e}", "error")
            import traceback

            traceback.print_exc()
            self._update_card_state(plugin_id, False)

    def _disable_plugin(self, plugin_id: str, plugin_name: str) -> None:
        """禁用插件:从导航栏移除"""

        try:
            self._remove_plugin_page(plugin_id)
            self.plugin_loader.disable_plugin(plugin_id)
            self._show_plugin_info(f"插件「{plugin_name}」已禁用", "success")
        except Exception as e:
            self._show_plugin_info(f"禁用插件出错: {e}", "error")
            self._update_card_state(plugin_id, True)

    def _uninstall_plugin(self, plugin_id: str) -> None:
        """卸载插件流程(内部)"""

        self._remove_plugin_page(plugin_id)
        success = self.plugin_loader.uninstall_plugin(plugin_id)
        if success:
            self._show_plugin_info(f"插件已卸载", "success")
            self._refresh_store()
        else:
            self._show_plugin_info(f"卸载失败,请检查日志", "error")

    def _load_single_plugin(self, plugin_id: str) -> None:
        """加载单个插件(用于安装后自动加载)"""

        register_func = self.plugin_loader._load_single_plugin(plugin_id)
        if register_func:
            self.plugin_context.set_plugin_id(plugin_id)
            widget = register_func(self.plugin_context)
            if widget is not None and isinstance(widget, QWidget):
                meta = self.plugin_loader.get_plugin_meta(plugin_id)
                icon = meta.get("icon", "APPLICATION")
                name = meta.get("name", plugin_id)
                widget.setObjectName(f"plugin_page_{plugin_id}")
                self.plugin_context.add_page(widget, icon, name)
                self.plugin_widgets[plugin_id] = widget
                print(f"插件 '{name}' 已添加到导航栏")

    # ========== 插件UI辅助 ==========

    def _remove_plugin_page(self, plugin_id: str) -> bool:
        """从导航栏和堆叠中移除插件页面"""

        widget = self.plugin_widgets.pop(plugin_id, None)
        if not widget:
            target_name = f"plugin_page_{plugin_id}"
            for child in self.children():
                if hasattr(child, "objectName") and child.objectName() == target_name:
                    widget = child
                    break

        if not widget:
            print(f"未找到插件 {plugin_id} 的页面")
            return False

        if hasattr(self, "removeInterface"):
            self.removeInterface(widget, isDelete=True)
            print(f"已移除插件页面: {plugin_id}")
            return True

        # 手动移除兼容方案
        from PySide2.QtWidgets import QStackedWidget

        stacked = None
        for child in self.children():
            if isinstance(child, QStackedWidget):
                stacked = child
                break

        if stacked:
            idx = stacked.indexOf(widget)
            if idx != -1:
                stacked.removeWidget(widget)
                widget.deleteLater()
                print(f"已从堆叠中移除插件页面: {plugin_id}")
                return True

        return False

    def _update_card_state(self, plugin_id: str, is_active: bool) -> None:
        """更新插件商店中对应卡片的状态"""

        if self.plugin_store_page is not None:
            self.plugin_store_page._update_card_state(plugin_id, is_active)

    def _refresh_store(self) -> None:
        """刷新插件商店页面"""

        if self.plugin_store_page is not None:
            self.plugin_store_page._refresh_plugin_list()
            self.plugin_store_page.refresh_online_list()

    def _show_plugin_info(self, message: str, level: str = "info") -> None:
        """显示插件通知(使用 InfoBar)"""
        from qfluentwidgets import InfoBar

        if level == "success":
            InfoBar.success(title="提示", content=message, parent=self, duration=2000)
        elif level == "error":
            InfoBar.error(title="错误", content=message, parent=self, duration=3000)
        else:
            InfoBar.info(title="提示", content=message, parent=self, duration=2000)

    # ========== 插件信号槽 ==========

    def _on_plugin_toggle(self, plugin_id: str, enable: bool) -> None:
        """处理启用/禁用请求"""

        meta = self.plugin_loader.get_plugin_meta(plugin_id)
        plugin_name = meta.get("name", plugin_id)

        if enable:
            self._enable_plugin(plugin_id, plugin_name)
        else:
            self._disable_plugin(plugin_id, plugin_name)

    def _on_plugin_uninstall(self, plugin_id: str) -> None:
        """处理卸载请求(含确认对话框)"""
        from qfluentwidgets import MessageBox

        meta = self.plugin_loader.get_plugin_meta(plugin_id)
        plugin_name = meta.get("name", plugin_id)

        msg_box = MessageBox(
            title="确认卸载",
            content=f"确定要卸载插件「{plugin_name}」吗？\n\n卸载后将删除插件文件,此操作不可恢复",
            parent=self,
        )
        if msg_box.exec_():
            self._uninstall_plugin(plugin_id)

    def _on_plugin_install(self, plugin_id: str):
        """处理安装请求"""

        self._load_single_plugin(plugin_id)
        self._refresh_store()

    def _on_plugin_update(self, plugin_id: str) -> None:
        """处理更新请求(待实现)"""

        self._show_plugin_info(f"更新插件 {plugin_id} 功能开发中", "info")

    def _on_plugin_installed(self, plugin_id: str) -> None:
        """插件安装完成信号"""

        self._load_single_plugin(plugin_id)
        self._refresh_store()

    def _on_plugin_uninstalled(self, plugin_id: str) -> None:
        """插件卸载完成信号"""

        self._refresh_store()

    def _on_plugin_enabled(self, plugin_id: str) -> None:
        """插件启用信号"""

        # 由 _enable_plugin 实际处理,此处仅用于全局通知
        pass

    def _on_plugin_disabled(self, plugin_id: str) -> None:
        """插件禁用信号"""

        # 由 _disable_plugin 实际处理,此处仅用于全局通知
        pass
