"""
启动文件, 
此页面是项目的入口, 运行与编译须从此开始
"""

import sys

from PySide2.QtWidgets import QApplication
import logger_config
from loguru import logger
from qfluentwidgets import qconfig

from ui.main_ui import MainWindow
from update.manager import read_current_version, write_current_version
from app_config import cfg
from app_const_var import AssetsPathTXT, AssetsPath
from update import check_pending_on_startup


# 检查未完成的更新
check_pending_on_startup()

# 确保版本文件存在（首次启动时写入默认版本）
if not AssetsPath.VER_FILE.exists():
    write_current_version(read_current_version())

# 加载配置
qconfig.load(AssetsPathTXT.USER_CONFIG, cfg)

# 用配置的值初始化日志
logger_config.setup_basic_logging(
    log_days=cfg.get(cfg.LogFileRetention),
    err_days=cfg.get(cfg.ErrorLogFileRetention),
)


if __name__ == "__main__":
    """程序入口"""

    # 创建QApplication实例
    app = QApplication(sys.argv)

    # 创建主窗口
    w = MainWindow()
    w.show()

    # 启动应用事件循环
    exit_code = app.exec_()
    logger.info(f"程序退出, code={exit_code}")
    sys.exit(exit_code)
