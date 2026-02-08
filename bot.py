import asyncio
import os
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Railway Variables-dan tokenni olamiz
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Blokdan qochish uchun umumiy sozlamalar
YDL_OPTIONS = {
    'quiet': True,
    'no_warnings': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🤖 **Universal Downloader!**\nYouTube, TikTok yoki Instagram linkini yuboring.")

@dp.message()
async def download_handler(message: types.Message):
    url = message.text
    if not url.startswith("http"): return

    # Agar foydalanuvchi tugmani bossa, xabar "music_" bilan keladi
    if url.startswith("music_"):
        actual_url = url.replace("music_", "")
        await download_audio(message, actual_url)
        return

    msg = await message.answer("Video yuklanmoqda... ⏳")
    v_path = f"v_{message.from_user.id}.mp4"

    try:
        with yt_dlp.YoutubeDL({**YDL_OPTIONS, 'format': 'best', 'outtmpl': v_path}) as ydl:
            ydl.download([url])
        
        # Tugma yaratish: Linkni xabar matni sifatida qayta yuborish buyrug'ini beramiz
        builder = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🎵 Qo'shig'ini topish", callback_data=f"audio_req")]
        ])

        if os.path.exists(v_path):
            # Linkni caption-da qoldiramiz, keyinchalik audio uchun kerak bo'ladi
            await message.answer_video(
                types.FSInputFile(v_path), 
                caption=f"Tayyor! ✅\n\nLink: `{url}`", 
                parse_mode="Markdown",
                reply_markup=builder
            )
            os.remove(v_path)
    except Exception:
        await message.answer("❌ Video yuklashda xatolik bo'ldi. Linkni tekshiring.")
    finally:
        await msg.delete()

# Tugma bosilganda ishlaydigan qism
@dp.callback_query()
async def process_callback(callback: types.CallbackQuery):
    if callback.data == "audio_req":
        # Caption-dan linkni ajratib olamiz
        caption = callback.message.caption
        try:
            url = caption.split("Link: ")[1].strip("`")
            await callback.answer("Musiqa tayyorlanmoqda... 🎶")
            await download_audio(callback.message, url)
        except:
            await callback.answer("❌ Linkni aniqlab bo'lmadi.", show_alert=True)

async def download_audio(message: types.Message, url: types.Message):
    a_temp = f"temp_{message.chat.id}"
    audio_opts = {
        **YDL_OPTIONS,
        'format': 'bestaudio/best',
        'outtmpl': a_temp,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    try:
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.download([url])
        
        audio_file = f"{a_temp}.mp3"
        if os.path.exists(audio_file):
            await message.answer_audio(types.FSInputFile(audio_file), caption="Marhamat! 🎵")
            os.remove(audio_file)
    except Exception:
        await message.answer("❌ Musiqani yuklab bo'lmadi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
