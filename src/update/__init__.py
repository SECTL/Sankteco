"""Sankteco 更新模块.

对外暴露:
    UpdateWorker - 后台更新线程
    read_current_version / write_current_version - VER.txt 读写
    check_pending_on_startup - 启动时 pending 恢复
"""

from .manager import read_current_version, write_current_version
from .rollback import check_pending_on_startup
from .signals import UpdateSignals
from .worker import UpdateWorker

__all__ = [
    "UpdateWorker",
    "UpdateSignals",
    "read_current_version",
    "write_current_version",
    "check_pending_on_startup",
]
