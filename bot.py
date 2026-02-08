import asyncio
import os
import re
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Blokdan qochish va barqaror ishlash uchun sozlamalar
YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("✅ **Bot qayta ishga tushdi!**\nYouTube yoki Instagram linkini yuboring.")

@dp.message()
async def main_handler(message: types.Message):
    url = message.text
    if not url or not url.startswith("http"): return

    msg = await message.answer("Video yuklanmoqda... ⏳")
    file_name = f"v_{message.from_user.id}.mp4"

    try:
        with yt_dlp.YoutubeDL({**YDL_OPTS, 'format': 'best', 'outtmpl': file_name}) as ydl:
            ydl.download([url])
        
        builder = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🎵 To'liq musiqasini topish", callback_data="find_full")]
        ])

        if os.path.exists(file_name):
            await message.answer_video(
                types.FSInputFile(file_name), 
                caption=f"Tayyor! ✅\n🔗 Havola: {url}", 
                reply_markup=builder
            )
            os.remove(file_name)
    except:
        await message.answer("❌ Video yuklashda xatolik. Linkni tekshiring.")
    finally:
        await msg.delete()

@dp.callback_query()
async def audio_handler(callback: types.CallbackQuery):
    if callback.data == "find_full":
        # Linkni caption ichidan olamiz
        caption = callback.message.caption
        links = re.findall(r'(https?://[^\s]+)', caption)
        if not links: return

        url = links[0]
        await callback.answer("Musiqa tayyorlanmoqda... 🎶")
        
        audio_file = f"a_{callback.from_user.id}.mp3"
        # Bu yerda 'bestaudio' YouTube'dan eng to'liq audio oqimini oladi
        audio_opts = {
            **YDL_OPTS,
            'format': 'bestaudio/best',
            'outtmpl': audio_file,
        }
        
        try:
            with yt_dlp.YoutubeDL(audio_opts) as ydl:
                ydl.download([url])
            
            # To'liq audioni yuboramiz
            if os.path.exists(audio_file):
                await callback.message.answer_audio(
                    types.FSInputFile(audio_file), 
                    caption="Marhamat, musiqaning to'liq varianti! 🎵"
                )
                os.remove(audio_file)
        except:
            await callback.message.answer("❌ Musiqani yuklab bo'lmadi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
