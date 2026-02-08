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
    await message.answer("🎥 **Assalomu alaykum!**\n\nUshbu bot **Obidjon Musurmonov** tomonidan yaratildi.\n\nMenga Instagram link yuboring, men sizga videoni va uning qo'shig'ini yuboraman! 🚀")

@dp.message()
async def download_video(message: types.Message):
    url = message.text
    if "instagram.com" not in url:
        return

    msg = await message.answer("Xo'sh, videoni yuklayapman, biroz kuting...⏳")

    # Fayl nomlari
    video_file = f"{message.from_user.id}.mp4"
    audio_file = f"{message.from_user.id}.mp3"

    try:
        # 1. Videoni yuklash sozlamalari
        ydl_opts_video = {
            'format': 'best',
            'outtmpl': video_file,
        }

        with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
            ydl.download([url])

        # 2. Videoni yuborish
        video = types.FSInputFile(video_file)
        await message.answer_video(video, caption="Mana siz so'ragan video! ✅")

        # 3. Audioni (qo'shiqni) ajratish va yuklash sozlamalari
        ydl_opts_audio = {
            'format': 'bestaudio/best',
            'outtmpl': audio_file.replace(".mp3", ""), # yt-dlp avtomat kengaytma qo'shadi
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        # Audioni yuklash
        with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
            ydl.download([url])
        
        # 4. Musiqani yuborish
        audio = types.FSInputFile(audio_file)
        await message.answer_audio(audio, caption="Bu esa videodagi qo'shiq! 🎶")

        # Fayllarni serverdan o'chirish (tozamiz)
        os.remove(video_file)
        if os.path.exists(audio_file):
            os.remove(audio_file)
        
        await msg.delete()

    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {e}")
        if os.path.exists(video_file): os.remove(video_file)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
