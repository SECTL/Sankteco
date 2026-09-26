"""
UI字符串文件
本文件用于储存UI中所需的所有字符串
"""

import gettext, json
from app_const_var import AssetsPathTXT, LogicFilesString

# 读取配置文件以获取语言配置
with open(AssetsPathTXT.APP_CONFIG, "r", encoding="utf-8") as f:
    json_data = json.load(f)
    language_config = json_data[LogicFilesString.LANG_JSON_1][
        LogicFilesString.LANG_JSON_2
    ]

# 初始化gettext翻译
_ = gettext.translation(
    LogicFilesString.LANG_DOMAIN,
    LogicFilesString.LANG_LOCALEDIR,
    [language_config],
    fallback=True,
).gettext


class BasicString:
    """项目基础信息字符串类"""

    NONE_TEXT = ""

    # 项目本体信息
    APP_NAME = "Sankteco"
    APP_PLATFORM = "Python"
    APP_GENERATION = "GENERATION" + " " + str("Dev")
    APP_VERSION = "VERSION" + " " + str("Dev")
    APP_VERSION_TYPE = "Dev"
    APP_COPYTYPE = "Copyleft, GPL-3.0, SECTL, 2023~2026."

    # 窗口标题信息
    APP_MAINWINDOW_TITLE = f"{APP_NAME} {APP_GENERATION}"
    APP_DOCSRUI_TITLE = APP_MAINWINDOW_TITLE + ":" + _("文档阅读")


class PrayUIString:
    """祈福 子页面字符串,
    仅包含 pray_ui.py 相关字符串,
    不包含隶属于主程序多UI交互的字符串"""

    # 一言显示 部分
    HITOKOTO_SHOW_LABEL_DEFAUT = _("旗开得胜,一举夺魁！")

    # 点名结果显示 部分
    PRAY_RESULT_LIST_DEFAULT = _("别紧张")

    # 点名快捷设置 部分
    PRAY_BUTTON_TEXT = _("祈福")
    PRAY_NAMELIST_CHOOSE_LIST_DEFAULT = _("请选择名单")
    PRAY_ALGORITHM_LIST_DEFAULT = _("默认公平随机算法")
    PRAY_NUMBER_SUBTRACT_BUTTON_TEXT = "-"
    PRAY_NUMBER_PLUS_BUTTON_TEXT = "+"
    PRAY_SEX_LIST_ALL = _("所有性别")
    PRAY_SEX_LIST_MALE = _("男")
    PRAY_SEX_LIST_FEMALE = _("女")
    PRAY_SEX_LIST_NOTBINARY = _("非二元性别")
    PRAY_GROUP_LIST_DEFAULT = _("请选择组别")
    PRAY_TAG_LIST_DEFAULT = _("请选择标签")
    PRAY_RESET_SETTING_BUTTON_TEXT = _("重置抽选")


class InfoUIString:
    """信息 子页面字符串"""

    # 页面标题
    FRAME_TITLE = _("信息")

    # ShowInfobar 类
    SHOWINFOBAR_OFFLINE_TITLE = _("错误！")
    SHOWINFOBAR_OFFLINE_CONTENT = _("无法找到离线文档！")
    SHOWINFOBAR_ONLINE_TITLE = _("警告！")
    SHOWINFOBAR_ONLINE_CONTENT = _("无法连接到服务器！")

    # 支持 部分
    SUPPTCARD_TITLE = _("支持")
    SUPPTCARD_OFFLINEDOCBUTTON = _("查看")
    SUPPTCARD_ONLINEDOCBUTTON = _("查看")
    SUPPTCARD_OFFLINEDOCGROUPTITLE = _("离线帮助文档")
    SUPPTCARD_OFFLINEDOCGROUPCONTEXT = _("查看保存于本地的帮助文档, 如果有的话")
    SUPPTCARD_ONLINEDOCGROUPTITLE = _("在线帮助文档")
    SUPPTCARD_ONLINEDOCGROUPCONTEXT = _("访问项目官网获取在线帮助文档")


