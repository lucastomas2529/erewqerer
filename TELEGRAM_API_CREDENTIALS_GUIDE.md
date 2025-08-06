# 🎯 **TELEGRAM API CREDENTIALS SETUP GUIDE**

## 📋 **What You Need for the Trading Bot**

To operate this trading bot, you need **3 types of Telegram credentials**:

1. **🔑 Telegram Bot Token** (from @BotFather)
2. **🆔 Telegram API ID** (from https://my.telegram.org/apps)
3. **🔐 Telegram API Hash** (from https://my.telegram.org/apps)

---

## 🚀 **STEP 1: Get Telegram Bot Token**

### **Method 1: Using @BotFather (Recommended)**

1. **Open Telegram** and search for `@BotFather`
2. **Start a chat** with BotFather
3. **Send the command**: `/newbot`
4. **Follow the prompts**:
   - Enter a name for your bot (e.g., "My Trading Bot")
   - Enter a username ending in 'bot' (e.g., "mytradingbot123_bot")
5. **Copy the token** that looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### **Method 2: Using Existing Bot**

If you already have a bot:
1. **Message @BotFather** with `/mybots`
2. **Select your bot**
3. **Click "API Token"** to view/copy the token

---

## 🆔 **STEP 2: Get Telegram API ID & Hash**

### **Step-by-Step Process:**

1. **Go to**: https://my.telegram.org/apps
2. **Log in** with your phone number
3. **Fill out the form**:
   - **App title**: "Trading Bot" (or any name)
   - **Short name**: "tradingbot" (lowercase, no spaces)
   - **Platform**: "Desktop"
   - **Description**: "Automated trading bot for cryptocurrency signals"
4. **Click "Create application"**
5. **Copy both values**:
   - **API ID**: A number like `12345678`
   - **API Hash**: A string like `abcdef1234567890abcdef1234567890`

### **⚠️ Important Notes:**
- **Keep these secret** - don't share them publicly
- **One app per phone number** - you can only create one app per Telegram account
- **Valid forever** - these credentials don't expire

---

## 🔧 **STEP 3: Get Your Telegram User ID**

### **Method 1: Using @userinfobot**

1. **Search for** `@userinfobot` in Telegram
2. **Start a chat** with it
3. **Send any message** (like "hello")
4. **Copy your User ID** from the response

### **Method 2: Using @RawDataBot**

1. **Search for** `@RawDataBot` in Telegram
2. **Start a chat** with it
3. **Send any message**
4. **Look for** `"id": 1234567890` in the response

### **Method 3: Using Your Own Bot**

1. **Send a message** to your bot
2. **Check the bot's logs** or use a webhook to see your user ID

---

## ⚙️ **STEP 4: Configure Your Bot**

### **Update Environment Variables**

Create or edit your `.env` file:

```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
TELEGRAM_ADMIN_ID=1234567890
```

### **Update config/settings.py**

Or update the configuration file directly:

```python
class TelegramConfig:
    TELEGRAM_BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
    TELEGRAM_API_ID = 12345678
    TELEGRAM_API_HASH = "abcdef1234567890abcdef1234567890"
    ADMIN_ID = 1234567890
```

---

## 🧪 **STEP 5: Test Your Setup**

### **Run the Test Script**

```bash
python test_telegram_fix.py
```

This will:
- ✅ Test your API credentials
- ✅ Verify bot token works
- ✅ Check Telegram connection
- ✅ Validate user ID

### **Expected Output:**
```
✅ Telegram API credentials are valid
✅ Bot token is working
✅ User ID is correct
✅ Ready to start the bot!
```

---

## 🔍 **TROUBLESHOOTING**

### **❌ "Invalid API ID" Error**
- **Solution**: Double-check your API ID from https://my.telegram.org/apps
- **Note**: API ID is a number, not a string

### **❌ "Invalid API Hash" Error**
- **Solution**: Copy the exact API Hash from https://my.telegram.org/apps
- **Note**: API Hash is case-sensitive

### **❌ "Bot Token Invalid" Error**
- **Solution**: 
  1. Check your bot token with @BotFather (`/mybots`)
  2. Make sure you copied the entire token
  3. Verify the bot is not deleted

### **❌ "Phone Number Not Registered" Error**
- **Solution**: 
  1. Make sure you're logged into the correct Telegram account
  2. Use the same phone number for both Telegram and API creation

### **❌ "Flood Wait" Error**
- **Solution**: 
  1. Wait 24 hours before trying again
  2. Don't make too many requests too quickly
  3. Use the session files to avoid re-authentication

---

## 🛡️ **SECURITY BEST PRACTICES**

### **✅ Do's:**
- Keep your API credentials private
- Use environment variables for sensitive data
- Regularly rotate your bot token if needed
- Monitor your bot's activity

### **❌ Don'ts:**
- Never share your API credentials publicly
- Don't commit credentials to version control
- Don't use the same bot for multiple projects
- Don't ignore security warnings

---

## 📱 **ADDITIONAL TELEGRAM SETUP**

### **Bot Permissions**
Your bot needs these permissions:
- ✅ **Read Messages** (to monitor signal groups)
- ✅ **Send Messages** (for notifications)
- ✅ **Edit Messages** (for status updates)

### **Group Access**
To monitor private groups:
1. **Join the groups** with your personal account
2. **Add your bot** to the groups (if required)
3. **Get the group ID** using @RawDataBot or similar

---

## 🎯 **QUICK REFERENCE**

### **Required Credentials:**
```
Bot Token: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
API ID: 12345678
API Hash: abcdef1234567890abcdef1234567890
User ID: 1234567890
```

### **Where to Get Them:**
- **Bot Token**: @BotFather on Telegram
- **API ID & Hash**: https://my.telegram.org/apps
- **User ID**: @userinfobot or @RawDataBot

### **Configuration Files:**
- **Environment**: `.env` file
- **Settings**: `config/settings.py`

---

## ✅ **VERIFICATION CHECKLIST**

- [ ] Bot token obtained from @BotFather
- [ ] API ID obtained from https://my.telegram.org/apps
- [ ] API Hash obtained from https://my.telegram.org/apps
- [ ] User ID obtained from @userinfobot
- [ ] Credentials added to `.env` file
- [ ] Test script runs successfully
- [ ] Bot responds to commands
- [ ] Can connect to Telegram groups

**Once all items are checked, your Telegram setup is complete! 🚀** 