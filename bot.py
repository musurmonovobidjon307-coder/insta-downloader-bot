import asyncio
import os
import re
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Railway Variables-dan tokenni olamiz
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Blokdan qochish uchun professional sozlamalar
YDL_OPTIONS = {
    'quiet': True,
    'no_warnings': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'nocheckcertificate': True,
}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🤖 **Universal Downloader!**\n\nYouTube, TikTok yoki Instagram linkini yuboring.")

@dp.message()
async def download_handler(message: types.Message):
    # Agar xabarda link bo'lmasa, e'tibor bermaymiz
    url = message.text
    if not url or not url.startswith("http"): return

    msg = await message.answer("Video yuklanmoqda... ⏳")
    v_path = f"v_{message.from_user.id}.mp4"

    try:
        # 1. Videoni yuklash
        with yt_dlp.YoutubeDL({**YDL_OPTIONS, 'format': 'best', 'outtmpl': v_path}) as ydl:
            ydl.download([url])
        
        # Tugma yaratish
        # Callback_data ichiga linkni emas, oddiy buyruqni qo'yamiz
        builder = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🎵 Qo'shig'ini topish", callback_data="get_audio")]
        ])

        if os.path.exists(v_path):
            # Caption-ga linkni aniq formatda yozamiz
            await message.answer_video(
                types.FSInputFile(v_path), 
                caption=f"Tayyor! ✅\n\n🔗 Havola: {url}", 
                reply_markup=builder
            )
            os.remove(v_path)
        else:
            raise Exception("Fayl topilmadi")
            
    except Exception:
        await message.answer("❌ Video yuklashda xatolik bo'ldi. Link noto'g'ri yoki video yopiq.")
    finally:
        await msg.delete()

# Tugma bosilganda ishlaydigan qism
@dp.callback_query()
async def process_callback(callback: types.CallbackQuery):
    if callback.data == "get_audio":
        # Caption-dan linkni Regex (muntazam ifodalar) orqali juda aniq sug'urib olamiz
        caption = callback.message.caption
        links = re.findall(r'(https?://[^\s]+)', caption)
        
        if not links:
            await callback.answer("❌ Havola topilmadi.", show_alert=True)
            return

        url = links[0]
        await callback.answer("Musiqa tayyorlanmoqda... 🎶")
        
        a_temp_name = f"temp_{callback.from_user.id}"
        audio_opts = {
            **YDL_OPTIONS,
            'format': 'bestaudio/best',
            'outtmpl': a_temp_name,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
        try:
            with yt_dlp.YoutubeDL(audio_opts) as ydl:
                ydl.download([url])
            
            final_audio = f"{a_temp_name}.mp3"
            if os.path.exists(final_audio):
                await callback.message.answer_audio(
                    types.FSInputFile(final_audio), 
                    caption="Marhamat, videodagi qo'shiq! 🎵"
                )
                os.remove(final_audio)
            else:
                await callback.message.answer("❌ Musiqa fayli yaratilmadi.")
        except Exception:
            await callback.message.answer("❌ Kechirasiz, bu videoning audiosini olib bo'lmadi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
