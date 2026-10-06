# 插件元数据（必须定义）
__plugin_meta__ = {
    "id": "plugin_template",
    "name": "Sankteco示例插件",
    "generation": 1,
    "version": "1.0.0",
    "description": "这是一个用于测试的插件",
    "author": "Sankteco",
    "icon": "INFO",
    "entry": "main.py",
    "parent_route": None,
}


def register(context):
    """
    插件注册函数（必须实现）
    :param context: 主程序传递的 PluginContext 对象
    :return: 返回一个 QWidget 实例（作为页面），或者返回 None（纯后台插件）
    """
    from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout
    from loguru import logger

    # 获取插件专属数据目录
    data_dir = context.get_plugin_data_dir()
    logger.info(f"插件数据目录: {data_dir}")

    widget = QWidget()
    widget.setObjectName("demo_plugin_page")
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Hello from Plugin!"))

    return widget


def unregister(context):
    """插件卸载前的清理函数（可选）"""
    print("插件正在卸载...")
