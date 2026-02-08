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
    await message.answer(
        "👋 **Assalomu alaykum!**\n\n"
        "Ushbu bot **@Obidjon_Musurmonov** tomonidan yaratildi.\n"
        "Menga Instagram link yuboring, men sizga video va qo'shig'ini yuboraman! 📥"
    )

@dp.message()
async def download_video(message: types.Message):
    url = message.text
    if "instagram.com" not in url:
        return

    msg = await message.answer("Xo'sh, jarayon boshlandi... ⏳")
    v_path = f"{message.from_user.id}.mp4"
    a_path = f"{message.from_user.id}.mp3"

    try:
        # 1. Video yuklash
        ydl_v = {
            'format': 'best', 'outtmpl': v_path, 'quiet': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
        }
        with yt_dlp.YoutubeDL(ydl_v) as ydl:
            ydl.download([url])

        await message.answer_video(types.FSInputFile(v_path), caption="Tayyor! ✅\nMuallif: Obidjon")

        # 2. Audio (musiqa) ajratish
        ydl_a = {
            'format': 'bestaudio/best', 'outtmpl': a_path.replace(".mp3", ""),
            'quiet': True,
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        }
        with yt_dlp.YoutubeDL(ydl_a) as ydl:
            ydl.download([url])

        if os.path.exists(a_path):
            await message.answer_audio(types.FSInputFile(a_path), caption="Videodagi qo'shiq! 🎶")

        # Tozalash
        for p in [v_path, a_path]:
            if os.path.exists(p): os.remove(p)
        await msg.delete()

    except Exception:
        await msg.edit_text("❌ Xatolik! Instagram yuklashga ruxsat bermadi.")
        for p in [v_path, a_path]:
            if os.path.exists(p): os.remove(p)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
