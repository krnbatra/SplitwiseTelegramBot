# SplitwiseTelegramBot

#### A telegram bot  for managing Splitwise application from within Telegram.


## 🤖 [SplitwizeBot](https://telegram.me/SplitwizeBot)


## What can this bot do?
The current version supports the following commands.
   1. **connect**: Connects your Splitwise account
   2. **list_expense**: List expenses from your Splitwise account
   3. **create_expense**: Creates new expense in your Splitwise account
   4. **settle_expense**: Settles expense in your Splitwise account
   
Use [/connect]() to connect to your Splitwise account.

## ✨ Demo
![](https://github.com/krnbatra/SplitwiseTelegramBot/blob/master/assets/demoSplitwise.gif)

## Getting started

### Setting up the local instance

Install the dependencies using:
```
   pip install -r requirements.txt
```

Set up the value of environment variables
```
   * BOT_TOKEN = Ask @BotFather for this token
   
   Register your app on Splitwise to get the value of next 2 tokens
   * CONSUMER_KEY
   * CONSUMER_SECRET
   
   * REDIS_URL = 127.0.0.1:6379
```
Make value of WEBHOOK = False in [this](https://github.com/krnbatra/SplitwiseTelegramBot/blob/master/configurations/settings.py) file.

Finally run 
```
   python main.py
```

## Author
   👤 Karan Deep Batra
   * LinkedIn: [@krnbatra](https://www.linkedin.com/in/krnbatra/)
   * Instagram: [@karandeepbatra](https://www.instagram.com/karandeepbatra/)

## 🤝 Contributing

Contributions, issues and feature requests are welcome!

Feel free to check [issues page](https://github.com/krnbatra/SplitwiseTelegramBot/issues). 


## Show your support

Give a ⭐️ if you liked this project!


<a href="https://www.producthunt.com/posts/splitwise-telegram-bot?utm_source=badge-featured&utm_medium=badge&utm_souce=badge-splitwise-telegram-bot" target="_blank"><img src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=204262&theme=light" alt="Splitwise Telegram Bot - Telegram Bot for managing your Splitwise account. | Product Hunt Embed" style="width: 250px; height: 54px;" width="250px" height="54px" /></a>

## License
This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/krnbatra/SplitwiseTelegramBot/blob/master/LICENSE.md) file for details
