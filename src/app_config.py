"""
应用配置类,用于保存项目的所有可调整设置
引用时可作 AppConfig 
"""

from enum import Enum
from typing import Type

from qfluentwidgets import (
    QConfig,
    OptionsConfigItem,
    OptionsValidator,
    EnumSerializer,
    ConfigItem,
    ConfigValidator,
)

from app_const_var import AppConfigString


class IntValidator(ConfigValidator):
    """整数校验器,确保配置值为有效的整数"""

    def validate(self, value) -> bool:
        """验证值是否为有效的整数"""

        try:
            # 尝试转换为整数,如果失败则返回 False
            int(value)
            return True
        except (TypeError, ValueError):
            return False


class ValuesMixin:
    """返回Enum类成员value的基类"""

    @classmethod
    def values(cls: Type[Enum]) -> list:  # type: ignore[reportGeneralTypeIssues]
        return [q.value for q in cls.__members__.values()]


class AppEnums:
    """应用枚举类"""

    class LanguageEnum(ValuesMixin, Enum):
        """语言枚举类"""

        ZH_CN = "zh_CN"
        EO = "eo"


class AppConfig(QConfig):
    """应用配置类"""

    # 子页面:语言( 首选项 的子页面)配置类
    # 语言
    Language = OptionsConfigItem(
        AppConfigString.LANGUAGE_GROUP,
        AppConfigString.LANGUAGE_NAME,
        AppEnums.LanguageEnum.ZH_CN,
        OptionsValidator([AppEnums.LanguageEnum.ZH_CN, AppEnums.LanguageEnum.EO]),
        EnumSerializer(AppEnums.LanguageEnum),
        restart=True,
    )

    # 子页面:调试选项( 首选项 的子页面)配置类
    # 日志文件保留时长(天)
    LogFileRetention = ConfigItem("Debug", "LogFileRetention", 30, IntValidator())

    # 错误日志文件保留时长(天)
    ErrorLogFileRetention = ConfigItem(
        "Debug", "ErrorLogFileRetention", 60, IntValidator()
    )

# 创建全局唯一配置项实例
cfg = AppConfig()
