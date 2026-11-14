"""打包新版本, 自动生成补丁链与 TUF 元数据。"""

import argparse
from pathlib import Path

from packaging.version import Version, InvalidVersion
from tufup.repo import Repository

REPO_DIR = Path(__file__).resolve().parent.parent / "repo"
KEYS_DIR = Path.home() / ".tufup_keys"


def add_version(
    bundle_dir: Path, version: str, app_name: str, required: bool = False, skip_patch: bool = False
):
    """
    bundle_dir: PyInstaller onedir 输出的目录（含 Sankteco.exe + _internal/）
    version:    符合 PEP440 的版本字符串, 例如 "1.2.0"
    required:   是否标记为必需版本（客户端必须先装到这一版）
    skip_patch: True 则跳过生成补丁（例如差异过大时）
    """

    try:
        Version(version)
    except InvalidVersion:
        raise SystemExit(f"版本号不符合 PEP440: {version}")

    if not bundle_dir.is_dir():
        raise SystemExit("bundle_dir目录不存在")
    
    repo = Repository(
        app_name=app_name,
        repo_dir=REPO_DIR,
        keys_dir=KEYS_DIR,
    )
    repo.initialize()
    
    if repo.roles is None:
        raise SystemExit("initialize不成功")

    repo.add_bundle(
        new_bundle_dir=bundle_dir,
        new_version=version,
        skip_patch=skip_patch,
        required=required,
    )
    repo.publish_changes(private_key_dirs=[KEYS_DIR])
    print(f"[OK] v{version} 已注册；required={required}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("bundle_dir", type=Path, help="onedir 打包输出目录")
    p.add_argument("version", help="版本号, 如 1.2.0")
    p.add_argument("--app-name", default="sankteco", help="应用名（如 sankteco-linux）")
    p.add_argument("--required", action="store_true")
    p.add_argument("--skip-patch", action="store_true")
    args = p.parse_args()
    
    add_version(args.bundle_dir, args.version, args.app_name, args.required, args.skip_patch)
