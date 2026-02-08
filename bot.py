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
    await message.answer(
        "🌟 **Universal Downloader Bot!**\n\n"
        "Menga YouTube, Instagram yoki TikTok linkini yuboring, "
        "video va audiosini (MP3) yuklab beraman! 🚀\n\n"
        "Muallif: **Obidjon Musurmonov**"
    )

@dp.message()
async def universal_download(message: types.Message):
    url = message.text
    if not url.startswith("http"):
        return

    msg = await message.answer("Havola tekshirilmoqda... ⏳")
    v_path = f"video_{message.from_user.id}.mp4"
    a_path = f"audio_{message.from_user.id}.mp3"

    try:
        # 1. Video yuklash sozlamalari
        ydl_v_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': v_path,
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_v_opts) as ydl:
            await msg.edit_text("Video yuklanmoqda... 🎥")
            ydl.download([url])
        
        await message.answer_video(
            types.FSInputFile(v_path), 
            caption="Tayyor! ✅\n@Vedio_yukla1bot orqali yuklandi."
        )

        # 2. Audio ajratish sozlamalari (FFmpeg kerak)
        ydl_a_opts = {
            'format': 'bestaudio/best',
            'outtmpl': a_path.replace(".mp3", ""),
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_a_opts) as ydl:
            await msg.edit_text("Musiqasi ajratilmoqda... 🎶")
            ydl.download([url])

        if os.path.exists(a_path):
            await message.answer_audio(
                types.FSInputFile(a_path), 
                caption="Videodagi qo'shiq! 🎵"
            )

    except Exception as e:
        await message.answer(f"❌ Xatolik: Yuklab bo'lmadi. Havola noto'g'ri yoki video yopiq profilda.")
    
    finally:
        # Fayllarni o'chirish
        for p in [v_path, a_path]:
            if os.path.exists(p): os.remove(p)
        await msg.delete()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
