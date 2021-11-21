from asyncio.queues import QueueEmpty

from pyrogram import Client
from pyrogram.types import Message
from callsmusic import callsmusic
from cache.admins import admins
from pyrogram import filters

from config import BOT_NAME as BN
from helpers.filters import command, other_filters
from helpers.decorators import errors, authorized_users_only


@Client.on_message(command(["pause", "dayandır"]) & other_filters)
@errors
@authorized_users_only
async def pause(_, message: Message):
    if (
            message.chat.id not in callsmusic.pytgcalls.active_calls
    ) or (
            callsmusic.pytgcalls.active_calls[message.chat.id] == 'Dayandırıldı'
    ):
        await message.reply_text("❗ Heçbir şey oxumur!")
    else:
        callsmusic.pytgcalls.pause_stream(message.chat.id)
        await message.reply_text("▶️ **Musiqi dayandırıldı!**\n\n• Musiqi istifadesine davam elemek üçün **komanda » resume**") 


@Client.on_message(command(["resume", "davam"]) & other_filters)
@errors
@authorized_users_only
async def resume(_, message: Message):
    if (
            message.chat.id not in callsmusic.pytgcalls.active_calls
    ) or (
            callsmusic.pytgcalls.active_calls[message.chat.id] == 'Oynanıyor'
    ):
        await message.reply_text("❗ Heçbir şey dayandırılmadı!")
    else:
        callsmusic.pytgcalls.resume_stream(message.chat.id)
        await message.reply_text("⏸ **Musiqi davam edir!**\n\n• İstifadeni dayandırmaq üçün **komanda » pause**")


@Client.on_message(command(["end", "son"]) & other_filters)
@errors
@authorized_users_only
async def stop(_, message: Message):
    if message.chat.id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("❗ Heçbir şey oxumur!")
    else:
        try:
            callsmusic.queues.clear(message.chat.id)
        except QueueEmpty:
            pass

        callsmusic.pytgcalls.leave_group_call(message.chat.id)
        await message.reply_text("✅ **Musiqi dayandırıldı!**\n\n• **Userbot'un sesli sohbet bağlantısı kesildi**")


@Client.on_message(command(["skip", "keç"]) & other_filters)
@errors
@authorized_users_only
async def skip(_, message: Message):
    if message.chat.id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("❗ Keçilecek musiqi yoxdur!")
    else:
        callsmusic.queues.task_done(message.chat.id)

        if callsmusic.queues.is_empty(message.chat.id):
            callsmusic.pytgcalls.leave_group_call(message.chat.id)
        else:
            callsmusic.pytgcalls.change_stream(
                message.chat.id,
                callsmusic.queues.get(message.chat.id)["file"]
            )

        await message.reply_text("⏭️ **__Mahnı bir sonraki növbeye alındı__**")


# Admin Vermek üçün (ver) Admin almaq üçün (al) komandasını elave etdim.
# Çox gözel işleyir. @DBMBOSSdu Terefinden düzeldilmişdir. 
@Client.on_message(command("ver") & other_filters)
@authorized_users_only
async def authenticate(client, message):
    global admins
    if not message.reply_to_message:
        await message.reply("User'e Yetki Vermek üçün yanıtla!")
        return
    if message.reply_to_message.from_user.id not in admins[message.chat.id]:
        new_admins = admins[message.chat.id]
        new_admins.append(message.reply_to_message.from_user.id)
        admins[message.chat.id] = new_admins
        await message.reply("user admindir.")
    else:
        await message.reply("✔ User onsuzda admindir!")


@Client.on_message(command("al") & other_filters)
@authorized_users_only
async def deautenticate(client, message):
    global admins
    if not message.reply_to_message:
        await message.reply("✘ useri adminlikden çıxartmaq üçün yanıt verin!")
        return
    if message.reply_to_message.from_user.id in admins[message.chat.id]:
        new_admins = admins[message.chat.id]
        new_admins.remove(message.reply_to_message.from_user.id)
        admins[message.chat.id] = new_admins
        await message.reply("user admin deyil")
    else:
        await message.reply("✔ artıq bu user admin deyil!")


# Sesli sohbet üçün 0-200 arası yeni komanda elave edilmiş. 
@Client.on_message(command(["ses"]) & other_filters)
@authorized_users_only
async def change_ses(client, message):
    range = message.command[1]
    chat_id = message.chat.id
    try:
       callsmusic.pytgcalls.change_volume_call(chat_id, volume=int(range))
       await message.reply(f"✅ **Ayarlandı:** ```{range}%```")
    except Exception as e:
       await message.reply(f"**xeta:** {e}")
