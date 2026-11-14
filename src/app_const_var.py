"""
常变量文件,
本文件是储存项目常量与变量标准值的文件, 不包括ui的字符串
"""

"""
====================
相对路径常量
====================
"""


class AssetsPathTXT:
    """资源相对路径纯文本类"""

    # 图片
    # 图标
    APP_ICON_DARK_PATH = "assets/icons/app_icon_dark.png"
    APP_ICON_LIGHT_PATH = "assets/icons/app_icon_light.png"

    # 项目详细图
    APP_DETAILEDIMAGE_DARK_PATH = "assets/images/app_detailed_image_dark.png"
    APP_DETAILEDIMAGE_LIGHT_PATH = "assets/images/app_detailed_image_light.png"

    # 音频
    # 默认音乐
    APP_DEFAULT_MUSIC_PATH = ""

    # 默认音效
    APP_DEFAULT_SOUND_PATH = "assets/sounds/notice.wav"

    # 文本文件
    # 文档
    APP_DOCS_FOLDER = "docs/"
    
    # 用户数据
    # 用户数据根目录
    USER_DATA_PATH = "data/"
    
    # 名单
    USER_NAMELISTS_PATH = USER_DATA_PATH + "namelists/"
    
    # 配置文件
    USER_CONFIG = USER_DATA_PATH + "config/" + "app_config.json"


class AssetsPath:
    """资源相对路径类"""

    import sys
    from pathlib import Path

    # 音频
    # 默认音乐
    APP_DEFAULT_MUSIC_PATH = Path(AssetsPathTXT.APP_DEFAULT_MUSIC_PATH)

    # 默认音效
    APP_DEFAULT_SOUND_PATH = Path(AssetsPathTXT.APP_DEFAULT_SOUND_PATH)

    # 更新相关路径
    if getattr(sys, "frozen", False):
        INSTALL_DIR = Path(sys.executable).parent
        ASSETS_DIR = INSTALL_DIR
    else:
        INSTALL_DIR = Path(__file__).resolve().parent.parent
        ASSETS_DIR = INSTALL_DIR
        
    if getattr(sys, "frozen", False):
        BUNDLED_ROOT = INSTALL_DIR / "root.json"
    else:
        # 开发环境下，信任根在 repo/metadata 里
        BUNDLED_ROOT = INSTALL_DIR / "repo" / "metadata" / "root.json"

    UPDATE_DIR = INSTALL_DIR / "_update"
    METADATA_DIR = UPDATE_DIR / "metadata"
    TARGET_DIR = UPDATE_DIR / "targets"
    STAGE_DIR = UPDATE_DIR / "stage"
    BACKUP_DIR = UPDATE_DIR / "backup"
    PENDING_FLAG = UPDATE_DIR / "pending"
    VER_FILE = INSTALL_DIR / "VERSION.txt"
    
    # 动态判断更新器后缀
    _updater_name = "SanktecoUpdater.exe" if sys.platform == "win32" else "SanktecoUpdater"
    UPDATER_EXE = INSTALL_DIR / _updater_name
    MAIN_EXE_NAME = "Sankteco.exe" if sys.platform == "win32" else "Sankteco"


"""
====================
Web地址常量
====================
"""


class WebUrl:
    """网址类"""

    # 一言API接口
    HITOKOTO_API_URL = "https://v1.hitokoto.cn/"
    HITOKOTO_API_URL_WITH_FORMAT = "https://v1.hitokoto.cn/?c=i&encode=text"

    # 加入翻译计划( 语言 子页面)
    JOIN_TRANSLATION_LINK = ""

    # SECTL API Base URL
    SECTL_API_BASE = "https://appwrite.sectl.cn"
    PROJECT_REPO = "SECTL/Sankteco"

    # stk.sectl.cn 分发目录基础路径 (已做 URL 编码)
    SECTL_DIST_BASE = (
        "https://stk.sectl.cn/Sankteco/"
        "%E6%80%9D%E6%8B%93%E5%88%9B%E8%81%94%20Github%20"
        "%E9%95%9C%E5%83%8F%E6%BA%90"
    )


"""
====================
字符串常量
====================
"""


class BasicInfo:
    """应用基础信息字符串"""

    import platform

    APP_PKG_NAME = "sankteco"
    APP_VER = "0.1.0"

    # 系统平台名称
    OS_PLATFORM = platform.system()


class AppConfigString:
    """应用配置类 的字符串, 仅包含 app_config.py 相关字符串"""

    # 语言 类字符串
    LANGUAGE_GROUP = "Language"
    LANGUAGE_NAME = "Language"

    # 调试选项 类字符串
    DEBUG_GROUP = "Debug"
    DEBUG_LOG_FILE_RETENTION = "LogFileRetention"
    DEBUG_ERROR_LOG_FILE_RETENTION = "ErrorLogFileRetention"

    # 更新选项 类字符串
    UPDATE_GROUP = "Update"
    UPDATE_UPDATE_CHANNEL = "UpdateChannel"
    UPDATE_AUTO_UPDATE_MODE = "AutoUpdateMode"
    UPDATE_MIRROR_MODE = "MirrorMode"


class LogicFilesString:
    """逻辑文件的字符串"""

    # add_import_export_namelist.py
    AIENAMELIST_HEADER_EXIST = "Exist?"
    AIENAMELIST_HEADER_NO = "No."
    AIENAMELIST_HEADER_NAME = "Name"
    AIENAMELIST_HEADER_GENDER = "Gender"
    AIENAMELIST_HEADER_GROUP = "Group"
    AIENAMELIST_HEADER_TIP = "Tip"
    AIENAMELIST_HEADER = [
        AIENAMELIST_HEADER_EXIST,
        AIENAMELIST_HEADER_NO,
        AIENAMELIST_HEADER_NAME,
        AIENAMELIST_HEADER_GENDER,
        AIENAMELIST_HEADER_GROUP,
        AIENAMELIST_HEADER_TIP,
    ]

    # ui_str.py
    # gettext 键名
    LANG_DOMAIN = "messages"
    LANG_LOCALEDIR = "locales"

    # json 键名
    LANG_JSON_1 = "Language"
    LANG_JSON_2 = "Language"
