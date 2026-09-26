# src/plugin/loader.py
"""
插件加载器
负责发现、加载、启用/禁用、卸载本地插件,以及从远程索引安装插件
"""

import logging
import sys
import shutil
import zipfile
import tempfile
import json
import urllib3
import hashlib
from typing import Dict, Callable, Optional, Any, List
from pathlib import Path
from stevedore import ExtensionManager
from PySide2.QtCore import QStandardPaths

try:
    import requests
except ImportError:
    requests = None
    logging.getLogger("PluginLoader").warning("requests 库未安装,远程索引功能不可用")

logger = logging.getLogger("PluginLoader")
# 禁用 SSL 警告(因使用 verify=False)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PluginLoader:
    """
    插件加载器
    支持两种来源：
    1. Stevedore(生产环境,通过 pip 安装的插件)
    2. 本地 plugins/ 目录(开发环境,直接拷贝文件夹)
    """

    # 远程插件索引 URL(GitHub raw)
    REMOTE_INDEX_URL = "https://raw.githubusercontent.com/SECTL/Sankteco-Plugins-Index/main/plugins.json"

    def __init__(self, namespace: str = "sankteco.plugin"):
        """
        初始化加载器
        :param namespace: Stevedore 命名空间
        """
        self.namespace = namespace
        # 存储所有插件信息：{ plugin_id: { register, meta, module, enabled, is_local, _plugin_dir } }
        self._plugins: Dict[str, Dict[str, Any]] = {}
        # 本地插件目录(项目根目录下的 plugins/)
        self._local_plugins_dir = Path(__file__).parent.parent.parent / "plugins"
        # 用户数据目录(用于插件配置存储)
        self._data_dir = self._get_data_dir()

    def _get_data_dir(self) -> Path:
        """获取用户数据目录(跨平台)"""
        data_dir = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)  # type: ignore
        plugin_data_dir = Path(data_dir) / "plugins" / "data"
        plugin_data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"插件数据目录: {plugin_data_dir}")
        return plugin_data_dir

    def _get_plugins_dir(self) -> Path:
        """获取本地插件目录"""
        return self._local_plugins_dir

    def get_plugin_data_dir(self, plugin_id: str) -> Path:
        """获取指定插件的私有数据目录"""
        plugin_data_dir = self._data_dir / plugin_id
        plugin_data_dir.mkdir(parents=True, exist_ok=True)
        return plugin_data_dir

    # ========== 加载入口 ==========

    def load_all_plugins(self) -> int:
        """
        加载所有插件
        优先使用 Stevedore,如果无插件则回退到本地扫描
        :return: 成功加载的插件数量(启用且可用的插件)
        """
        loaded_count = self._load_from_stevedore()
        if loaded_count > 0:
            return loaded_count

        logger.info("Stevedore 未发现插件,回退到扫描本地 plugins/ 目录...")
        return self._load_from_local_plugins()

    # ========== Stevedore 加载 ==========

    def _load_from_stevedore(self) -> int:
        """使用 Stevedore 加载通过 pip 安装的插件"""
        logger.info(f"尝试从 Stevedore 加载命名空间 '{self.namespace}'...")
        try:
            mgr = ExtensionManager(
                namespace=self.namespace,
                invoke_on_load=False,
            )
        except Exception as e:
            logger.error(f"加载 ExtensionManager 失败: {e}")
            return 0

        loaded_count = 0
        for ext in mgr.extensions:
            plugin_id = ext.name
            register_func = ext.plugin
            if not callable(register_func):
                logger.warning(f"插件 {plugin_id} 的入口点不是可调用对象")
                continue
            meta = self._extract_metadata(ext.module)
            self._plugins[plugin_id] = {
                "register": register_func,
                "meta": meta,
                "module": ext.module,
                "enabled": True,
                "is_local": False,
                "_plugin_dir": None,  # Stevedore 插件没有本地目录
            }
            loaded_count += 1
            logger.info(
                f"[Stevedore] 加载插件: {plugin_id} (v{meta.get('version', 'unknown')})"
            )
        return loaded_count

    def _extract_metadata(self, module) -> Dict[str, Any]:
        """从插件模块中提取 __plugin_meta__ 字典"""
        default_meta = {
            "name": module.__name__,
            "version": "1.0.0",
            "description": "",
            "author": "",
            "icon": "APPLICATION",
            "generation": 0,
        }
        if hasattr(module, "__plugin_meta__"):
            meta = getattr(module, "__plugin_meta__")
            if isinstance(meta, dict):
                default_meta.update(meta)
        return default_meta

    # ========== 查询接口 ==========

    def get_register_func(self, plugin_id: str) -> Optional[Callable]:
        """获取已加载插件的 register 函数"""
        plugin_info = self._plugins.get(plugin_id)
        if plugin_info:
            return plugin_info.get("register")
        return None

    def get_plugin_meta(self, plugin_id: str) -> Dict[str, Any]:
        """获取插件元数据"""
        plugin_info = self._plugins.get(plugin_id)
        if plugin_info:
            return plugin_info.get("meta", {})
        return {}

    def get_all_plugin_ids(self) -> List[str]:
        """获取所有已记录插件的 ID 列表(包括禁用的)"""
        return list(self._plugins.keys())

    def get_all_plugin_info(self) -> List[Dict[str, Any]]:
        """获取所有插件的简要信息(用于 UI 展示)"""
        result = []
        for plugin_id, info in self._plugins.items():
            result.append(
                {
                    "id": plugin_id,
                    "meta": info.get("meta", {}),
                    "has_register": info.get("register") is not None,
                }
            )
        return result

    def is_plugin_enabled(self, plugin_id: str) -> bool:
        """
        检查插件是否启用
        优先使用 _plugins 中的 enabled 标志,如果不存在则检查文件夹状态
        """
        plugin_info = self._plugins.get(plugin_id)
        if plugin_info is not None:
            return plugin_info.get("enabled", False)
        # 如果记录不存在(例如插件未被扫描到),检查文件夹
        plugin_dir = self._get_plugin_dir_by_id(plugin_id)
        if plugin_dir:
            return not plugin_dir.name.endswith(".disabled")
        return False

    # ========== 热重载 ==========

    def reload_all_plugins(self) -> int:
        """全量重载所有插件(清空缓存重新扫描)"""
        logger.info("热重载所有插件...")
        self._plugins.clear()
        return self.load_all_plugins()

    def reload_plugin(self, plugin_id: str) -> bool:
        """单个插件重载(暂不支持,提示使用全量重载)"""
        logger.warning("单个插件热重载暂不支持,请使用 reload_all_plugins()")
        return False

    # ========== 卸载与启用/禁用 ==========

    def unload_plugin(self, plugin_id: str) -> bool:
        """
        从内存中卸载插件(不删除文件)
        保留 _plugins 记录,但清空 register 和 module,标记为禁用
        """
        if plugin_id not in self._plugins:
            logger.warning(f"插件 {plugin_id} 未加载,无法卸载")
            return False

        plugin_info = self._plugins[plugin_id]
        module = plugin_info.get("module")

        # 从 sys.modules 中移除模块及其子模块
        if module and hasattr(module, "__name__"):
            module_name = module.__name__
            if module_name in sys.modules:
                to_remove = [
                    name for name in sys.modules if name.startswith(module_name)
                ]
                for name in to_remove:
                    del sys.modules[name]
                logger.debug(f"已从 sys.modules 移除: {to_remove}")

        # 清空运行时状态,保留元数据
        plugin_info["register"] = None
        plugin_info["module"] = None
        plugin_info["enabled"] = False
        logger.info(f"插件 {plugin_id} 已从内存中卸载(保留记录)")
        return True

    def uninstall_plugin(self, plugin_id: str) -> bool:
        """
        彻底卸载插件：从内存移除 + 删除文件夹
        如果是 Stevedore 插件,仅移除记录
        """
        # 先从内存卸载
        self.unload_plugin(plugin_id)

        # 查找本地插件目录(包括 .disabled)
        plugin_dir = self._get_plugin_dir_by_id(plugin_id)
        if plugin_dir and plugin_dir.exists():
            try:
                shutil.rmtree(plugin_dir)
                logger.info(f"已删除插件: {plugin_dir}")
                if plugin_id in self._plugins:
                    del self._plugins[plugin_id]
                return True
            except Exception as e:
                logger.error(f"删除失败: {e}")
                return False

        # 如果是 Stevedore 插件(无本地文件夹),仅移除记录
        if plugin_id in self._plugins:
            del self._plugins[plugin_id]
            logger.info(f"已移除 Stevedore 插件记录: {plugin_id}")
            return True

        logger.warning(f"找不到插件 {plugin_id} 的文件")
        return False

    def _get_metadata_path(self, plugin_dir: Path) -> Optional[Path]:
        """返回插件目录中的元数据文件路径,优先 plugin.json,其次 manifest.json"""
        plugin_json = plugin_dir / "plugin.json"
        if plugin_json.exists():
            return plugin_json
        manifest_json = plugin_dir / "manifest.json"
        if manifest_json.exists():
            return manifest_json
        return None

    def _get_plugin_dir_by_id(self, plugin_id: str) -> Optional[Path]:
        """
        根据 plugin_id 查找对应的本地插件目录
        包括正常目录和 .disabled 目录
        """
        plugins_root = self._local_plugins_dir
        if not plugins_root.exists():
            return None

        for item in plugins_root.iterdir():
            if not item.is_dir():
                continue
            # 去掉 .disabled 后缀比较
            name = item.name
            if name.endswith(".disabled"):
                name = name[:-9]  # 移除 ".disabled"
            # 通过 plugin.json 或 manifest.json 中的 id 验证
            meta_path = self._get_metadata_path(item)
            if meta_path:
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    if meta.get("id") == plugin_id:
                        print(f"[DEBUG] 找到插件目录: {item}")  # 调试输出
                        return item
                except:
                    pass
        print(f"[DEBUG] 未找到插件目录: {plugin_id}")  # 调试输出
        return None

    def enable_plugin(self, plugin_id: str, context) -> Optional[Callable]:
        """
        启用插件：
        1. 如果存在 .disabled 文件夹,重命名为正常名称
        2. 重新加载插件模块
        :return: register 函数,失败返回 None
        """
        plugins_root = self._local_plugins_dir
        if not plugins_root.exists():
            return None

        # 查找 .disabled 文件夹
        disabled_dir = None
        for item in plugins_root.iterdir():
            if not item.is_dir():
                continue
            if item.name.endswith(".disabled"):
                meta_path = self._get_metadata_path(item)
                if meta_path:
                    try:
                        with open(meta_path, "r", encoding="utf-8") as f:
                            meta = json.load(f)
                        if meta.get("id") == plugin_id:
                            disabled_dir = item
                            break
                    except:
                        pass

        if disabled_dir:
            new_name = disabled_dir.name[:-9]  # 移除 ".disabled"
            new_path = disabled_dir.parent / new_name
            disabled_dir.rename(new_path)
            logger.info(f"已启用插件: {plugin_id} ({new_path})")

        # 重新加载模块
        return self._load_single_plugin(plugin_id)

    def disable_plugin(self, plugin_id: str) -> bool:
        """
        禁用插件：
        1. 从内存中卸载模块
        2. 将插件文件夹重命名为 .disabled
        3. 更新 _plugins 记录状态
        """
        # 先卸载(清空模块,保留记录)
        self.unload_plugin(plugin_id)

        # 查找插件目录
        plugin_dir = self._get_plugin_dir_by_id(plugin_id)
        if not plugin_dir:
            logger.warning(f"找不到插件目录: {plugin_id}")
            return False

        # 重命名为 .disabled
        new_name = plugin_dir.name + ".disabled"
        new_path = plugin_dir.parent / new_name
        plugin_dir.rename(new_path)
        logger.info(f"已禁用插件: {plugin_id} ({new_path})")

        # 更新 _plugins 中的记录
        if plugin_id in self._plugins:
            self._plugins[plugin_id]["enabled"] = False
            self._plugins[plugin_id]["register"] = None
            self._plugins[plugin_id]["module"] = None
            self._plugins[plugin_id]["_plugin_dir"] = str(new_path.absolute())
        else:
            # 如果记录不存在(例如首次启动时未扫描到),创建一条禁用记录
            meta_path = self._get_metadata_path(new_path)
            if meta_path:
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    meta_data = {
                        "name": meta.get("name", plugin_id),
                        "version": meta.get("version", "1.0.0"),
                        "description": meta.get("description", ""),
                        "author": meta.get("author", "未知"),
                        "icon": meta.get("icon", "APPLICATION"),
                        "generation": meta.get("generation", 0),
                    }
                    self._plugins[plugin_id] = {
                        "register": None,
                        "meta": meta_data,
                        "module": None,
                        "enabled": False,
                        "is_local": True,
                        "_plugin_dir": str(new_path.absolute()),
                    }
                except:
                    pass
        return True

    # ========== 本地目录扫描 ==========

    def _load_from_local_plugins(self) -> int:
        """
        扫描本地 plugins/ 目录
        1. 加载非 .disabled 的插件(enabled=True)
        2. 记录 .disabled 的插件(enabled=False,不加载模块)
        """
        plugins_dir = self._local_plugins_dir
        if not plugins_dir.exists():
            return 0

        count_loaded = 0
        # 清理旧的本地插件记录(保留 Stevedore 的)
        for pid in list(self._plugins.keys()):
            if self._plugins[pid].get("is_local", False):
                del self._plugins[pid]

        for plugin_dir in plugins_dir.iterdir():
            if not plugin_dir.is_dir():
                continue
            if plugin_dir.name.startswith("_") or plugin_dir.name.startswith("."):
                continue

            is_disabled = plugin_dir.name.endswith(".disabled")
            meta_path = self._get_metadata_path(plugin_dir)
            if not meta_path:
                continue

            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
            except Exception as e:
                logger.warning(f"解析 {meta_path} 失败: {e}")
                continue

            plugin_id = meta.get("id")
            if not plugin_id:
                continue

            # 如果是 .disabled 插件,只记录元数据,不加载模块
            if is_disabled:
                meta_data = {
                    "name": meta.get("name", plugin_id),
                    "version": meta.get("version", "1.0.0"),
                    "description": meta.get("description", ""),
                    "author": meta.get("author", "未知"),
                    "icon": meta.get("icon", "APPLICATION"),
                    "generation": meta.get("generation", 0),
                }
                self._plugins[plugin_id] = {
                    "register": None,
                    "meta": meta_data,
                    "module": None,
                    "enabled": False,
                    "is_local": True,
                    "_plugin_dir": str(plugin_dir.absolute()),
                }
                logger.debug(f"已记录禁用的插件: {plugin_id}")
                continue

            # 正常加载
            entry = meta.get("entry", "main.py")
            main_path = plugin_dir / entry
            if not main_path.exists():
                logger.warning(f"入口文件不存在: {main_path}")
                continue

            import importlib.util

            module_name = f"local_plugin_{plugin_id.replace('.', '_')}"
            if module_name in sys.modules:
                del sys.modules[module_name]

            try:
                spec = importlib.util.spec_from_file_location(module_name, main_path)
                if not spec or not spec.loader:
                    continue
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            except Exception as e:
                logger.error(f"加载 {main_path} 失败: {e}")
                continue

            meta_data = getattr(module, "__plugin_meta__", {})
            register_func = getattr(module, "register", None)

            if not callable(register_func):
                logger.warning(f"插件 {plugin_id} 缺少 register 函数")
                continue

            if "name" not in meta_data:
                meta_data["name"] = meta.get("name", plugin_id)
            if "icon" not in meta_data:
                meta_data["icon"] = meta.get("icon", "APPLICATION")
            if "generation" not in meta_data:
                meta_data["generation"] = meta.get("generation", 0)

            self._plugins[plugin_id] = {
                "register": register_func,
                "meta": meta_data,
                "module": module,
                "enabled": True,
                "is_local": True,
                "_plugin_dir": str(plugin_dir.absolute()),
            }
            count_loaded += 1
            logger.info(
                f"[本地] 加载插件: {plugin_id} (v{meta_data.get('version', 'unknown')})"
            )

        return count_loaded

    def _load_single_plugin(self, plugin_id: str) -> Optional[Callable]:
        """
        加载单个插件(用于启用时重新加载)
        先检查 _plugins 中是否已有记录,若已有且已启用则直接返回
        """
        # 如果已经加载且启用,直接返回
        if plugin_id in self._plugins:
            plugin_info = self._plugins[plugin_id]
            if plugin_info.get("enabled") and plugin_info.get("register"):
                return plugin_info["register"]

        # 查找插件目录(可能已重命名,但不会是 .disabled)
        plugin_dir = self._get_plugin_dir_by_id(plugin_id)
        if not plugin_dir or not plugin_dir.exists():
            logger.error(f"找不到插件目录: {plugin_id}")
            return None

        if plugin_dir.name.endswith(".disabled"):
            logger.error(f"插件 {plugin_id} 已被禁用")
            return None

        meta_path = self._get_metadata_path(plugin_dir)
        if not meta_path:
            logger.error(f"插件 {plugin_id} 缺少 plugin.json 或 manifest.json")
            return None

        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
        except Exception as e:
            logger.error(f"读取 plugin.json 失败: {e}")
            return None

        entry = meta.get("entry", "main.py")
        main_path = plugin_dir / entry
        if not main_path.exists():
            logger.error(f"入口文件不存在: {main_path}")
            return None

        import importlib.util

        module_name = f"local_plugin_{plugin_id.replace('.', '_')}"
        if module_name in sys.modules:
            del sys.modules[module_name]

        try:
            spec = importlib.util.spec_from_file_location(module_name, main_path)
            if not spec or not spec.loader:
                return None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            logger.error(f"加载模块失败: {e}")
            return None

        register_func = getattr(module, "register", None)
        if not callable(register_func):
            logger.error(f"插件 {plugin_id} 缺少 register 函数")
            return None

        meta_data = getattr(module, "__plugin_meta__", {})
        if "name" not in meta_data:
            meta_data["name"] = meta.get("name", plugin_id)
        if "icon" not in meta_data:
            meta_data["icon"] = meta.get("icon", "APPLICATION")
        if "generation" not in meta_data:
            meta_data["generation"] = meta.get("generation", 0)

        # 更新 _plugins
        if plugin_id in self._plugins:
            self._plugins[plugin_id]["register"] = register_func
            self._plugins[plugin_id]["meta"] = meta_data
            self._plugins[plugin_id]["module"] = module
            self._plugins[plugin_id]["enabled"] = True
        else:
            self._plugins[plugin_id] = {
                "register": register_func,
                "meta": meta_data,
                "module": module,
                "enabled": True,
                "is_local": True,
                "_plugin_dir": str(plugin_dir.absolute()),
            }

        logger.info(f"插件 {plugin_id} 已重新加载")
        return register_func

    # ========== 远程索引与安装 ==========

    def fetch_remote_index(self) -> List[Dict]:
        """从远程索引拉取插件列表"""
        if requests is None:
            logger.error("requests 库未安装,无法拉取远程索引")
            return []
        try:
            response = requests.get(self.REMOTE_INDEX_URL, timeout=10, verify=False)
            response.raise_for_status()
            data = response.json()
            return data.get("plugins", [])
        except Exception as e:
            logger.error(f"拉取远程索引失败: {e}")
            return []

    def get_plugin_update_status(self, plugin_id: str) -> Optional[str]:
        """检查插件是否有更新,返回 'update_available' 或 'newer_installed'"""
        local_meta = self.get_plugin_meta(plugin_id)
        remote_plugins = self.fetch_remote_index()
        for remote in remote_plugins:
            if remote.get("id") == plugin_id:
                local_gen = local_meta.get("generation", 0)
                remote_gen = remote.get("generation", 0)
                if remote_gen > local_gen:
                    return "update_available"
                elif remote_gen < local_gen:
                    return "newer_installed"
        return None

    def install_plugin_from_zip(self, zip_path: Path) -> bool:
        """
        从 ZIP 文件安装插件
        1. 解压到临时目录
        2. 查找 manifest.json
        3. 复制到本地 plugins/ 目录
        """
        try:
            temp_dir = Path(tempfile.mkdtemp())
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            # 查找 manifest.json
            manifest_path = None
            for item in temp_dir.rglob("manifest.json"):
                manifest_path = item
                break

            if not manifest_path:
                logger.error("ZIP 包缺少 manifest.json")
                shutil.rmtree(temp_dir)
                return False

            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            plugin_id = manifest.get("id")
            if not plugin_id:
                logger.error("manifest.json 缺少 id 字段")
                shutil.rmtree(temp_dir)
                return False

            target_dir = self._local_plugins_dir / plugin_id
            if target_dir.exists():
                backup_dir = self._local_plugins_dir / f"{plugin_id}.backup"
                if backup_dir.exists():
                    shutil.rmtree(backup_dir)
                target_dir.rename(backup_dir)
                logger.info(f"已备份旧插件: {backup_dir}")

            # manifest.json 所在目录即为插件根目录
            plugin_root = manifest_path.parent
            shutil.copytree(plugin_root, target_dir)
            shutil.rmtree(temp_dir)

            logger.info(f"插件 {plugin_id} 安装成功")
            return True
        except Exception as e:
            logger.error(f"安装插件失败: {e}")
            if temp_dir and temp_dir.exists():
                shutil.rmtree(temp_dir)
            return False

    def download_plugin(self, plugin_info: Dict) -> Optional[Path]:
        """
        下载插件 ZIP 包到临时文件,带进度报告和 SHA256 校验
        """
        download_url = plugin_info.get("download_url")
        expected_sha256 = plugin_info.get("sha256")  # 可选,但强烈建议提供

        if not download_url:
            logger.error("插件缺少 download_url")
            return None

        try:
            # 流式下载
            response = requests.get(download_url, timeout=30, verify=False, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0

            # 使用 NamedTemporaryFile 保存
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
                temp_zip = Path(tmp_file.name)
                sha256_hash = hashlib.sha256()

                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        tmp_file.write(chunk)
                        sha256_hash.update(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            # 发射进度信号(通过 plugin_signals)
                            from .signals import plugin_signals

                            plugin_signals.install_progress.emit(progress)

                tmp_file.flush()

            # 校验 SHA256
            if expected_sha256:
                actual_sha256 = sha256_hash.hexdigest()
                if actual_sha256.lower() != expected_sha256.lower():
                    logger.error(
                        f"SHA256 校验失败: 预期 {expected_sha256}, 实际 {actual_sha256}"
                    )
                    temp_zip.unlink()
                    return None
                logger.info(f"SHA256 校验通过: {actual_sha256}")
            else:
                logger.warning("插件未提供 SHA256,跳过校验")

            logger.info(f"插件下载成功: {temp_zip}")
            return temp_zip

        except Exception as e:
            logger.error(f"下载插件失败: {e}")
            if "temp_zip" in locals() and temp_zip.exists():
                temp_zip.unlink()
            return None

    def install_remote_plugin(self, plugin_info: Dict) -> bool:
        """从远程插件信息安装(下载 + 解压 + 校验)"""
        from .signals import plugin_signals

        # 重置进度
        plugin_signals.install_progress.emit(0)

        # 1. 下载(带进度)
        zip_path = self.download_plugin(plugin_info)
        if not zip_path:
            plugin_signals.install_progress.emit(-1)  # -1 表示失败
            return False

        # 2. 安装
        success = self.install_plugin_from_zip(zip_path)

        # 3. 清理临时文件
        if zip_path.exists():
            zip_path.unlink()

        if success:
            logger.info(f"插件 {plugin_info.get('id')} 安装成功")
            plugin_signals.install_progress.emit(100)
        else:
            logger.error(f"插件 {plugin_info.get('id')} 安装失败")
            plugin_signals.install_progress.emit(-1)

        return success
