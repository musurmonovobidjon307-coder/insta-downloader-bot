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

YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("✅ **Bot tayyor!**\nLink yuboring, men to'liq original musiqasini topib beraman.")

@dp.message()
async def main_handler(message: types.Message):
    url = message.text
    if not url or not url.startswith("http"): return

    msg = await message.answer("Video yuklanmoqda... ⏳")
    v_name = f"v_{message.from_user.id}.mp4"

    try:
        with yt_dlp.YoutubeDL({**YDL_OPTS, 'format': 'best', 'outtmpl': v_name}) as ydl:
            ydl.download([url])
        
        builder = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🔍 To'liq original musiqani topish", callback_data="find_shazam")]
        ])

        if os.path.exists(v_name):
            await message.answer_video(types.FSInputFile(v_name), caption=f"Tayyor! ✅\n🔗 Havola: {url}", reply_markup=builder)
            os.remove(v_name)
    except:
        await message.answer("❌ Video yuklashda xatolik.")
    finally:
        if msg: await msg.delete()

@dp.callback_query()
async def shazam_handler(callback: types.CallbackQuery):
    if callback.data == "find_shazam":
        caption = callback.message.caption
        links = re.findall(r'(https?://[^\s]+)', caption)
        if not links: return

        url = links[0]
        wait_msg = await callback.message.answer("Musiqa tahlil qilinmoqda... 🧠")
        short_a = f"s_{callback.from_user.id}.mp3"
        
        try:
            # 1. Videodan qisqa audio ajratamiz
            with yt_dlp.YoutubeDL({**YDL_OPTS, 'format': 'bestaudio/best', 'outtmpl': short_a}) as ydl:
                ydl.download([url])
            
            # 2. Shazam orqali tanib olamiz
            shz = Shazam()
            out = await shz.recognize_song(short_a)
            
            if out.get('track'):
                track_name = f"{out['track']['subtitle']} - {out['track']['title']}"
                await wait_msg.edit_text(f"🎵 Topildi: **{track_name}**\nTo'liq versiya qidirilmoqda... 🚀")
                
                # 3. YouTube'dan o'sha nom bilan qidirib, to'liq mp3 yuklaymiz
                full_a = f"full_{callback.from_user.id}.mp3"
                search_opts = {
                    **YDL_OPTS, 
                    'format': 'bestaudio/best', 
                    'outtmpl': full_a,
                    'default_search': 'ytsearch1',
                }
                with yt_dlp.YoutubeDL(search_opts) as ydl:
                    ydl.download([f"ytsearch1:{track_name}"])
                
                if os.path.exists(full_a):
                    await callback.message.answer_audio(types.FSInputFile(full_a), caption=f"✅ {track_name}\nTo'liq original versiya!")
                    os.remove(full_a)
                if os.path.exists(short_a): os.remove(short_a)
                await wait_msg.delete()
            else:
                await wait_msg.edit_text("🔍 Shazam topolmadi. Videodagi audioni o'zi yuborilmoqda...")
                await callback.message.answer_audio(types.FSInputFile(short_a), caption="Videodagi audio 🎵")
                os.remove(short_a)
                
        except Exception:
            await wait_msg.edit_text("❌ Musiqani topishda xatolik bo'ldi.")
            if os.path.exists(short_a): os.remove(short_a)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
