"""更新流程信号定义,
本模块只承载信号, 不包含任何业务逻辑,
信号由 UpdateWorker 发射, 由 UI 层连接处理,
修改信号时需同步更新 worker 和 UI 两侧
"""

from PySide2.QtCore import QObject, Signal


class UpdateSignals(QObject):
    """更新流程信号集合,
    信号按流程时间轴排列:\n
        check_started -> mirror_switched -> check_finished\n
        -> download_started -> download_progress -> download_finished\n
        -> update_ready / update_error\n
        -> rollback_started -> rollback_finished
    """

    # 开始检查元数据时发射
    check_started = Signal()

    # 检查完成, 参数: (最新版本号, 是否必需)
    # 版本号为空串表示已是最新
    check_finished = Signal(str, bool)

    # 开始下载时发射
    download_started = Signal()

    # 下载进度, 参数: (已下载字节, 总字节)
    download_progress = Signal(int, int)

    # 下载完成时发射
    download_finished = Signal()

    # 更新已就绪, 更新器已启动, 主程序即将退出
    update_ready = Signal()

    # 更新过程中发生错误, 参数: (标题, 详情)
    update_error = Signal(str, str)

    # 开始回滚, 参数是回滚原因
    rollback_started = Signal(str)

    # 回滚完成, 参数是是否成功
    rollback_finished = Signal(bool)
