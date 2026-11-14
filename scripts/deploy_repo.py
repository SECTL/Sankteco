"""分离元数据与 targets, 分别推送到 Pages / Releases。"""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT / "repo"
OUT = ROOT / "deploy"

if OUT.exists():
    shutil.rmtree(OUT)


def deploy():
    meta_out = OUT / "metadata"
    target_out = OUT / "targets"
    meta_out.mkdir(parents=True, exist_ok=True)
    target_out.mkdir(parents=True, exist_ok=True)

    for f in (REPO / "metadata").glob("*.json"):
        shutil.copy2(f, meta_out / f.name)
    for f in (REPO / "targets").iterdir():
        if f.name.endswith((".tar.gz", ".patch")):
            shutil.copy2(f, target_out / f.name)

    print("元数据 -> deploy/metadata/  （推送到 gh-pages 分支）")
    print("targets -> deploy/targets/   （作为 Release 附件上传）")


if __name__ == "__main__":
    deploy()
