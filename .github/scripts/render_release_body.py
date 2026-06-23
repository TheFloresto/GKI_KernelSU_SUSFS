import json
import os
import sys
from pathlib import Path

# Словарь с метаданными вариантов KSU
KSU_METADATA = {
    "Next": {"name": "KernelSU-Next", "url": "https://github.com/KernelSU-Next/KernelSU-Next"},
    "KSU": {"name": "KernelSU (Official)", "url": "https://github.com/tiann/KernelSU"},
    "MKSU": {"name": "MKSU", "url": "https://github.com/5ec1cff/KernelSU"},
    "KowSU": {"name": "KowSU", "url": "https://github.com/KOWX712/KernelSU-Next"},
    "ReSukiSU": {"name": "ReSukiSU", "url": "https://github.com/ReSukiSU/ReSukiSU"},
    "WKSU": {"name": "Wild_KSU", "url": "https://github.com/WildKernels/Wild_KSU"}
}

def get_ksu_meta():
    variant = os.environ.get("KSU_VARIANT", "Next")
    return KSU_METADATA.get(variant, {"name": variant, "url": "#"})

PLACEHOLDERS = {
    "{{KSU_NAME}}": lambda: get_ksu_meta()["name"],
    "{{KSU_URL}}": lambda: get_ksu_meta()["url"],
    "{{KSU_VERSION}}": lambda: os.environ.get("KSU_VERSION", "unknown"),
    "{{KSU_GIT_TAG}}": lambda: os.environ.get("KSU_GIT_TAG", "no-tag"),
    "{{KSUN_BRANCH}}": lambda: os.environ.get("KSUN_BRANCH", os.environ.get("KSU_BRANCH", "dev")),
    "{{KSUN_COMMIT}}": lambda: os.environ.get("KSU_COMMIT", os.environ.get("KSUN_COMMIT", "unknown")),
    "{{KSU_MANAGER}}": lambda: os.environ.get("KSU_MANAGER", "Placeholder"),
}

def render_markdown(template_path: Path):
    text = template_path.read_text()

    commits_path = template_path.parent / "commits.json"
    commits = json.loads(commits_path.read_text()) if commits_path.exists() else {}

    for placeholder, getter in PLACEHOLDERS.items():
        text = text.replace(placeholder, getter())

    susfs_branches = []
    for branch, commit in commits.get("susfs", {}).items():
        susfs_branches.append(f"**{branch}**\n`{commit}`")

    if "{{SUSFS_BRANCHS}}" in text:
        text = text.replace("{{SUSFS_BRANCHS}}", "\n".join(susfs_branches))
    if "{{SUSFS_BRANCHES}}" in text:
        text = text.replace("{{SUSFS_BRANCHES}}", "\n".join(susfs_branches))

    print(text, end="")


config_path = Path(sys.argv[1])
if config_path.suffix.lower() == ".md":
    render_markdown(config_path)
    sys.exit(0)

# Backward-compatible JSON renderer for older release configs.

def emit(text=""):
    print(text)

def emit_list(items):
    if isinstance(items, list):
        for item in items:
            emit(f"- {item}")

def emit_description(value):
    if isinstance(value, list):
        for line in value:
            emit(line)
    elif value:
        emit(str(value))


data = json.loads(config_path.read_text())

commits_path = config_path.parent / "commits.json"
commits = json.loads(commits_path.read_text()) if commits_path.exists() else {}

emit("**IMPORTANT DISCLAIMER**")
if "release" in data and "disclaimer" in data["release"]:
    for line in data["release"]["disclaimer"]:
        emit(line)

kernelsu = data.get("kernelsu", {})
meta = get_ksu_meta()
emit()
emit(f"## {meta['name']}")
emit(f"- Version: {os.environ.get('KSU_VERSION', kernelsu.get('version', 'unknown'))}")
emit(f"- Tag: {os.environ.get('KSU_GIT_TAG', kernelsu.get('tag', 'no-tag'))}")
emit(f"- Branch: {os.environ.get('KSUN_BRANCH', os.environ.get('KSU_BRANCH', kernelsu.get('branch', 'dev')))}")
emit(f"- Commit: {os.environ.get('KSU_COMMIT', os.environ.get('KSUN_COMMIT', kernelsu.get('commit', 'unknown')))}")
if meta['url']:
    emit(f"- URL: {meta['url']}")
if kernelsu.get("manager") or os.environ.get("KSU_MANAGER"):
    emit(f"- Manager: {os.environ.get('KSU_MANAGER', kernelsu.get('manager', ''))}")

skip_keys = {"release", "kernelsu"}
for key in data.keys():
    if key in skip_keys:
        continue

    section = data[key]
    emit()
    emit(f"## {section.get('name', key)}")

    if section.get("description"):
        emit_description(section["description"])

    if section.get("version"):
        emit(f"- Version: {section['version']}")
    if section.get("tag"):
        emit(f"- Tag: {section['tag']}")
    if section.get("branch"):
        emit(f"- Branch: {section['branch']}")

    if key == "susfs" and "susfs" in commits:
        emit("- Branches:")
        for branch, commit in commits["susfs"].items():
            emit(f"**{branch}**")
            emit(f"`{commit}`")

    if section.get("items"):
        emit_list(section["items"])

    if section.get("url"):
        emit(f"- URL: {section['url']}")
