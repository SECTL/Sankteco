"""
日志配置文件,
此文件用于初始化配置日志功能
"""

import sys
from pathlib import Path
from datetime import timedelta

from loguru import logger


# 确保日志目录存在
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

_file_sink_ids = []


def setup_basic_logging(log_days: int = 30, err_days: int = 60):
    """基础日志配置:文件 + 控制台,参数由调用方注入"""

    # 移除 Loguru 默认的 stderr sink，避免重复输出
    logger.remove()
    _file_sink_ids.clear()

    # 控制台输出(带颜色，便于开发调试)
    logger.add(
        sys.stderr,
        level="DEBUG",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )

    # 全量文件日志(按天轮转，保留 30 天)
    _file_sink_ids.append(logger.add(
        LOG_DIR / "core_{time:YYYY-MM-DD}.log",
        level="DEBUG", rotation="00:00",
        retention=timedelta(days=log_days),
        compression="zip", encoding="utf-8", enqueue=True,
        backtrace=True, diagnose=True,
    ))

    # 错误日志单独一份，方便排查
    _file_sink_ids.append(logger.add(
        LOG_DIR / "error_{time:YYYY-MM-DD}.log",
        level="ERROR", rotation="00:00",
        retention=timedelta(days=err_days),
        compression="zip", encoding="utf-8", enqueue=True,
        backtrace=True, diagnose=True,
    ))

    logger.info("基础日志系统初始化完成")
    
def reconfigure_file_sinks(log_days: int, err_days: int):
    """配置变化后重配文件 sink"""
    
    for sid in _file_sink_ids:
        logger.remove(sid)
    _file_sink_ids.clear()
    
    # 全量文件日志(按天轮转，保留 30 天)
    _file_sink_ids.append(logger.add(
        LOG_DIR / "core_{time:YYYY-MM-DD}.log",
        level="DEBUG", rotation="00:00",
        retention=timedelta(days=log_days),
        compression="zip", encoding="utf-8", enqueue=True,
        backtrace=True, diagnose=True,
    ))

    # 错误日志单独一份，方便排查
    _file_sink_ids.append(logger.add(
        LOG_DIR / "error_{time:YYYY-MM-DD}.log",
        level="ERROR", rotation="00:00",
        retention=timedelta(days=err_days),
        compression="zip", encoding="utf-8", enqueue=True,
        backtrace=True, diagnose=True,
    ))

# 模块被导入时自动执行一次
setup_basic_logging()
