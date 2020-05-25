import os

APP_NAME = os.environ.get("APP_NAME")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get('PORT', '8443'))
NAME = "SplitwizeBot"
WEBHOOK = False
## The following configuration is only needed if you setted WEBHOOK to True ##
WEBHOOK_OPTIONS = {
    'listen': '0.0.0.0',  # IP
    'port': PORT,
    'url_path': BOT_TOKEN,  # This is recommended for avoiding random people
    # making fake updates to your bot
}
WEBHOOK_URL = f'{APP_NAME}/{WEBHOOK_OPTIONS["url_path"]}'
