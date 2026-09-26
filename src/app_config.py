"""
应用配置类,用于保存项目的所有可调整设置
引用时可作 AppConfig 
"""

from enum import Enum
from typing import Type

from qfluentwidgets import QConfig, OptionsConfigItem, OptionsValidator, EnumSerializer
from app_const_var import AppConfigString


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
