
---

### How to Switch Terminal Output to English
By default, terminal messages are in Chinese. To switch to English:
1. Open the `.env` file in project root directory.
2. Find or add the line:
   # BOT_LANG=EN
3. Remove the '#' to uncomment:
   BOT_LANG=EN
4. Save and restart the bot.

Or launch directly:

    export BOT_LANG=EN; python3 src/deepseekBNB.py

To switch back to Chinese, restore '#' or use BOT_LANG=CN.
