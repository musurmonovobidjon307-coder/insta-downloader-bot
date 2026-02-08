import asyncio
import os
import re
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

YDL_OPTS_BASE = {
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'referer': 'https://www.google.com/',
}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🤖 **Musiqa qidiruvchi bot tayyor!**\nLink tashlang, men videoning nomi emas, ichidagi qo'shig'iga qarab qidiraman.")

@dp.message()
async def main_handler(message: types.Message):
    url = message.text
    if not url or not url.startswith("http"): return

    msg = await message.answer("Video tahlil qilinmoqda... ⏳")
    v_path = f"v_{message.from_user.id}.mp4"

    try:
        # 1. Videoni yuklash va ichidagi haqiqiy musiqa ma'lumotlarini olish
        with yt_dlp.YoutubeDL({**YDL_OPTS_BASE, 'format': 'best', 'outtmpl': v_path}) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # YouTube o'zi taniy olgan qo'shiq ma'lumotlarini qidiramiz
            track = info.get('track')
            artist = info.get('artist')
            alt_title = info.get('title')
            
            if track and artist:
                search_query = f"{artist} - {track}"
                found_by = "musiqa ma'lumotlari"
            else:
                # Agar musiqani YouTube tanimagan bo'lsa, keraksiz so'zlarni olib tashlab qidiramiz
                search_query = re.sub(r'[^\w\s]', '', alt_title)
                found_by = "video nomi"

        builder = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🎵 To'liq original musiqani topish", callback_data=f"search:{search_query[:40]}")]
        ])

        if os.path.exists(v_path):
            await message.answer_video(
                types.FSInputFile(v_path), 
                caption=f"✅ Topildi (manba: {found_by})\n🔍 Qidiruv so'rovi: **{search_query}**", 
                reply_markup=builder
            )
            os.remove(v_path)
    except:
        await message.answer("❌ Yuklashda xatolik. Linkni tekshiring.")
    finally:
        if msg: await msg.delete()

@dp.callback_query(lambda c: c.data.startswith('search:'))
async def find_audio(callback: types.CallbackQuery):
    query = callback.data.replace('search:', '')
    await callback.answer(f"Qidirilmoqda: {query}")
    
    wait_msg = await callback.message.answer(f"🔍 **{query}** qo'shig'ining to'liq varianti yuklanmoqda...")
    a_path = f"full_{callback.from_user.id}.mp3"
    
    try:
        # Qidiruvni aniqroq qilish uchun 'official audio' qo'shamiz
        search_opts = {
            **YDL_OPTS_BASE,
            'format': 'bestaudio/best',
            'outtmpl': a_path,
            'default_search': 'ytsearch1',
        }
        
        with yt_dlp.YoutubeDL(search_opts) as ydl:
            ydl.download([f"ytsearch1:{query} official audio"])
        
        if os.path.exists(a_path):
            await callback.message.answer_audio(
                types.FSInputFile(a_path), 
                caption=f"🎵 {query}\n\n✨ To'liq original versiya!"
            )
            os.remove(a_path)
            await wait_msg.delete()
    except:
        await wait_msg.edit_text("❌ Qo'shiqni topishda xatolik yuz berdi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
