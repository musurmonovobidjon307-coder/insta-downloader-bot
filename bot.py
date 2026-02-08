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

# Blokdan qochish uchun eng kuchli sozlamalar
YDL_COMMON_OPTIONS = {
    'quiet': True,
    'no_warnings': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'geo_bypass': True,
}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🤖 **Universal Downloader!**\n\nYouTube yoki Instagram linkini yuboring.")

@dp.message()
async def download_handler(message: types.Message):
    url = message.text
    if not url or not url.startswith("http"): return

    msg = await message.answer("Video yuklanmoqda... ⏳")
    v_path = f"v_{message.from_user.id}.mp4"

    try:
        # Videoni eng yaxshi sifatda yuklash
        with yt_dlp.YoutubeDL({**YDL_COMMON_OPTIONS, 'format': 'best', 'outtmpl': v_path}) as ydl:
            ydl.download([url])
        
        # Audio tugmasini yaratish
        builder = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🎵 Qo'shig'ini topish", callback_data="get_audio")]
        ])

        if os.path.exists(v_path):
            # Caption ichiga linkni aniq joylaymiz
            await message.answer_video(
                types.FSInputFile(v_path), 
                caption=f"Tayyor! ✅\n\n🔗 Havola: {url}", 
                reply_markup=builder
            )
            os.remove(v_path)
        else:
            await message.answer("❌ Videoni yuklab bo'lmadi.")
    except Exception:
        await message.answer("❌ Xatolik yuz berdi.")
    finally:
        await msg.delete()

@dp.callback_query()
async def process_callback(callback: types.CallbackQuery):
    if callback.data == "get_audio":
        caption = callback.message.caption
        links = re.findall(r'(https?://[^\s]+)', caption)
        
        if not links:
            await callback.answer("❌ Havola topilmadi.", show_alert=True)
            return

        url = links[0]
        await callback.answer("Musiqa tayyorlanmoqda... 🎶")
        
        # Audio yuklash uchun sodda va xatosiz sozlama
        a_path = f"audio_{callback.from_user.id}.mp3"
        audio_opts = {
            **YDL_COMMON_OPTIONS,
            'format': 'bestaudio/best',
            'outtmpl': a_path, # To'g'ridan-to'g'ri MP3 qilib yuklaymiz
        }
        
        try:
            with yt_dlp.YoutubeDL(audio_opts) as ydl:
                ydl.download([url])
            
            # Agar fayl nomi .mp3 bilan tugamasa, uni to'g'irlaymiz
            # Ba'zan yt-dlp o'ziga xos formatda yuklashi mumkin
            files = os.listdir('.')
            downloaded_file = ""
            for f in files:
                if f.startswith(f"audio_{callback.from_user.id}"):
                    downloaded_file = f
                    break

            if downloaded_file:
                await callback.message.answer_audio(
                    types.FSInputFile(downloaded_file), 
                    caption="Marhamat, videodagi qo'shiq! 🎵"
                )
                os.remove(downloaded_file)
            else:
                await callback.message.answer("❌ Musiqani topib bo'lmadi.")
        except Exception:
            await callback.message.answer("❌ Musiqa yuklashda xatolik yuz berdi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
