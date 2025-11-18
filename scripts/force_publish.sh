#!/usr/bin/env bash
set -euo pipefail

# 警告：此脚本会强制覆盖远端仓库（--force --mirror），会重写远端历史，
# 所有协作者的本地仓库将出现不兼容历史，需要重新 clone 或按指示重置。
# 使用前请务必备份并通知所有协作者。

WORK_DIR="ai-trading-bot-clean"
REPO_URL_ORIG="https://github.com/xuanoooooo/ai-trading-bot.git"

if [ ! -d "$WORK_DIR" ]; then
  echo "未找到工作目录 '$WORK_DIR'。请先运行 scripts/publish_clean.sh 并在该目录完成清理步骤。" >&2
  exit 1
fi

read -p "你确定要强制覆盖原仓库 $REPO_URL_ORIG 吗？这将不可逆。输入 YES 以继续：" CONFIRM
if [ "$CONFIRM" != "YES" ]; then
  echo "取消操作。要覆盖仓库必须输入 YES" && exit 1
fi

cd "$WORK_DIR"

echo "再次提示：建议先手动复查变更（至少运行：git log --stat, git show <commit> 若干）。" 
read -p "确认已复查并备份（输入 CONFIRMED 才继续）：" CONF2
if [ "$CONF2" != "CONFIRMED" ]; then
  echo "取消操作。输入 CONFIRMED 才会继续" && exit 1
fi

echo "添加远端并强制推送（--force --mirror）到 $REPO_URL_ORIG"
git remote remove origin_clean 2>/dev/null || true
git remote add origin_clean "$REPO_URL_ORIG"

echo "开始强推... 请确保你有权限并了解后果。"
git push --force --mirror origin_clean

echo "强推完成。请立即通知所有协作者：他们需要重新 clone 或运行官方 reset 指南。"
