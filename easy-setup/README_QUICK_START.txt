━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 AI Trading Bot - 5-Minute Quick Start Guide
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ IMPORTANT: Please read this guide carefully before starting!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 1: Get API Keys (Most Important!)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Get DeepSeek AI Key:
   ① Visit: https://platform.deepseek.com/
   ② Register and login
   ③ Click "API Keys" to create a new key
   ④ Copy the key (format: sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)
   ⑤ 💰 Recommended: Deposit $10-20 for extended usage

2. Get Binance API Key:
   ① Visit: https://www.binance.com (US users: binance.us)
   ② Login → Profile → API Management
   ③ Create new API key
   ④ Copy API Key and Secret Key
   ⑤ ⚠️ Important Permissions:
      - ✅ Enable "Futures Trading" permission
      - ✅ Enable "Read" permission
      - ⚠️ Disable "Withdrawal" permission (for security)
   ⑥ 🛡️ Recommended: Set IP whitelist

3. 🛡️ Security Recommendations:
   - Strongly recommend using Binance sub-accounts
   - Use one sub-account per coin for risk isolation
   - Don't use main account directly

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 2: Configure API Keys
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Find the ".env" file in the extracted folder
   
2. Open .env with a text editor (Notepad/TextEdit)

3. Fill in your API keys:

   DEEPSEEK_API_KEY=sk-your_deepseek_key_here
   BINANCE_API_KEY=your_binance_api_key
   BINANCE_SECRET=your_binance_secret_key

4. Save the file (Ctrl+S / Cmd+S)

⚠️ Notes:
   - Don't remove the equals sign (=)
   - Don't add quotes or spaces
   - Each key should be on a separate line

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 3: Start the Program
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Windows Users:
  1. Double-click "Windows系统一键安装.bat" in scripts folder (first time only)
     → Wait for dependencies installation (1-3 minutes)
  
  2. Double-click "Windows系统一键启动.bat"
     → Program starts, you'll see AI analysis output!

Linux/Mac Users:
  1. Open terminal, navigate to program directory
     cd /path/to/ai-trading-bot
  
  2. Run installation (first time only):
     chmod +x scripts/*.sh
     bash scripts/Linux系统一键安装.sh
  
  3. Run startup:
     bash scripts/Linux系统一键启动.sh
  
  4. Run in background (optional):
     nohup bash scripts/Linux系统一键启动.sh > trading.log 2>&1 &
  
  5. Check background process:
     ps aux | grep deepseekBNB
  
  6. Stop background process:
     pkill -f deepseekBNB

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 4: Verify Running
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Program running successfully when you see:
  ✅ "BNB Auto Trading Bot Started Successfully"
  ✅ "Current Account Balance" information
  ✅ "DeepSeek API Call Success" every 10 minutes
  ✅ AI decision analysis (LONG/SHORT/HOLD)

Common Errors:
  ❌ "Invalid API Key" → Check keys in .env file
  ❌ "Network Connection Failed" → Check network access to Binance
  ❌ "Permission Denied" → Enable futures trading in Binance API settings
  ❌ "ModuleNotFoundError" → Re-run "一键安装.bat"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ Important Reminders
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 📍 Position Mode:
   - Must use "One-Way Position Mode"
   - Binance APP: Futures → Settings → Position Mode → One-Way

2. 🌐 Network Requirements:
   - US and China IPs cannot directly access Binance API
   - Please resolve network issues on your own

3. 💰 Fund Management:
   - Recommend testing with small amounts first
   - Use sub-accounts for risk isolation
   - Program automatically reserves 20% as buffer

4. 📊 Monitoring:
   - Keep program window open to monitor status
   - Regularly check account balance and positions
   - Log file: bnb_trader.log

5. ❌ Stop Program:
   - Windows: Close window or press Ctrl+C
   - Linux/Mac: Press Ctrl+C

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 Get Help
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GitHub Project: https://github.com/xuanoooooo/ai-trading-bot
Issue Reports: Submit GitHub Issue

⚠️ Risk Warning:
Cryptocurrency trading involves risks. AI decisions don't guarantee profit.
Please use cautiously based on your risk tolerance. Start with small amounts.

Happy Trading! 🚀

