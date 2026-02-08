import asyncio
import os
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🤖 **Universal Downloader Tayyor!**\n\nYouTube, TikTok va Instagram linklarini yuboravering, men ularni yuklab beraman.")

@dp.message()
async def universal_downloader(message: types.Message):
    url = message.text
    if not url.startswith("http"):
        return

    msg = await message.answer("Tekshirilmoqda... 🔍")
    v_path = f"video_{message.from_user.id}.mp4"
    a_path = f"audio_{message.from_user.id}.mp3"

    # YouTube va TikTok bloklarini chetlab o'tish uchun sozlamalar
    ydl_opts = {
        'format': 'best',
        'outtmpl': v_path,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'referer': 'https://www.google.com/',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await msg.edit_text("Video yuklanmoqda... 🎥")
            info = ydl.extract_info(url, download=True)
            if not info:
                raise Exception("Info topilmadi")

        await message.answer_video(types.FSInputFile(v_path), caption="Tayyor! ✅")

        # Musiqasini ajratish (FFmpeg serverda bor bo'lsa)
        audio_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'temp_audio',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            await msg.edit_text("Musiqasi ajratilmoqda... 🎶")
            ydl.download([url])
            
        if os.path.exists("temp_audio.mp3"):
            await message.answer_audio(types.FSInputFile("temp_audio.mp3"), caption="Musiqa! 🎵")

    except Exception as e:
        await message.answer("❌ Xatolik: Bu platformadan yuklashda muammo bo'ldi. Linkni tekshiring.")
    
    finally:
        for f in [v_path, "temp_audio.mp3"]:
            if os.path.exists(f): os.remove(f)
        await msg.delete()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