class SettNLUIString:
    """首选项-名单 页面字符串"""

    # 页面标题
    FRAME_TITLE = _("名单管理")

    # 询问新名单的标识符对话框
    ASK_NEW_ID_MSG_TITLE = _("键入新名单标识符")
    ASK_NEW_ID_MSG_LINEEDIT_TEXT = _("以英文字母、汉字、数字组成, 不能以数字开头")

    # 当前名单
    NOW_NAMELIST_CARD_TITLE = _("当前名单")
    NOW_NAMELIST_CARD_CONTEXT = _("选择要管理的名单")

    # 名单操作
    REFRESH_NAMELIST_BUTTON_TEXT = _("刷新")
    ADD_NEW_NAMELIST_BUTTON_TEXT = _("新建名单")
    RENAME_NAMELIST_BUTTON_TEXT = _("重命名名单")
    DEL_NAMELIST_BUTTON_TEXT = _("删除名单")
    IMPORT_NAMELIST_BUTTON_TEXT = _("导入...")
    EXPORT_NAMELIST_BUTTON_TEXT = _("导出...")

    # 名单表格
    NAMETABLE_HEADER_LABEL_EXIST = _("存在?")
    NAMETABLE_HEADER_LABEL_NO = _("学号")
    NAMETABLE_HEADER_LABEL_NAME = _("姓名")
    NAMETABLE_HEADER_LABEL_GENDER = _("性别")
    NAMETABLE_HEADER_LABEL_GROUP = _("小组")
    NAMETABLE_HEADER_LABEL_TIP = _("标签")

    # 导入名单部分
    # 导入名单对话框
    IMPORT_NAMELIST_DIALOG_TITLE = _("选择一个名单文件")
    EXPORT_NAMELIST_DIALOG_TITLE = _("选择一个储存名单文件的位置")
    NAMELIST_DIALOG_FILTER_TXT = _("文本文件")
    NAMELIST_DIALOG_FILTER_JSON = _("JSON文件")
    NAMELIST_DIALOG_FILTER_YAML = _("YAML配置文件")
    NAMELIST_DIALOG_FILTER_CSV = _("逗号分隔符文件")
    NAMELIST_DIALOG_FILTER_XLSX_XLS_ODS = _("电子表格文档")
    NAMELIST_DIALOG_FILTER_XLSX = _("Excel2007~365电子表格文档")
    NAMELIST_DIALOG_FILTER_XLS = _("Excel97~2003电子表格文档")
    NAMELIST_DIALOG_FILTER_ODS = _("开放电子表格文档格式")
    NAMELIST_DIALOG_FILTER_QR = _("二维码")


class SettThemeUIString:
    """首选项-主题 页面字符串"""

    # 页面标题
    FRAME_TITLE = _("主题")

    # 显示主题
    THEME_CARD_TITLE = _("显示主题")
    THEME_CARD_CONTEXT = _("更改程序的显示主题")
    THEME_CARD_TEXT_LIGHT = _("浅色")
    THEME_CARD_TEXT_DARK = _("深色")
    THEME_CARD_TEXT_AUTO = _("跟随系统")


class SettLangUIString:
    """首选项-语言 子页面字符串"""

    # 页面标题
    FRAME_TITLE = _("语言")

    # 语言选择
    SCREEN_LANGUAGE_TITLE = _("显示语言")
    SCREEN_LANGUAGE_CONTEXT = _("选择将在屏幕上显示的语言")
    SCREEN_LANGUAGE_TEXT_ZH_CN = "简体中文"
    SCREEN_LANGUAGE_TEXT_EO = "Esperanto"
    SCREEN_LANGUAGE_TEXT_EMOJI = "Emoji"

    # 加入翻译计划
    JOIN_TRANSLATION_TITLE = _("加入翻译计划")
    JOIN_TRANSLATION_CONTEXT = _("加入项目的在线翻译工程, 为本地化做出贡献")
    JOIN_TRANSLATION_HYPERLINK_TEXT = _("跳转")


class DocsRUIString:
    """信息-文档阅读 孙页面字符串"""

    # 当前文档
    NOW_DOC_CARD_TITLE = _("当前文档")
    NOW_DOC_CARD_CONTEXT = _("选择要查看的文档")


class MainUIString:
    """主页面 字符串,
    包含 main_ui.py 相关字符串,
    包含隶属于主程序多UI交互的字符串"""

    # 子页面对象名
    SUBPAGE_INFORMATION_OBJNAME = "subpage_information"
    SUBPAGE_SETTINGS_OBJNAME = "subpage_settings"
    SUBPAGE_PRAY_OBJNAME = "subpage_pray"

    # 子页面导航窗口显示字段
    SUBPAGE_INFORMATION_NAVNAME = _("信息")
    SUBPAGE_SETTINGS_NAVNAME = _("首选项")
    SUBPAGE_PRAY_NAVNAME = _("祈福")


class SettWindowString:
    """首选项 页面字符串,
    包含 settings_window.py 相关字符串"""

    # 子页面对象名
    NAMELISTS_UI_OBJNAME = "namelists_ui"
    THEME_UI_OBJNAME = "theme_ui"
    LANGUAGE_UI_OBJNAME = "language_ui"

    # 子页面导航窗口显示字段
    NAMELISTS_UI_NAVNAME = _("名单管理")
    THEME_UI_NAVNAME = _("主题")
    LANGUAGE_UI_NAVNAME = _("语言")

    # 窗口显示字段
    SETTWINDOW_TITLE = f"{BasicString.APP_NAME} {BasicString.APP_GENERATION}: " + _(
        "首选项"
    )
