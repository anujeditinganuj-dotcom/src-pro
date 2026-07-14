import asyncio
import datetime
import sys
import os
from datetime import timezone, timedelta
from pyrogram import Client, filters, enums, __version__ as pyrogram_version
from pyrogram.types import Message, BotCommand
from pyrogram.errors import FloodWait, RPCError
from config import API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL, ADMINS
from database.db import db
from logger import LOGGER

try:
    from keep_alive import keep_alive
except ImportError:
    keep_alive = None

logger = LOGGER(__name__)
IST = timezone(timedelta(hours=5, minutes=30))
USER_CACHE = set()

E_CHECK  = '<emoji id=5206607081334906820>✔️</emoji>'
E_CROSS  = '<emoji id=5210952531676504517>❌</emoji>'
E_BOLT   = '<emoji id=5456140674028019486>⚡️</emoji>'
E_ROCKET = '<emoji id=5456140674028019486>🚀</emoji>'
E_GEAR   = '<emoji id=5341715473882955310>⚙️</emoji>'
E_USERS  = '<emoji id=5334544901428229844>👥</emoji>'
E_CLOCK  = '<emoji id=5386367538735104399>⌛</emoji>'
E_STOP   = '<emoji id=5260293700088511294>⛔️</emoji>'
E_STAR   = '<emoji id=5438496463044752972>⭐️</emoji>'
E_CROWN  = '<emoji id=5217822164362739968>👑</emoji>'
E_INFO   = '<emoji id=5334544901428229844>ℹ️</emoji>'

