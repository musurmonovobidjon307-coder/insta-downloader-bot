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
    await message.answer("🎥 Salom! Instagram link yuboring, men uni yuklab beraman.")

@dp.message()
async def download_video(message: types.Message):
    url = message.text
    if "instagram.com" not in url:
        await message.answer("❌ Iltimos, faqat Instagram linkini yuboring.")
        return

    status_msg = await message.answer("⏳ Video tayyorlanmoqda, kuting...")

    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'mp4',
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        for file in os.listdir():
            if file.startswith("video"):
                await message.answer_video(video=types.FSInputFile(file), caption="Tayyor! ✅")
                os.remove(file)
                break
        await status_msg.delete()
    except Exception:
        await message.answer("❌ Xatolik: Video yopiq profilda yoki link noto'g'ri bo'lishi mumkin.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
