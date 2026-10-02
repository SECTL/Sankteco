"""
UI日志面板(含 Qt sink),
本文件用于将UI产生的日志安全地记录到统一文件中
"""

from shiboken2 import isValid
from loguru import logger
from PySide2.QtCore import QObject, Signal, Slot
from qfluentwidgets import TextEdit


class LogEmitter(QObject):
    """跨线程安全地把日志消息投递到 UI 线程"""

    log_signal = Signal(str)


class QtLogSink:
    """自定义 Loguru sink：把日志写到 QFluentWidgets 的 TextEdit"""

    def __init__(self, text_edit: TextEdit):

        self.text_edit = text_edit
        self.emitter = LogEmitter()
        self.emitter.log_signal.connect(self._append)
        self._sink_id = None

    def write(self, message: str):

        # 由 Loguru 调用，可能处于任意线程；通过信号切到 UI 线程
        self.emitter.log_signal.emit(message.rstrip())

    @Slot(str)
    def _append(self, message: str):

        # 关键:先判断 C++ 对象是否仍然有效
        if not isValid(self.text_edit):
            return
        try:
            self.text_edit.append(message)
            sb = self.text_edit.verticalScrollBar()
            # 自动滚动到底部
            sb.setValue(sb.maximum())
        except RuntimeError:
            # 极端竞态下仍可能抛错,吞掉即可
            return

    def attach(self, level="DEBUG"):
        """把本 sink 注册到 Loguru，并记录 sink_id 以便后续移除"""

        self._sink_id = logger.add(
            self.write,
            level=level,
            format="{time:HH:mm:ss} | {level: <8} | {message}",
            colorize=False,  # TextEdit 不支持 ANSI 颜色
        )

    def detach(self):
        """窗口关闭时可调用，避免悬挂引用"""

        # 移除 Loguru sink(不再有新消息进来)
        if self._sink_id is not None:
            logger.remove(self._sink_id)
            self._sink_id = None
        # 断开信号连接(队列里已有的消息也不再投递到 _append)
        try:
            self.emitter.log_signal.disconnect(self._append)
        except (RuntimeError, TypeError):
            pass
