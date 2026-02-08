import asyncio
import os
import re
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from shazamio import Shazam

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()
shazam = Shazam()

YDL_OPTS_BASE = {
    'quiet': True, 'no_warnings': True, 'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🤖 **Musiqa qidiruvchi bot!**\nLink yuboring, men to'liq qo'shiqni topib beraman.")

@dp.message()
async def download_handler(message: types.Message):
    url = message.text
    if not url or not url.startswith("http"): return

    msg = await message.answer("Video tahlil qilinmoqda... ⏳")
    v_path = f"v_{message.from_user.id}.mp4"

    try:
        with yt_dlp.YoutubeDL({**YDL_OPTS_BASE, 'format': 'best', 'outtmpl': v_path}) as ydl:
            ydl.download([url])
        
        builder = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🎵 To'liq qo'shiqni topish", callback_data="find_full_audio")]
        ])

        if os.path.exists(v_path):
            await message.answer_video(types.FSInputFile(v_path), caption=f"Tayyor! ✅\n🔗 Havola: {url}", reply_markup=builder)
            os.remove(v_path)
    except:
        await message.answer("❌ Xatolik yuz berdi.")
    finally:
        await msg.delete()

@dp.callback_query()
async def process_callback(callback: types.CallbackQuery):
    if callback.data == "find_full_audio":
        caption = callback.message.caption
        links = re.findall(r'(https?://[^\s]+)', caption)
        if not links: return

        url = links[0]
        await callback.answer("Qo'shiq qidirilmoqda... 🔍", show_alert=False)
        
        # 1. Videodan qisqa audio ajratamiz (tanish uchun)
        temp_a = f"short_{callback.from_user.id}.mp3"
        try:
            with yt_dlp.YoutubeDL({**YDL_OPTS_BASE, 'format': 'bestaudio/best', 'outtmpl': temp_a}) as ydl:
                ydl.download([url])
            
            # 2. Shazam orqali tanib olamiz
            out = await shazam.recognize_song(temp_a)
            os.remove(temp_a)

            if not out.get('track'):
                await callback.message.answer("❌ Kechirasiz, qo'shiqni aniqlab bo'lmadi.")
                return

            title = out['track']['title']
            author = out['track']['subtitle']
            full_name = f"{author} - {title}"
            
            await callback.message.answer(f"🔍 Topildi: **{full_name}**\nTo'liq versiyasi yuklanmoqda... ⏳")

            # 3. YouTube'dan to'liq variantini qidirib yuklaymiz
            full_audio_path = f"full_{callback.from_user.id}.mp3"
            search_opts = {
                **YDL_OPTS_BASE,
                'format': 'bestaudio/best',
                'outtmpl': full_audio_path,
                'default_search': 'ytsearch1', # Birinchi chiqqan natija
            }
            
            with yt_dlp.YoutubeDL(search_opts) as ydl:
                ydl.download([f"ytsearch1:{full_name}"])
            
            if os.path.exists(full_audio_path):
                await callback.message.answer_audio(types.FSInputFile(full_audio_path), caption=f"🎵 {full_name}\nTo'liq versiya ✅")
                os.remove(full_audio_path)
                
        except Exception as e:
            await callback.message.answer("❌ Qo'shiqni topishda xatolik yuz berdi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
