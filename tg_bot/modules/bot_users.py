import html
from io import BytesIO
from telegram import Message, Update, Bot, User, Chat, ParseMode
from telegram.error import BadRequest, TelegramError
from telegram.ext import run_async, CommandHandler, MessageHandler, Filters
from telegram.utils.helpers import mention_html
from tg_bot import dispatcher, OWNER_ID, SUDO_USERS

@run_async
def listsudo(bot: Bot, update: Update):
    message = update.effective_message
    reply_msg = "**SUDO USERS:**"
    for i in SUDO_USERS:
        reply_msg += "\n" + i

    message.reply_text(reply_msg)
