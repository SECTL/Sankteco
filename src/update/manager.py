"""单步更新执行器与版本查询"""

from __future__ import annotations

import shutil
from typing import Callable, Optional

import requests
from loguru import logger
from packaging.version import InvalidVersion, Version
from tufup.client import Client

from app_const_var import AssetsPath, BasicInfo, WebUrl

# ==================== 工具函数 ====================


def get_platform_suffix() -> str:
    """获取当前系统的平台后缀"""

    if BasicInfo.OS_PLATFORM == "Windows":
        return "windows"
    elif BasicInfo.OS_PLATFORM == "Darwin":
        return "macos"
    elif BasicInfo.OS_PLATFORM == "Linux":
        return "linux"
    else:
        return ""


def fetch_latest_version(channel: str) -> Optional[str]:
    """
    从 SECTL API 获取指定渠道的最新纯净版本号\n
    channel: "release" 或 "prerelease",
    返回例如 "0.2.0", 失败返回 None
    """

    url = f"{WebUrl.SECTL_API_BASE}/api/software/latest-tag"
    params = {"repo": WebUrl.PROJECT_REPO, "channel": channel}

    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        if not data.get("success"):
            logger.error(f"API 返回失败: {data.get('message', '未知错误')}")
            return None

        latest_data = data.get("latest") or {}
        tag_name = latest_data.get("tag")
        if not tag_name:
            logger.warning(f"未找到 {channel} 渠道的版本号")
            return None

        # 清除前缀 'v' (例如 v0.2.0 -> 0.2.0)
        clean_version = tag_name.lstrip("v")

        try:
            Version(clean_version)
        except InvalidVersion:
            logger.error(f"API 返回的版本号不合法: {tag_name}")
            return None

        return clean_version

    except requests.RequestException as e:
        logger.error(f"请求 SECTL API 失败: {e}")
        return None


# ==================== VER.txt 读写 ====================


def read_current_version() -> str:
    """读取本地当前版本(带平台后缀), 不存在则用代码内置版本兜底"""

    ver_path = AssetsPath.VER_FILE
    if ver_path.exists():
        try:
            v = ver_path.read_text(encoding="utf-8").strip()
            if v:
                # 兼容处理：如果以前的历史文件里带有 -linux/-windows 后缀, 把它切掉
                return v.split("-")[0]
        except Exception as e:
            logger.warning(f"读取版本失败: {e}")

    # 兜底: 直接返回纯净的 APP_VER, 例如 "0.1.0"
    return BasicInfo.APP_VER


def write_current_version(version: str) -> None:
    """把版本号(带平台后缀)写入 VERSION.txt"""

    ver_path = AssetsPath.VER_FILE
    ver_path.write_text(version, encoding="utf-8")
    logger.debug(f"程序版本已更新为 {version}")


# ==================== tufup 执行器 ====================


class UpdateManager:
    """
    针对单次版本跨度的更新执行器,
    当前版本和目标版本均需携带平台后缀(如 0.1.0-windows)
    """

    def __init__(self, current_version: str, target_version: str, clean_tag: str):
        """
        :param current_version: 本地当前版本, 如 "0.1.0-windows"
        :param target_version: 目标版本, 如 "0.2.0-windows"
        :param clean_tag: API 拉取的纯净版本, 如 "0.2.0" (用于拼接下载目录)
        """

        self.current_version = current_version
        self.target_version = target_version
        self.clean_tag = clean_tag

    def _make_client(self, progress_hook: Optional[Callable] = None) -> Client:
        """构造 tufup 客户端"""
        
        for d in (AssetsPath.METADATA_DIR, AssetsPath.TARGET_DIR, AssetsPath.STAGE_DIR):
            d.mkdir(parents=True, exist_ok=True)

        root_dst = AssetsPath.METADATA_DIR / "root.json"
        if not root_dst.exists() and AssetsPath.BUNDLED_ROOT.exists():
            shutil.copy2(AssetsPath.BUNDLED_ROOT, root_dst)

        # 动态获取带平台后缀的 App Name
        suffix = get_platform_suffix()
        dynamic_app_name = f"{BasicInfo.APP_PKG_NAME}-{suffix}" if suffix else BasicInfo.APP_PKG_NAME

        # 处理本地测试和线上环境的 URL 差异
        if "127.0.0.1" in WebUrl.SECTL_DIST_BASE or "0.0.0.0" in WebUrl.SECTL_DIST_BASE:
            # 本地测试：直接指向根目录的 metadata 和 targets
            metadata_url = f"{WebUrl.SECTL_DIST_BASE}/metadata"
            target_url = f"{WebUrl.SECTL_DIST_BASE}/targets"
        else:
            # 线上环境：指向特定版本的 Release 目录
            base_release_url = f"{WebUrl.SECTL_DIST_BASE}/v{self.clean_tag}"
            metadata_url = f"{base_release_url}/metadata"
            target_url = base_release_url

        return Client(
            app_name=dynamic_app_name, # 使用带后缀的名字, 如 sankteco-linux
            app_install_dir=AssetsPath.INSTALL_DIR,
            current_version=self.current_version, # 纯净的 0.1.0
            metadata_dir=AssetsPath.METADATA_DIR,
            metadata_base_url=metadata_url,
            target_dir=AssetsPath.TARGET_DIR,
            target_base_url=target_url,
            extract_dir=AssetsPath.STAGE_DIR,
            refresh_required=False,
        )

    def check(self) -> Optional[str]:
        """检查 tufup 仓库里是否真的有目标的增量或全量包"""

        client = self._make_client()
        info = client.check_for_updates()
        if not info:
            return None
        return str(info.version)

    def apply(
        self,
        progress_hook: Optional[Callable[[int, int], None]] = None,
        install_callback: Optional[Callable] = None,
    ) -> None:
        """下载并应用更新"""

        client = self._make_client(progress_hook=progress_hook)

        client.download_and_apply_update(
            skip_confirmation=True,
            install=install_callback,
            progress_hook=progress_hook,
        )
