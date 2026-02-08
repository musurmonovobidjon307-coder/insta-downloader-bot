import asyncio
import os
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🤖 **Universal Downloader!**\nLink yuboring, video yuklab beraman.")

@dp.message()
async def download_handler(message: types.Message):
    url = message.text
    if not url.startswith("http"): return

    msg = await message.answer("Video yuklanmoqda... ⏳")
    v_path = f"v_{message.from_user.id}.mp4"

    ydl_opts = {
        'format': 'best',
        'outtmpl': v_path,
        'quiet': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Tugma yaratish
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(
            text="🎵 Qo'shig'ini topish", 
            callback_data=f"audio|{url}") # Linkni tugma ichiga yashiramiz
        )

        await message.answer_video(
            types.FSInputFile(v_path), 
            caption="Tayyor! ✅",
            reply_markup=builder.as_markup()
        )
        os.remove(v_path)
    except:
        await message.answer("❌ Xatolik! Linkni tekshiring.")
    finally:
        await msg.delete()

# Tugma bosilganda ishlaydigan qism
@dp.callback_query()
async def audio_callback(callback: types.CallbackQuery):
    data = callback.data.split("|")
    if data[0] == "audio":
        url = data[1]
        await callback.answer("Qo'shiq tayyorlanmoqda... 🎶")
        
        a_path = f"a_{callback.from_user.id}.mp3"
        audio_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'temp_audio',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
        }

        try:
            with yt_dlp.YoutubeDL(audio_opts) as ydl:
                ydl.download([url])
            
            if os.path.exists("temp_audio.mp3"):
                await callback.message.answer_audio(
                    types.FSInputFile("temp_audio.mp3"), 
                    caption="Mana marhamat! 🎵"
                )
                os.remove("temp_audio.mp3")
        except:
            await callback.message.answer("❌ Kechirasiz, bu videoning audiosini olib bo'lmadi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
