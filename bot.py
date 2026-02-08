import asyncio
import os
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Railway Variables bo'limidagi BOT_TOKEN ni oladi
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Assalomu alaykum! Menga YouTube, TikTok yoki Instagram linkini yuboring. 📥")

@dp.message()
async def download_handler(message: types.Message):
    url = message.text
    if not url.startswith("http"):
        return

    status_msg = await message.answer("Havola tekshirilmoqda... 🔍")
    v_file = f"v_{message.from_user.id}.mp4"
    a_file = f"temp_audio.mp3"

    # TikTok va Instagram uchun maxsus sozlamalar
    ydl_opts_base = {
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'nocheckcertificate': True,
    }

    try:
        # 1. Video yuklash (TikTok va boshqalar uchun)
        await status_msg.edit_text("Video yuklanmoqda... 🎥")
        with yt_dlp.YoutubeDL({**ydl_opts_base, 'format': 'best', 'outtmpl': v_file}) as ydl:
            ydl.download([url])
        
        await message.answer_video(types.FSInputFile(v_file), caption="Tayyor! ✅\n@Vedio_yukla1bot")

        # 2. Audio (MP3) ajratish (FFmpeg yordamida)
        await status_msg.edit_text("Audio ajratib olinmoqda... 🎶")
        audio_opts = {
            **ydl_opts_base,
            'format': 'bestaudio/best',
            'outtmpl': 'temp_audio',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.download([url])
        
        if os.path.exists(a_file):
            await message.answer_audio(types.FSInputFile(a_file), caption="Videodagi musiqa 🎵")

    except Exception as e:
        await message.answer("❌ Xatolik: Havola noto'g'ri yoki video yopiq profilda. Iltimos, boshqa link yuboring.")
    
    finally:
        # Serverni tozalash
        for f in [v_file, a_file]:
            if os.path.exists(f): os.remove(f)
        await status_msg.delete()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
