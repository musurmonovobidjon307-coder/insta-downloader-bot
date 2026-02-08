import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import yt_dlp

# Railway Variables bo'limidan tokenni oladi
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🎥 **Salom!** Men Obidjon Musurmonov yaratgan botman.\n\nInstagram link yuboring, video va audiosini yuklab beraman! 🚀")

@dp.message()
async def download(message: types.Message):
    if "instagram.com" not in message.text:
        return
    
    msg = await message.answer("Jarayon boshlandi... ⏳")
    v_path = f"{message.from_user.id}.mp4"
    a_path = f"{message.from_user.id}.mp3"

    try:
        # 1. Video yuklash
        ydl_opts_v = {'format': 'best', 'outtmpl': v_path, 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts_v) as ydl:
            ydl.download([message.text])
        
        await message.answer_video(types.FSInputFile(v_path), caption="Tayyor! ✅\nMuallif: @Obidjon_Musurmonov")

        # 2. Audio ajratish
        ydl_opts_a = {
            'format': 'bestaudio/best',
            'outtmpl': a_path.replace(".mp3", ""),
            'quiet': True,
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        }
        with yt_dlp.YoutubeDL(ydl_opts_a) as ydl:
            ydl.download([message.text])
        
        if os.path.exists(a_path):
            await message.answer_audio(types.FSInputFile(a_path), caption="Videodagi qo'shiq! 🎶")

    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi. Instagram yuklashni chekladi.")
    
    finally:
        # Fayllarni tozalash
        for p in [v_path, a_path]:
            if os.path.exists(p):
                os.remove(p)
        await msg.delete()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
