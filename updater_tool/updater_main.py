"""
独立更新器,
在主程序退出后, 把 stage_dir 里的新版本文件覆盖到 app_dir,
更新 VERSION.txt, 然后重启主程序;\n
仅依赖标准库, 用 PyInstaller onefile 打包, 无 Qt 依赖
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


# 日志写到临时目录, 便于排查
_LOG_DIR = Path(os.environ.get("TEMP", "/tmp"))
LOG_FILE = _LOG_DIR / "sankteco_updater.log"

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("updater")


# ==================== 进程等待 ====================


def wait_pid_exit(pid: int, timeout: float = 120.0) -> bool:
    """轮询等待指定 pid 的进程消失"""
    
    start = time.time()
    while time.time() - start < timeout:
        if not _pid_alive(pid):
            log.info(f"主进程 {pid} 已退出")
            return True
        time.sleep(0.5)
    log.warning(f"等待主进程 {pid} 退出超时")
    return False


def _pid_alive(pid: int) -> bool:
    """跨平台判断进程是否存活"""
    
    if sys.platform == "win32":
        try:
            # CREATE_NO_WINDOW 避免弹出黑框
            out = subprocess.check_output(
                ["tasklist", "/FI", f"PID eq {pid}"],
                stderr=subprocess.DEVNULL,
                creationflags=0x08000000,
            ).decode("gbk", errors="ignore")
            return str(pid) in out
        except Exception:
            return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False


# ==================== 文件操作 ====================


def replace_tree(
    src: Path, dst: Path, exclude=("_update", "data", "logs")
) -> None:
    """把 src 里的内容覆盖到 dst, 保留 exclude 里的名字;
    默认保护 _update(更新缓存), data(用户数据), logs(日志)"""
    # 删除 dst 里的旧内容(被保护的除外)
    for item in dst.iterdir():
        # 如果在豁免名单里, 或者以 . 开头的隐藏文件，直接跳过
        if item.name in exclude or item.name.startswith("."):
            continue
            
        try:
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
            else:
                item.unlink()
        except PermissionError:
            log.warning(f"无法删除 {item} (被占用)")

    # 把新内容复制过去
    for item in src.iterdir():
        target = dst / item.name
        
        # 如果新包里带了 data, 为了安全, 我们只把文件合并进去, 不覆盖同名的
        # 如果不想合并, 可以直接 continue 跳过
        if item.name in exclude:
            continue
            
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)


def write_version_file(app_dir: Path, version: str) -> None:
    """把版本号写入 VERSION.txt """
    
    ver_path = app_dir / "VERSION.txt"
    ver_path.write_text(version, encoding="utf-8")
    log.info(f"VERSION.txt 已更新为 {version}")


# ==================== 主流程 ====================


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pid", type=int, required=True)
    parser.add_argument("--app-dir", type=Path, required=True)
    parser.add_argument("--stage-dir", type=Path, required=True)
    parser.add_argument("--backup-dir", type=Path, required=True)
    parser.add_argument("--exe-name", default="Sankteco.exe")
    parser.add_argument("--target-version", required=True)
    parser.add_argument("--cleanup-marker", type=Path, default=None)
    args = parser.parse_args()

    log.info(f"更新器启动: pid={args.pid}, version={args.target_version}")

    # 等待主程序退出
    if not wait_pid_exit(args.pid):
        log.error("主进程未退出, 放弃更新")
        return

    # 备份当前 install_dir
    try:
        if args.backup_dir.exists():
            shutil.rmtree(args.backup_dir, ignore_errors=True)
        shutil.copytree(
            args.app_dir,
            args.backup_dir,
            ignore=shutil.ignore_patterns("_update"),
            symlinks=True,
        )
        log.info("备份完成")
    except Exception:
        log.exception("备份失败")
        return

    # 覆盖文件
    try:
        replace_tree(args.stage_dir, args.app_dir)
        log.info("文件替换完成")
    except Exception:
        log.exception("替换失败, 尝试回滚")
        try:
            replace_tree(args.backup_dir, args.app_dir)
            log.info("回滚完成")
        except Exception:
            log.exception("回滚失败")
        # 清理 pending 后退出
        if args.cleanup_marker and args.cleanup_marker.exists():
            args.cleanup_marker.unlink()
        return

    # 更新 VERSION.txt
    try:
        write_version_file(args.app_dir, args.target_version)
    except Exception:
        log.exception("写入 VERSION.txt 失败")

    # 清理 pending 标记
    if args.cleanup_marker and args.cleanup_marker.exists():
        try:
            args.cleanup_marker.unlink()
        except Exception:
            log.exception("清理 pending 失败")

    # 重启主程序
    exe = args.app_dir / args.exe_name
    if exe.exists():
        try:
            subprocess.Popen([str(exe)], cwd=str(args.app_dir))
            log.info("主程序已重启")
        except Exception:
            log.exception("重启失败")
    else:
        log.error(f"主程序不存在: {exe}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log.exception("更新器未捕获异常")
        sys.exit(1)
