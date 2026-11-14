"""仅开发机运行, 初始化 tufup 仓库。"""

from pathlib import Path
from tufup.repo import Repository


APP_NAME = "sankteco"
REPO_DIR = Path(__file__).resolve().parent.parent / "repo"
KEYS_DIR = Path.home() / ".tufup_keys"  # 私钥务必离线备份

repo = Repository(
    app_name=APP_NAME,
    repo_dir=REPO_DIR,
    keys_dir=KEYS_DIR,
)
repo.initialize()
repo.save_config()
print(f"[OK] 仓库初始化完成：{REPO_DIR}")
print(f"     私钥目录：{KEYS_DIR}（请务必离线备份！）")
