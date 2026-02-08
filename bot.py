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
        "Ushbu bot **Obidjon Musurmonov** tomonidan yaratildi.\n"
        "Menga Instagram link yuboring, men uni yuklab beraman! 📥"
    )

@dp.message()
async def download_video(message: types.Message):
    url = message.text
    if "instagram.com" not in url:
        return

    msg = await message.answer("Yuklanmoqda... ⏳")
    file_path = f"{message.from_user.id}.mp4"

    try:
        # Instagram blokini aylanib o'tish uchun maxsus sozlamalar
        ydl_opts = {
            'format': 'best',
            'outtmpl': file_path,
            'quiet': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'add_header': [
                'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language: en-US,en;q=0.5',
            ],
            'referer': 'https://www.google.com/',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if os.path.exists(file_path):
            await message.answer_video(types.FSInputFile(file_path), caption="Tayyor! ✅\nMuallif: Obidjon")
            os.remove(file_path)
            await msg.delete()
        else:
            raise Exception("Fayl yuklanmadi")

    except Exception as e:
        print(f"Xato: {e}")
        await msg.edit_text("❌ Instagram hozircha blokladi. 5-10 daqiqadan so'ng boshqa link bilan urinib ko'ring yoki kutubxonani yangilang📥.")
        if os.path.exists(file_path): os.remove(file_path)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
