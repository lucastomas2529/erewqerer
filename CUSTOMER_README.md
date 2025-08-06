# 🚀 Tomas Bot - Customer Guide

## 📋 Quick Start Guide

### **Step 1: Install Python**
1. Download Python 3.8+ from [python.org](https://python.org)
2. Install with "Add to PATH" option checked
3. Restart your computer

### **Step 2: Run the Bot**
1. **Double-click** `START_BOT.bat`
2. Wait for the setup to complete
3. The bot will start automatically in **safe testing mode**

## 🎯 What the Bot Does

The Tomas Bot is a professional cryptocurrency trading bot that:

✅ **Monitors Telegram Groups** - Listens to trading signals from multiple groups
✅ **Executes Trades Automatically** - Places orders based on signals
✅ **Manages Risk** - Uses stop-loss and take-profit orders
✅ **Scales Positions** - Increases position size when profitable
✅ **Sends Notifications** - Reports all activities via Telegram

## 📁 File Structure

```
📦 Tomas Bot Package
├── 🚀 START_BOT.bat              # Start bot in testing mode
├── ⚙️ SETUP_LIVE_TRADING.bat      # Configure live trading
├── 💰 START_BOT_LIVE.bat         # Start bot in live trading mode
├── 🛑 EMERGENCY_STOP.bat         # Emergency stop all trading
├── 📖 CUSTOMER_README.md         # This guide
└── 📁 Bot Files                  # Technical files (don't modify)
```

## 🎮 How to Use

### **Testing Mode (Safe)**
```bash
Double-click: START_BOT.bat
```
- ✅ Safe testing with fake money
- ✅ No real trades executed
- ✅ Perfect for learning and testing

### **Live Trading Mode (Real Money)**
```bash
1. Double-click: SETUP_LIVE_TRADING.bat
2. Enter your API credentials
3. Double-click: START_BOT_LIVE.bat
```
- ⚠️ Executes real trades with real money
- ⚠️ Only use after thorough testing
- ⚠️ Start with small amounts

### **Emergency Stop**
```bash
Double-click: EMERGENCY_STOP.bat
```
- 🛑 Immediately stops all trading
- 🛑 Closes all positions
- 🛑 Use if something goes wrong

## 📊 Bot Features

### **Signal Processing**
- Monitors up to 20 Telegram groups
- Parses multiple signal formats
- Filters spam and invalid signals

### **Trading Strategy**
- **Dual Entry**: Places 2 limit orders for better execution
- **Risk Management**: 2% risk per trade
- **Position Scaling**: Increases size when profitable
- **Stop-Loss**: Automatic loss protection
- **Take-Profit**: Multiple profit targets

### **Advanced Features**
- **Break-even Protection**: Moves stop-loss to break-even
- **Trailing Stops**: Follows price movement
- **Re-entry Logic**: Re-enters after stop-loss
- **Hedging**: Protects against adverse moves
- **Timeout Protection**: Closes trades after 4 hours

## 🔧 Configuration

### **API Credentials Needed**
1. **Bitget Account**: [bitget.com](https://bitget.com)
   - API Key, Secret, and Passphrase
2. **Telegram Bot**: [@BotFather](https://t.me/BotFather)
   - Bot Token, API ID, and API Hash

### **Risk Settings**
- **Default Leverage**: 10x (configurable)
- **Risk per Trade**: 2% of account
- **Initial Margin**: 20 USDT per trade
- **Maximum Position**: 1000 USDT

## 📱 Telegram Commands

Once the bot is running, you can control it via Telegram:

```
/status          - Check bot status
/help            - Show all commands
/buy SYMBOL      - Manual buy order
/sell SYMBOL     - Manual sell order
/close SYMBOL    - Close position
/modify SL/TP    - Modify stop-loss/take-profit
/override        - Emergency overrides
```

## ⚠️ Important Safety Notes

### **Before Live Trading**
1. ✅ Test thoroughly in testing mode
2. ✅ Start with small amounts
3. ✅ Monitor the bot closely
4. ✅ Keep emergency stop ready
5. ✅ Understand the risks involved

### **Risk Warnings**
- ⚠️ Cryptocurrency trading is highly risky
- ⚠️ You can lose all your invested money
- ⚠️ Past performance doesn't guarantee future results
- ⚠️ Only invest what you can afford to lose

## 🆘 Troubleshooting

### **Common Issues**

**Bot won't start:**
- Check if Python is installed
- Run `START_BOT.bat` as administrator
- Check internet connection

**Telegram not working:**
- Verify bot token is correct
- Check API credentials
- Ensure bot has proper permissions

**Trades not executing:**
- Check API credentials
- Verify account has sufficient balance
- Check if trading is enabled on exchange

### **Getting Help**
1. Check the logs in the console
2. Look for error messages
3. Contact support with specific error details

## 📈 Performance Monitoring

The bot provides detailed reports:

### **Daily Reports** (22:00 UTC)
- Total trades executed
- Win rate and profit/loss
- Performance by symbol
- Risk metrics

### **Weekly Reports** (Sunday 23:00 UTC)
- 7-day performance summary
- Group performance analysis
- Risk assessment
- Recommendations

## 🔄 Updates and Maintenance

### **Keeping the Bot Updated**
- Check for updates regularly
- Backup your configuration files
- Test updates in testing mode first

### **Regular Maintenance**
- Monitor bot performance
- Review trading logs
- Adjust risk parameters as needed
- Keep API credentials secure

## 📞 Support

For technical support:
- Check this README first
- Review error logs
- Contact with specific error details
- Include screenshots if possible

---

## 🎉 You're Ready!

The Tomas Bot is now ready to help you trade cryptocurrencies automatically. Remember:

1. **Start with testing mode** to learn how it works
2. **Configure live trading** only when ready
3. **Monitor closely** during initial live trading
4. **Use emergency stop** if needed
5. **Keep learning** and adjusting as needed

**Happy Trading! 🚀** 