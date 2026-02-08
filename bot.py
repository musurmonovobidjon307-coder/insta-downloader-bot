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
        "Ushbu bot Obidjon Musurmonov tomonidan yaratildi.\n"
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
        ydl_opts = {'format': 'best', 'outtmpl': file_path, 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await message.answer_video(types.FSInputFile(file_path), caption="Tayyor! ✅")
        os.remove(file_path)
        await msg.delete()

    except Exception:
        # Xatolik bo'lsa uzun tekst o'rniga qisqa xabar beradi
        await msg.edit_text("❌ Kechirasiz, Instagram bu videoni yuklashga ruxsat bermadi. Keyinroq qayta urinib ko'ring.")
        if os.path.exists(file_path): os.remove(file_path)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
