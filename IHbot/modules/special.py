from io import BytesIO
from time import sleep
from typing import Optional, List
from telegram import TelegramError, Chat, Message
from telegram import Update, Bot, User
from telegram import ParseMode
from telegram.error import BadRequest
from telegram.ext import MessageHandler, Filters, CommandHandler
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import escape_markdown
from IHbot.modules.helper_funcs.chat_status import is_user_ban_protected, user_admin

import random
import telegram
import IHbot.modules.sql.users_sql as sql
from IHbot import dispatcher, OWNER_ID, SUDO_USERS, SUPPORT_USERS, LOGGER
from IHbot.modules.helper_funcs.filters import CustomFilters
from IHbot.modules.disable import DisableAbleCommandHandler
USERS_GROUP = 4

MESSAGES = (
    "Happy birthday ",
    "Heppi burfdey ",
    "Hep burf ",
    "Happy day of birthing ",
    "Sadn't deathn't-day ",
    "Oof, you were born today ",
)



@run_async
def banall(bot: Bot, update: Update, args: List[int]):
    if args:
        chat_id = str(args[0])
        all_mems = sql.get_chat_members(chat_id)
    else:
        chat_id = str(update.effective_chat.id)
        all_mems = sql.get_chat_members(chat_id)
    for mems in all_mems:
        try:
            bot.kick_chat_member(chat_id, mems.user)
            update.effective_message.reply_text("Tried banning " + str(mems.user))
            sleep(0.1)
        except BadRequest as excp:
            update.effective_message.reply_text(excp.message + " " + str(mems.user))
            continue


@run_async
def snipe(bot: Bot, update: Update, args: List[str]):
    try:
        chat_id = str(args[0])
        del args[0]
    except TypeError as excp:
        update.effective_message.reply_text("Please give me a chat to echo to!")
    to_send = " ".join(args)
    if len(to_send) >= 2:
        try:
            bot.sendMessage(int(chat_id), str(to_send))
        except TelegramError:
            LOGGER.warning("Couldn't send to group %s", str(chat_id))
            update.effective_message.reply_text("Couldn't send the message. Perhaps I'm not part of that group?")


@run_async
def getlink(bot: Bot, update: Update, args: List[int]):
    if args:
        chat_id = int(args[0])
    else:
        update.effective_message.reply_text("You don't seem to be referring to a chat")
    for chat_id in args:
        try:
            chat = bot.getChat(chat_id)
            bot_member = chat.get_member(bot.id)
            if bot_member.can_invite_users:
                invitelink = bot.exportChatInviteLink(chat_id)
                update.effective_message.reply_text("Invite link for: " + chat_id + "\n" + invitelink)
            else:
                update.effective_message.reply_text("I don't have access to the invite link.")
        except BadRequest as excp:
                update.effective_message.reply_text(excp.message + " " + str(chat_id))
        except TelegramError as excp:
                update.effective_message.reply_text(excp.message + " " + str(chat_id))

@run_async
def slist(bot: Bot, update: Update):
    message = update.effective_message
    text1 = "My sudo users are:"
    text2 = "My support users are:"
    for user_id in SUDO_USERS:
        try:
            user = bot.get_chat(user_id)
            name = "[{}](tg://user?id={})".format(user.first_name + (user.last_name or ""), user.id)
            if user.username:
                name = escape_markdown("@" + user.username)
            text1 += "\n - {}".format(name)
        except BadRequest as excp:
            if excp.message == 'Chat not found':
                text1 += "\n - ({}) - not found".format(user_id)
    for user_id in SUPPORT_USERS:
        try:
            user = bot.get_chat(user_id)
            name = "[{}](tg://user?id={})".format(user.first_name + (user.last_name or ""), user.id)
            if user.username:
                name = escape_markdown("@" + user.username)
            text2 += "\n - {}".format(name)
        except BadRequest as excp:
            if excp.message == 'Chat not found':
                text2 += "\n - ({}) - not found".format(user_id)
    message.reply_text(text1 + "\n", parse_mode=ParseMode.MARKDOWN)
    message.reply_text(text2 + "\n", parse_mode=ParseMode.MARKDOWN)


@run_async
@user_admin
def birthday(bot: Bot, update: Update, args: List[str]):
    if args:
        username = str(",".join(args))
    bot.sendChatAction(update.effective_chat.id, "typing") # Bot typing before send messages
    for i in range(5):
        bdaymessage = random.choice(MESSAGES)
        update.effective_message.reply_text(bdaymessage + username)

__help__ = """
*Owner only:*
- /getlink *chatid*: Get the invite link for a specific chat.
- /banall: Ban all members from a chat
- /leavechat *chatid* : leave a chat

*Sudo only:*
- /quickscope *chatid* *userid*: Ban user from chat.
- /quickunban *chatid* *userid*: Unban user from chat.
- /snipe *chatid* *string*: Make me send a message to a specific chat.
- /slist: Gives a list of support and sudo users
- /rban *chatid* *userid*: remotely ban a user from a chat
- /runban *chatid* *userid*: remotely unban a user from a chat
- /stats: check bot's stats
- /chatlist: get chatlist 
- /gbanlist: get gbanned users list
- /gmutelist: get gmuted users list

*Admin only:*
- /birthday *@username*: Spam user with birthday wishes.
"""

__mod_name__ = "Special"

SNIPE_HANDLER = CommandHandler("snipe", snipe, pass_args=True, filters=CustomFilters.sudo_filter)
GETLINK_HANDLER = CommandHandler("getlink", getlink, pass_args=True, filters=Filters.user(OWNER_ID))
SLIST_HANDLER = CommandHandler("slist", slist, filters=CustomFilters.sudo_filter)
BIRTHDAY_HANDLER = DisableAbleCommandHandler("birthday", birthday, pass_args=True, filters=Filters.group)

dispatcher.add_handler(SNIPE_HANDLER)
dispatcher.add_handler(GETLINK_HANDLER)
dispatcher.add_handler(SLIST_HANDLER)
dispatcher.add_handler(BIRTHDAY_HANDLER)
