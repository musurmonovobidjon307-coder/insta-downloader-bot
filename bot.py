import asyncio
import os
import re
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from shazamio import Shazam

# Railway Variables
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
    await message.answer("**Assalomu alaykum!**\nMen orqali YouTube yoki Instagram videolarini yuklashingiz va ulardagi musiqaning **to'liq versiyasini** topishingiz mumkin. 🎵")

@dp.message()
async def download_handler(message: types.Message):
    url = message.text
    if not url or not url.startswith("http"): return

    msg = await message.answer("Video yuklanmoqda... ⏳")
    v_path = f"v_{message.from_user.id}.mp4"

    try:
        with yt_dlp.YoutubeDL({**YDL_OPTS_BASE, 'format': 'best', 'outtmpl': v_path}) as ydl:
            ydl.download([url])
        
        builder = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🎵 To'liq musiqasini topish", callback_data="full_music")]
        ])

        if os.path.exists(v_path):
            await message.answer_video(types.FSInputFile(v_path), caption=f"Tayyor! ✅\n🔗 Havola: {url}", reply_markup=builder)
            os.remove(v_path)
    except:
        await message.answer("❌ Videoni yuklab bo'lmadi.")
    finally:
        await msg.delete()

@dp.callback_query()
async def process_callback(callback: types.CallbackQuery):
    if callback.data == "full_music":
        caption = callback.message.caption
        links = re.findall(r'(https?://[^\s]+)', caption)
        if not links: return

        url = links[0]
        wait_msg = await callback.message.answer("Qo'shiq tahlil qilinmoqda... 🔍")
        
        temp_a = f"short_{callback.from_user.id}.mp3"
        try:
            # 1. Videodan ovozni yuklab olamiz
            with yt_dlp.YoutubeDL({**YDL_OPTS_BASE, 'format': 'bestaudio/best', 'outtmpl': temp_a}) as ydl:
                ydl.download([url])
            
            # 2. Shazam orqali qo'shiqni taniymiz
            out = await shazam.recognize_song(temp_a)
            if os.path.exists(temp_a): os.remove(temp_a)

            if not out.get('track'):
                await wait_msg.edit_text("❌ Kechirasiz, qo'shiqni aniqlab bo'lmadi.")
                return

            track_info = out['track']
            full_name = f"{track_info['subtitle']} - {track_info['title']}"
            await wait_msg.edit_text(f"🎵 Topildi: **{full_name}**\nTo'liq versiya yuklanmoqda... ⏳")

            # 3. YouTube'dan to'liq versiyasini qidiramiz
            full_a_path = f"full_{callback.from_user.id}.mp3"
            search_opts = {
                **YDL_OPTS_BASE,
                'format': 'bestaudio/best',
                'outtmpl': full_a_path,
                'default_search': 'ytsearch1',
            }
            
            with yt_dlp.YoutubeDL(search_opts) as ydl:
                ydl.download([f"ytsearch1:{full_name}"])
            
            if os.path.exists(full_a_path):
                await callback.message.answer_audio(types.FSInputFile(full_a_path), caption=f"🎵 {full_name}\nOriginal to'liq versiya ✅")
                os.remove(full_a_path)
                await wait_msg.delete()
                
        except Exception:
            await wait_msg.edit_text("❌ Musiqani topishda xatolik yuz berdi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
