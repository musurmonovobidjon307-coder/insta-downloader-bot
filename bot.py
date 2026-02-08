import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🎥 **Salom!** Men Obidjon Musurmonov yaratgan botman.\n\nInstagram link yuboring, video va audiosini yuklab beraman! 🚀")

@dp.message()
async def download(message: types.Message):
    if "instagram.com" not in message.text: return
    
    msg = await message.answer("Yuklanmoqda... ⏳")
    v_path, a_path = f"{message.from_user.id}.mp4", f"{message.from_user.id}.mp3"

    try:
        # Video yuklash
        with yt_dlp.YoutubeDL({'format': 'best', 'outtmpl': v_path, 'quiet': True}) as ydl:
            ydl.download([message.text])
        await message.answer_video(types.FSInputFile(v_path), caption="Tayyor! ✅\nMuallif: Obidjon")

        # Audio ajratish
        ydl_a = {
            'format': 'bestaudio/best', 'outtmpl': a_path.replace(".mp3", ""), 'quiet': True,
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        }
        with yt_dlp.YoutubeDL(ydl_a) as ydl:
            ydl.download([message.text])
        
        if os.path.exists(a_path):
            await message.answer_audio(types.FSInputFile(a_path), caption="Videodagi qo'shiq! 🎶")

    except Exception as e:
        await message.answer("❌ Xatolik yuz berdi. Instagram yuklashni chekladi.")
    
    finally:
        for p in [v_path, a_path]:
            if os.path.exists(p): os.remove(p)
        await msg.delete()

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
