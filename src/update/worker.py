"""更新工作线程"""

from __future__ import annotations

import os
import subprocess
import sys

from loguru import logger
from packaging.version import InvalidVersion, Version
from PySide2.QtCore import QThread, QTimer
from PySide2.QtWidgets import QApplication

from app_const_var import AssetsPath
from .manager import (
    UpdateManager,
    fetch_latest_version,
    read_current_version,
)
from .signals import UpdateSignals


class UpdateWorker(QThread):
    """更新流程的工作线程, 负责串联 API 查询、tufup 下载和拉起更新器"""

    def __init__(self, channel: str = "stable", auto_mode: str = "notify", parent=None):
        """
        :param channel: "stable" (正式版) 或 "prerelease" (测试版)
        :param auto_mode: "never", "notify", "download", "install"
        """
        super().__init__(parent)
        self.channel = channel
        self.auto_mode = auto_mode
        self.signals = UpdateSignals()

    def run(self):
        try:
            self.signals.check_started.emit()

            # 读取本地版本并剥离平台后缀, 用于版本比对
            full_current_ver = read_current_version()

            # 请求 SECTL API
            latest_ver = fetch_latest_version(self.channel)
            if not latest_ver:
                self.signals.update_error.emit(
                    "网络异常", "无法获取最新版本信息, 请检查网络。"
                )
                return

            # 比对版本
            try:
                if Version(full_current_ver) >= Version(latest_ver):
                    self.signals.check_finished.emit("", False)  # 已是最新
                    return
            except InvalidVersion:
                self.signals.update_error.emit(
                    "版本异常", f"版本号解析失败: {full_current_ver} / {latest_ver}"
                )
                return

            # 发现新版本, 通知 UI
            self.signals.check_finished.emit(latest_ver, False)

            if self.auto_mode in ("never", "notify"):
                return

            if self.isInterruptionRequested():
                return

            # 实例化 Manager 并执行更新
            mgr = UpdateManager(
                current_version=full_current_ver,
                target_version=latest_ver,
                clean_tag=latest_ver,
            )

            # 提前检查一下 tufup 仓库里是不是真的有这个目标包
            if not mgr.check():
                self.signals.update_error.emit(
                    "更新失败", "服务器上尚未找到对应的更新包, 请稍后再试。"
                )
                return

            self.signals.download_started.emit()

            def progress_hook(done: int, total: int):
                self.signals.download_progress.emit(int(done), int(total))

            install_cb = self._make_install_callback(latest_ver)

            # 调用 tufup 下载并应用, 传入我们的回调
            mgr.apply(progress_hook=progress_hook, install_callback=install_cb)

            # 如果流程没在回调中退出（比如 auto_mode=download）, 则发结束信号
            self.signals.download_finished.emit()
            self.signals.update_ready.emit()

        except Exception as e:
            logger.exception("更新流程异常")
            self.signals.update_error.emit("更新异常", str(e))

    def _make_install_callback(self, target_version: str):
        """构造传给 tufup 的 install 回调"""

        def callback(*args, **kwargs):
            if self.auto_mode == "download":
                logger.info("auto_mode=download, 文件已下载至 stage, 跳过安装")
                return

            try:
                # 写入 pending 标记 (记录带后缀的目标版本)
                AssetsPath.PENDING_FLAG.parent.mkdir(parents=True, exist_ok=True)
                AssetsPath.PENDING_FLAG.write_text(target_version, encoding="utf-8")

                # 启动独立更新器
                self._launch_updater(target_version)

                # 触发主程序退出
                app = QApplication.instance()
                if app:
                    QTimer.singleShot(0, app.quit)

            except Exception:
                logger.exception("install callback 执行失败")
                raise

        return callback

    def _launch_updater(self, target_version: str):
        """启动独立更新器进程"""
        updater_exe = AssetsPath.UPDATER_EXE
        if not updater_exe.exists():
            raise FileNotFoundError(f"未找到更新器: {updater_exe}")

        args = [
            str(updater_exe),
            "--pid",
            str(os.getpid()),
            "--app-dir",
            str(AssetsPath.INSTALL_DIR),
            "--stage-dir",
            str(AssetsPath.STAGE_DIR),
            "--backup-dir",
            str(AssetsPath.BACKUP_DIR),
            "--exe-name",
            AssetsPath.MAIN_EXE_NAME,
            "--target-version",
            target_version,
            "--cleanup-marker",
            str(AssetsPath.PENDING_FLAG),
        ]

        creationflags = 0
        if sys.platform == "win32":
            creationflags = (
                subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
            )

        subprocess.Popen(args, close_fds=True, creationflags=creationflags)
        logger.info(f"独立更新器已启动, 目标版本: {target_version}")
