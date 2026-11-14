"""启动时的 pending 恢复.

主程序启动时若发现 pending 标记, 说明上次更新未正常收尾.
本模块只做轻量清理, 真正的文件回滚由独立更新器负责.
"""

from __future__ import annotations

import shutil

from loguru import logger

from app_const_var import AssetsPath


def check_pending_on_startup() -> None:
    """启动时检查未完成的更新.

    情形一: VER.txt 已是目标版本 -> 更新器其实成功了,
        只是没清 pending, 直接清理即可.
    情形二: VER.txt 仍是旧版本 -> 更新器没走完, 但用户当前
        会话仍在旧版本, 无需回滚. 清理残留文件即可.
    无论哪种情形, 都是清理动作, 不做文件替换.
    """
    pending = AssetsPath.PENDING_FLAG
    if not pending.exists():
        return

    try:
        target_version = pending.read_text(encoding="utf-8").strip()
    except Exception:
        target_version = "unknown"

    logger.warning(f"检测到未完成的更新 (目标 {target_version}), 清理残留")

    # 清理 pending
    try:
        pending.unlink()
    except Exception:
        logger.exception("清理 pending 失败")

    # 清理 stage 和 backup
    for d in (AssetsPath.STAGE_DIR, AssetsPath.BACKUP_DIR):
        if d.exists():
            try:
                shutil.rmtree(d, ignore_errors=True)
                logger.debug(f"已清理 {d}")
            except Exception:
                logger.exception(f"清理 {d} 失败")
