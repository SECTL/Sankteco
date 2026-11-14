"""
子页面:更新( 首选项 的子页面)的UI逻辑文件, 
引用时可作 SettUpdateUILogic / settings_update_ui_logic
"""

from qfluentwidgets import InfoBar, InfoBarPosition

from app_config import AppConfig, AppEnums
from update.worker import UpdateWorker
from ui.settings_ui.settings_update_ui import SettUpdateUI


class SettUpdateUILogic(SettUpdateUI):
    """子页面:更新( 首选项 的子页面)的UI基础逻辑类,
    引用时可作 SettUpdateUILogic / settings_update_ui_logic"""

    def __init__(self, cfg: AppConfig, parent=None):
        super().__init__(cfg, parent)

        self.worker = None

        # 开始检查更新信号连接
        self.update_main_area.check_update_button.clicked.connect(
            self._on_check_clicked
        )

    def _on_check_clicked(self):
        """点击检查更新按钮"""

        if self.worker and self.worker.isRunning():
            return

        # 读取渠道配置
        channel_str = self.cfg.get(self.cfg.UpdateChannel).value

        # 读取自动更新模式
        auto_mode_str = self.cfg.get(self.cfg.AutoUpdateMode).value

        # 创建并启动 Worker
        self.worker = UpdateWorker(channel=channel_str, auto_mode=auto_mode_str)
        self._connect_worker_signals()
        self.worker.start()

    def _connect_worker_signals(self):
        """连接 Worker 的信号到 UI 槽函数"""

        signals = self.worker.signals
        signals.check_started.connect(self._on_check_started)
        signals.check_finished.connect(self._on_check_finished)
        signals.download_started.connect(self._on_download_started)
        signals.update_ready.connect(self._on_update_ready)
        signals.update_error.connect(self._on_error)

        # Worker 线程结束清理
        self.worker.finished.connect(self.worker.deleteLater)

    def _on_check_started(self):
        """开始检查更新"""

        area = self.update_main_area
        area.check_update_button.setEnabled(False)
        area.update_state_indicator.setText("正在检查更新...")
        area.update_progress.start()

    def _on_check_finished(self, version: str, required: bool):
        """更新检查结束"""

        area = self.update_main_area
        if not version:
            area.update_state_indicator.setText("已是最新版本。")
            area.update_progress.stop()
            area.check_update_button.setEnabled(True)
        else:
            area.update_state_indicator.setText(f"发现新版本 {version}, 准备下载...")

    def _on_download_started(self):
        """下载更新包"""

        area = self.update_main_area
        area.update_state_indicator.setText("正在下载更新包...")
        area.update_progress.start()

    def _on_update_ready(self):
        """更新就绪"""

        area = self.update_main_area
        area.update_state_indicator.setText("更新已就绪, 即将重启应用...")
        area.update_progress.stop()

        if (
            self.cfg.get(self.cfg.AutoUpdateMode)
            == AppEnums.AutoUpdateModeEnum.DOWNLOAD
        ):
            InfoBar.success(
                "下载完成",
                "更新包已下载, 等待安装",
                parent=self,
                position=InfoBarPosition.TOP,
            )
            area.check_update_button.setEnabled(True)

    def _on_error(self, title: str, msg: str):
        """更新抛出错误"""

        area = self.update_main_area
        area.update_state_indicator.setText("更新失败。")
        area.update_progress.stop()
        area.check_update_button.setEnabled(True)
        InfoBar.error(
            title, msg, parent=self, position=InfoBarPosition.TOP, duration=5000
        )
