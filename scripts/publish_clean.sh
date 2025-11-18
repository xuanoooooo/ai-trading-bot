#!/usr/bin/env bash
set -euo pipefail

# 脚本说明：
# 1) 在当前工作目录创建一个镜像备份（--mirror）
# 2) 使用 git-filter-repo 和 replace.txt 重写历史（需提前安装 git-filter-repo）
# 3) 将清理后的仓库推送到目标仓库（默认不会强推原仓库，需手动确认）

REPO_URL_ORIG="https://github.com/xuanoooooo/ai-trading-bot.git"
MIRROR_DIR="ai-trading-bot-mirror.git"
WORK_DIR="ai-trading-bot-clean"
REPLACE_FILE="replace.txt"

if [ ! -f "$REPLACE_FILE" ]; then
  echo "缺少 $REPLACE_FILE，请确保它存在于仓库根目录。" >&2
  exit 1
fi

echo "1) 创建镜像备份 (--mirror)..."
git clone --mirror "$REPO_URL_ORIG" "$MIRROR_DIR"

echo "2) 克隆工作副本用于清理..."
git clone "$REPO_URL_ORIG" "$WORK_DIR"
cd "$WORK_DIR"

echo "3) 备份当前工作分支..."
git branch -m main main-before-scrub || true

echo "4) 使用 git-filter-repo 应用替换文本（请先安装 git-filter-repo: pip install git-filter-repo）"
git filter-repo --replace-text ../$REPLACE_FILE || {
  echo "git-filter-repo 执行失败，请检查安装或 replace.txt 格式" >&2
  exit 1
}

echo "5) 本地检查并清理敏感文件（如果需要，请在此添加额外命令）"
echo "  - 建议手动复查变更：git log --stat | less"

cat <<'EOF'
下一步：
  - 若要将清理后的仓库推到新仓库（推荐）:
      1) 在 GitHub 创建新仓库，例如 your-username/ai-trading-bot-scrubbed
      2) git remote add scrubbed https://github.com/your-username/ai-trading-bot-scrubbed.git
      3) git push scrubbed --mirror

  - 若要覆盖原仓库（非常危险，需确认）:
      git remote add origin_clean "${REPO_URL_ORIG}" || true
      git push --force --mirror origin_clean

请在推送前务必确认已备份并通知所有合作者。
EOF

echo "脚本执行完毕。请手动复查并按需要推送到目标仓库。"
