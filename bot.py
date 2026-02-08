import asyncio
import os
import re
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Eng yangi va barqaror sozlamalar
YDL_OPTS_BASE = {
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'referer': 'https://www.google.com/',
}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🤖 **Assalomu alaykum!**\nBu bot @Obidjon_Musurmonov tomonidan yaratildi\nYouTube yoki Instagram linkini yuboring.")

@dp.message()
async def download_handler(message: types.Message):
    url = message.text
    if not url or not url.startswith("http"): return

    msg = await message.answer("Jarayon boshlandi... ⏳")
    v_path = f"v_{message.from_user.id}.mp4"

    try:
        # Videoni yuklash
        with yt_dlp.YoutubeDL({**YDL_OPTS_BASE, 'format': 'best', 'outtmpl': v_path}) as ydl:
            ydl.download([url])
        
        builder = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🎵 Qo'shig'ini topish", callback_data="get_audio")]
        ])

        if os.path.exists(v_path):
            await message.answer_video(
                types.FSInputFile(v_path), 
                caption=f"Tayyor! ✅\n\n🔗 Havola: {url}", 
                reply_markup=builder
            )
            os.remove(v_path)
        else:
            await message.answer("❌ Video yuklanmadi. Boshqa link sinab ko'ring.")
    except:
        await message.answer("❌ Xatolik: Bu videoni yuklab bo'lmadi.")
    finally:
        await msg.delete()

@dp.callback_query()
async def process_callback(callback: types.CallbackQuery):
    if callback.data == "get_audio":
        caption = callback.message.caption
        links = re.findall(r'(https?://[^\s]+)', caption)
        if not links: return

        url = links[0]
        await callback.answer("Musiqa tayyorlanmoqda... 🎶")
        
        a_path = f"audio_{callback.from_user.id}.mp3"
        # Audio yuklashda eng sodda formatdan foydalanamiz
        audio_opts = {
            **YDL_OPTS_BASE,
            'format': 'bestaudio/best',
            'outtmpl': a_path,
        }
        
        try:
            with yt_dlp.YoutubeDL(audio_opts) as ydl:
                ydl.download([url])
            
            # Faylni aniq topish uchun
            downloaded = ""
            for f in os.listdir('.'):
                if f.startswith(f"audio_{callback.from_user.id}"):
                    downloaded = f
                    break

            if downloaded:
                await callback.message.answer_audio(
                    types.FSInputFile(downloaded), 
                    caption="Marhamat, videodagi qo'shiq! 🎵"
                )
                os.remove(downloaded)
        except:
            await callback.message.answer("❌ Musiqani yuklashda xatolik bo'ldi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
