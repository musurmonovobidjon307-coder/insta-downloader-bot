import asyncio
import os
import re
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# YouTube blokidan o'tish uchun eng kuchli sozlamalar
YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'referer': 'https://www.google.com/',
    'geo_bypass': True,
    'extract_flat': False,
}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🤖 **Universal Bot qayta tiklandi!**\nYouTube va Instagram videolarini tashlang. Men to'liq musiqasini topib beraman.")

@dp.message()
async def main_handler(message: types.Message):
    url = message.text
    if not url or not url.startswith("http"): return

    msg = await message.answer("Video tahlil qilinmoqda... ⏳")
    v_name = f"v_{message.from_user.id}.mp4"

    try:
        # Videoni yuklash va metadata (ma'lumotlar)ni olish
        with yt_dlp.YoutubeDL({**YDL_OPTS, 'format': 'best', 'outtmpl': v_name}) as ydl:
            info = ydl.extract_info(url, download=True)
            # Eng muhimi: artist va track nomini olishga harakat qilamiz
            track = info.get('track')
            artist = info.get('artist')
            title = info.get('title', 'Nomaalum video')
            
            # Agar artist/track bo'lsa shuni, bo'lmasa video nomini ishlatamiz
            search_query = f"{artist} - {track}" if artist and track else title

        builder = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🎵 To'liq original musiqani topish", callback_data=f"f_m:{search_query[:40]}")]
        ])

        if os.path.exists(v_name):
            await message.answer_video(
                types.FSInputFile(v_name), 
                caption=f"✅ {title}\n\n🔗 Havola: {url}", 
                reply_markup=builder
            )
            os.remove(v_name)
    except Exception as e:
        await message.answer(f"❌ Yuklashda xatolik: YouTube/Instagram cheklov qo'ydi.")
    finally:
        if msg: await msg.delete()

@dp.callback_query(lambda c: c.data.startswith('f_m:'))
async def audio_handler(callback: types.CallbackQuery):
    # Callback ma'lumotidan qidiruv so'zini olamiz
    search_query = callback.data.replace('f_m:', '')
    
    await callback.answer("Original musiqa qidirilmoqda... 🎶")
    full_a = f"full_{callback.from_user.id}.mp3"
    
    # Qidiruvni aniqroq qilish: "official audio" so'zini qo'shamiz
    final_query = f"ytsearch1:{search_query} official audio"
    
    wait_msg = await callback.message.answer(f"🔍 **{search_query}** qidirilmoqda...")

    try:
        search_opts = {
            **YDL_OPTS,
            'format': 'bestaudio/best',
            'outtmpl': full_a,
        }

        with yt_dlp.YoutubeDL(search_opts) as ydl:
            ydl.download([final_query])
        
        if os.path.exists(full_a):
            await callback.message.answer_audio(
                types.FSInputFile(full_a), 
                caption=f"🎵 {search_query}\n\n✨ To'liq original versiya topildi!"
            )
            os.remove(full_a)
            await wait_msg.delete()
        else:
            await wait_msg.edit_text("❌ Musiqa fayli topilmadi.")
    except:
        await wait_msg.edit_text("❌ Qidiruvda xatolik yuz berdi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
