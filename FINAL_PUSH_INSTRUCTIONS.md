# 最终发布到原仓库（强制推送）

## 前置确认

**强制推送前请确保已完成以下操作：**

1. ✅ 已运行 `git-filter-repo --replace-text replace.txt`
2. ✅ 已验证历史替换成功（已在本地 CLI 中验证）
3. ✅ 已创建备份分支 `main-before-cleaning`
4. ✅ 仓库中已没有真实敏感信息（无 AWS key、GitHub token、private key 等）

## 推送命令（复制粘贴执行）

进入仓库根目录，运行以下命令：

```bash
cd /root/ziyong/duobizhong

# 强制推送到远端 main 分支（覆盖原仓库）
git push --force origin main

# 或者用 --mirror 推送所有分支和标签（推荐，更完整）
git push --force --mirror origin

# 验证推送成功
git log --oneline --graph --all origin/main | head -20
```

## 推送后的建议操作

### 1. 通知协作者 📢

所有有权限访问该仓库的协作者需要重新 clone 或重置本地仓库：

**给协作者的通知模板：**
```
亲爱的团队成员，

我们已清理并重写了 https://github.com/xuanoooooo/ai-trading-bot.git 的 Git 历史，以移除可能意外包含的敏感信息（配置示例等）。

请按以下步骤更新你的本地仓库：

**选项 A（推荐）：完全重新 clone**
git clone https://github.com/xuanoooooo/ai-trading-bot.git
cd ai-trading-bot

**选项 B：强制同步现有本地仓库**
cd 你的本地仓库
git fetch origin
git checkout main
git reset --hard origin/main
git branch -D main-before-cleaning  # 删除备份分支（如果本地有）

如有任何问题，请告诉我们。谢谢理解！
```

### 2. 验证远端已更新 ✅

在 GitHub 网页上查看仓库，确认：
- 最新提交是否符合预期
- 提交历史中是否仍有"敏感配置相关"的内容（通过 GitHub 搜索验证，如搜索 "OPENAI_API_KEY" 应不再出现示例值）

### 3. 撤销/更换任何可能泄露的密钥 🔑

**若在历史中发现真实泄露的密钥（Binance API key、OpenAI key 等），立即：**

- **Binance**: 登录账户 → API Management → 删除泄露的 key → 创建新 key
- **OpenAI**: 登录平台 → API keys → 删除旧 key → 生成新 key
- **AWS/其他服务**: 类似流程

**然后在本项目的 `.env` 中更新为新密钥。**

### 4. 发布 Release 或 Notice（可选）

在 GitHub 仓库中发布一条 Release 或 Issue，说明此次清理：

```markdown
## 🔐 Repository Cleanup - Git History Rewrite

**Changes:**
- Removed/redacted example configurations and sensitive documentation references
- Cleaned git history to prevent any accidental credential exposure
- Added `.env.example` for secure configuration template
- Added `replace.txt` for future history cleaning automation

**For Team Members:**
- Please re-clone or reset your local repository (see instructions above)
- Update your `.env` file from `.env.example` template
- Verify you're using the latest API credentials

**Timeline:**
- Cleaned on: 2025-11-19
- Effective from commit: [HEAD hash]
```

## 恢复步骤（如遇紧急情况）

若推送后发现问题需要回滚，可使用之前创建的备份分支恢复：

```bash
# 查看备份分支是否在本地仍存在
git branch -a | grep main-before-cleaning

# 如果本地备份分支仍存在，可强制推送回去（非常危险，仅在紧急情况）
git push --force origin main-before-cleaning:main
```

**注意：** 备份分支只在执行 `git-filter-repo` 的本地环境中保留。推送后，备份分支不会自动上传到 GitHub（除非手动推送）。如需保留备份在远端，执行：

```bash
git push origin main-before-cleaning
```

## 最终检查清单

- [ ] 已在本地验证历史替换（`git log` 已查阅）
- [ ] 已验证敏感字符串已替换（`git show` 查阅关键提交）
- [ ] 已创建备份分支 `main-before-cleaning`
- [ ] 已准备好通知协作者的信息
- [ ] 已准备好在相关服务中吊销密钥的计划
- [ ] 已确认有网络连接和 GitHub 权限
- [ ] 已准备好 Release notes 或说明

---

**当以上检查清单全部完成后，运行推送命令即可！** 🚀