LOGO = r"""
  ██████╗  ██╗  ██╗  █████╗  ███╗   ██╗ ██████╗   █████╗  ██╗      
  ██╔══██╗ ██║  ██║ ██╔══██╗ ████╗  ██║ ██╔══██╗ ██╔══██╗ ██║      
  ██║  ██║ ███████║ ███████║ ██╔██╗ ██║ ██████╔╝ ███████║ ██║      
  ██║  ██║ ██╔══██║ ██╔══██║ ██║╚██╗██║ ██╔═══╝  ██╔══██║ ██║      
  ██████╔╝ ██║  ██║ ██║  ██║ ██║ ╚████║ ██║      ██║  ██║ ███████╗
    𝙱𝙾𝚃 𝚆𝙾𝚁𝙺𝙸𝙽𝙶 𝙿𝚁𝙾𝙿𝙴𝚁𝙻𝚈....
"""


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Rexbots_Login_Bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="Rexbots"),
            workers=10,
            sleep_threshold=15,
            max_concurrent_transmissions=5,
            ipv6=False,
            in_memory=False,
        )
        self._keep_alive_started = False

    async def start(self, **kwargs):
        print(LOGO)

        if keep_alive and not self._keep_alive_started:
            try:
                loop = asyncio.get_running_loop()
                try:
                    keep_alive(loop)
                except TypeError:
                    keep_alive()
                self._keep_alive_started = True
                logger.info("Keep-alive server started.")
            except Exception as e:
                logger.warning(f"Keep-alive failed: {e}")

        while True:
            try:
                await super().start(**kwargs)
                break
            except FloodWait as e:
                wait_time = int(e.value) + 10
                logger.warning(f"FLOOD_WAIT detected during login. Sleeping for {wait_time}s...")
                await asyncio.sleep(wait_time)
            except Exception as e:
                logger.error(f"Critical Startup Error: {e}")
                await asyncio.sleep(15)

        me = await self.get_me()

        try:
            user_count = await db.total_users_count()
            logger.info(f"MongoDB Connected: {user_count} users found.")
        except Exception as e:
            logger.error(f"DB stats failed: {e}")
            user_count = "Unknown"

        now = datetime.datetime.now(IST)
        startup_text = (
            f"<blockquote>{E_ROCKET} <b>Bot Successfully Started!</b>\n\n"
            f"{E_STAR} <b>Bot:</b> @{me.username}\n"
            f"{E_USERS} <b>Users:</b> <code>{user_count} / 200</code>\n"
            f"{E_CLOCK} <b>Time:</b> <code>{now.strftime('%I:%M %p')} IST</code>\n\n"
            f"{E_CROWN} <b>Developed by @anujedits76</b></blockquote>"
        )

        try:
            await self.send_message(LOG_CHANNEL, startup_text, parse_mode=enums.ParseMode.HTML)
            logger.info("Startup log sent.")
        except Exception as e:
            logger.error(f"Failed to send startup log: {e}")

        await self.set_bot_commands_list()

    async def stop(self, *args):
        try:
            await self.send_message(
                LOG_CHANNEL,
                f"<b>{E_STOP} Bot is going Offline.</b>",
                parse_mode=enums.ParseMode.HTML
            )
        except:
            pass
        await asyncio.shield(super().stop())
        logger.info("Bot stopped cleanly")

    async def set_bot_commands_list(self):
        commands = [
    BotCommand("start",         "🚀 Start the bot"),
    BotCommand("help",          "❓ Show help"),
    BotCommand("login",         "🔐 Login"),
    BotCommand("logout",        "🚪 Logout"),
    BotCommand("cancel",        "🚫 Cancel current action"),
    BotCommand("myplan",        "📋 Check your plan"),
    BotCommand("premium",       "⭐ Premium info"),
    BotCommand("broadcast",     "📢 Broadcast message (admin only)"),
    BotCommand("setchat",       "💬 Set target chat"),
    BotCommand("set_thumb",     "🖼️ Set thumbnail"),
    BotCommand("view_thumb",    "👁️ View thumbnail"),
    BotCommand("del_thumb",     "🗑️ Delete thumbnail"),
    BotCommand("set_caption",   "✏️ Set caption"),
    BotCommand("see_caption",   "📄 View caption"),
    BotCommand("del_caption",   "❌ Delete caption"),
    BotCommand("set_del_word",  "➕ Add delete word"),
    BotCommand("rem_del_word",  "➖ Remove delete word"),
    BotCommand("set_repl_word", "🔄 Add replace word"),
    BotCommand("rem_repl_word", "🔃 Remove replace word"),
    BotCommand("add_premium",   "👑 Add premium to user (admin only)"),
    BotCommand("remove_premium","💔 Remove premium from user (admin only)"),
    BotCommand("ban",           "🔨 Ban a user"),
    BotCommand("unban",         "✅ Unban a user"),
]
        await self.set_bot_commands(commands)


BotInstance = Bot()


@BotInstance.on_message(filters.private & filters.incoming, group=-1)
async def new_user_log(bot: Client, message: Message):
    user = message.from_user
    if not user or user.id in USER_CACHE:
        return

    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
        now = datetime.datetime.now(IST)
        log_text = (
            f"<blockquote>{E_USERS} <b>#NewUser</b>\n"
            f"{E_STAR} <b>User:</b> {user.mention}\n"
            f"{E_INFO} <b>ID:</b> <code>{user.id}</code>\n"
            f"{E_CLOCK} <b>Time:</b> {now.strftime('%I:%M %p')} IST</blockquote>"
        )
        try:
            await bot.send_message(LOG_CHANNEL, log_text, parse_mode=enums.ParseMode.HTML)
        except:
            pass

    USER_CACHE.add(user.id)


@BotInstance.on_message(filters.command("cmd") & filters.user(ADMINS))
async def update_commands(bot: Client, message: Message):
    try:
        await bot.set_bot_commands_list()
        await message.reply_text(
            f"<b>{E_CHECK} Commands menu updated!</b>",
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        await message.reply_text(
            f"<b>{E_CROSS} Error:</b> {e}",
            parse_mode=enums.ParseMode.HTML
        )


if __name__ == "__main__":
    BotInstance.run()
