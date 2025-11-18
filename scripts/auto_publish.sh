#!/usr/bin/env bash
set -euo pipefail

# 自动化强制发布脚本
# 用途：将清理后的本地仓库强制推送到原远端仓库
# 需要：有效的 GitHub 凭据和仓库推送权限

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_NAME="ai-trading-bot"
REPO_URL="https://github.com/xuanoooooo/ai-trading-bot.git"

cd "$REPO_ROOT"

echo "========================================="
echo "🚀 AI Trading Bot - 自动强制发布脚本"
echo "========================================="
echo ""
echo "仓库地址：$REPO_URL"
echo "本地目录：$REPO_ROOT"
echo ""

# 检查 git 状态
if [ -n "$(git status --porcelain)" ]; then
  echo "❌ 错误：当前工作目录有未提交的改动，请先 commit 或 stash"
  git status
  exit 1
fi

echo "✅ 工作目录干净"
echo ""

# 显示最近提交
echo "最近提交："
git log --oneline -5
echo ""

# 再次确认
read -p "⚠️  这将强制推送本地历史到远端，覆盖原仓库。确认继续吗？(yes/no): " CONFIRM_1
if [ "$CONFIRM_1" != "yes" ]; then
  echo "取消操作"
  exit 0
fi

read -p "最后确认：你已通知所有协作者，且准备好处理后续影响吗？(yes/no): " CONFIRM_2
if [ "$CONFIRM_2" != "yes" ]; then
  echo "取消操作"
  exit 0
fi

echo ""
echo "开始推送..."
echo ""

# 尝试推送
if ! git push --force origin main 2>&1; then
  echo ""
  echo "❌ 推送失败。可能原因："
  echo "  1. 网络连接问题"
  echo "  2. 未登录 GitHub（需要设置 git 凭据或 SSH key）"
  echo "  3. 无权限推送到该仓库"
  echo ""
  echo "解决方法："
  echo "  - 验证网络连接：ping github.com"
  echo "  - 验证 git 凭据：git config user.name 和 user.email"
  echo "  - 尝试用 SSH：git remote set-url origin git@github.com:xuanoooooo/ai-trading-bot.git"
  echo ""
  exit 1
fi

echo ""
echo "✅ 推送成功！"
echo ""
echo "现在需要通知所有协作者。模板已保存在 FINAL_PUSH_INSTRUCTIONS.md"
echo ""
echo "后续建议："
echo "  1. 通知团队成员重新 clone 或重置本地仓库"
echo "  2. 检查相关服务中的密钥，必要时更换"
echo "  3. 在 GitHub 发布 Release 或说明"
echo ""
echo "在 GitHub 验证：https://github.com/xuanoooooo/ai-trading-bot"
echo ""
echo "完成！🎉"

