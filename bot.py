import asyncio
import os
import re
import yt_dlp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Qidiruv natijalari uchun vaqtinchalik xotira
search_results = {}

YDL_OPTS_BASE = {
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'referer': 'https://www.google.com/',
}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🤖 **Assalomu alaykum!**\nYouTube yoki Instagram linkini yuboring. Men videoni yuklayman va undagi musiqani qidirib beraman!")

@dp.message(F.text.startswith("http"))
async def handle_link(message: types.Message):
    url = message.text
    msg = await message.answer("Video yuklanmoqda... ⏳")
    v_path = f"v_{message.from_user.id}.mp4"

    try:
        # 1. Videoni yuklash va ma'lumotlarni olish
        with yt_dlp.YoutubeDL({**YDL_OPTS_BASE, 'format': 'best', 'outtmpl': v_path}) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Aqlli qidiruv so'zini yasaymiz
            track = info.get('track')
            artist = info.get('artist')
            title = info.get('title', 'Musiqa')
            
            if track and artist:
                q = f"{artist} {track}"
            else:
                # Keraksiz so'zlarni tozalaymiz
                q = re.sub(r'(?i)shorts|reels|instagram|video|#\w+|@\w+', '', title)
            
            q = q.strip()

        # 2. Videoni yuboramiz
        builder = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🎵 To'liq variantlarni ko'rish", callback_data=f"list:{q[:40]}")]
        ])

        if os.path.exists(v_path):
            await message.answer_video(types.FSInputFile(v_path), caption=f"✅ Tayyor!\n🔍 Qidiruv: **{q}**", reply_markup=builder)
            os.remove(v_path)
    except:
        await message.answer("❌ Yuklashda xatolik yuz berdi.")
    finally:
        await msg.delete()

@dp.callback_query(F.data.startswith("list:"))
async def show_list(callback: types.CallbackQuery):
    query = callback.data.replace("list:", "")
    await callback.answer("Qidirilmoqda...")
    
    wait_msg = await callback.message.answer(f"🔍 **{query}** bo'yicha eng yaxshi variantlar...")

    try:
        with yt_dlp.YoutubeDL(YDL_OPTS_BASE) as ydl:
            # YouTube'dan 5 ta natija
            search_data = ydl.extract_info(f"ytsearch5:{query} official audio", download=False)['entries']
            
            results_text = f"🎶 **{query}** uchun natijalar:\n\n"
            buttons = []
            temp_list = []

            for i, entry in enumerate(search_data, 1):
                t = entry.get('title')[:35]
                d = entry.get('duration_string', '0:00')
                results_text += f"{i}. {t} — **{d}**\n"
                temp_list.append({'url': entry.get('webpage_url'), 'title': t})
                buttons.append(types.InlineKeyboardButton(text=str(i), callback_data=f"dl:{i}"))

            search_results[callback.from_user.id] = temp_list
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons])
            await callback.message.answer(results_text, reply_markup=keyboard)
            await wait_msg.delete()
    except:
        await wait_msg.edit_text("❌ Qidiruvda xatolik bo'ldi.")

@dp.callback_query(F.data.startswith("dl:"))
async def download_audio(callback: types.CallbackQuery):
    idx = int(callback.data.split(":")[1]) - 1
    user_id = callback.from_user.id

    if user_id not in search_results:
        await callback.answer("Ma'lumot topilmadi, linkni qayta yuboring.", show_alert=True)
        return

    chosen = search_results[user_id][idx]
    status = await callback.message.answer(f"📥 **{chosen['title']}** yuklanmoqda...")
    
    path = f"a_{user_id}.mp3"
    try:
        with yt_dlp.YoutubeDL({**YDL_OPTS_BASE, 'format': 'bestaudio/best', 'outtmpl': path}) as ydl:
            ydl.download([chosen['url']])
        
        if os.path.exists(path):
            await callback.message.answer_audio(types.FSInputFile(path), caption=f"🎵 {chosen['title']}\nMarhamat! ✅")
            os.remove(path)
            await status.delete()
    except:
        await callback.message.answer("❌ Yuklab bo'lmadi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
