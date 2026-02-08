import asyncio
import os
import re
import yt_dlp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Qidiruv uchun xotira (vaqtinchalik natijalarni saqlash)
search_results = {}

YDL_OPTS = {
    'quiet': True, 'no_warnings': True, 'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🤖 **Musiqa qidiruvchi bot tayyor!**\nLink yuboring, men sizga ro'yxat ko'rsataman.")

@dp.message(F.text.startswith("http"))
async def handle_link(message: types.Message):
    msg = await message.answer("Tahlil qilinmoqda... ⏳")
    url = message.text

    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)
            # Metadata yoki video nomidan qidiruv so'zi yasaymiz
            q = f"{info.get('artist', '')} {info.get('track', '')}" or info.get('title')
            q = re.sub(r'[^\w\s]', '', q).strip()

            # YouTube'dan 5 ta natija qidiramiz
            search_data = ydl.extract_info(f"ytsearch5:{q} official audio", download=False)['entries']
            
            results_text = f"🔍 **{q}** bo'yicha natijalar:\n\n"
            buttons = []
            temp_list = []

            for i, entry in enumerate(search_data, 1):
                title = entry.get('title')[:40]
                duration = entry.get('duration_string', '0:00')
                results_text += f"{i}. {title} **{duration}**\n"
                
                # Natijani saqlab qo'yamiz
                temp_list.append({'url': entry.get('webpage_url'), 'title': title})
                buttons.append(types.InlineKeyboardButton(text=str(i), callback_data=f"down:{i}"))

            # Foydalanuvchi IDsi bilan natijalarni saqlaymiz
            search_results[message.from_user.id] = temp_list

            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons])
            await message.answer(results_text, reply_markup=keyboard)
            
    except Exception:
        await message.answer("❌ Ma'lumot topilmadi.")
    finally:
        await msg.delete()

@dp.callback_query(F.data.startswith("down:"))
async def download_chosen(callback: types.CallbackQuery):
    idx = int(callback.data.split(":")[1]) - 1
    user_id = callback.from_user.id

    if user_id not in search_results:
        await callback.answer("Eski natija. Linkni qayta yuboring.", show_alert=True)
        return

    chosen = search_results[user_id][idx]
    await callback.message.edit_text(f"📥 **{chosen['title']}** yuklanmoqda...")

    path = f"music_{user_id}.mp3"
    try:
        with yt_dlp.YoutubeDL({**YDL_OPTS, 'format': 'bestaudio/best', 'outtmpl': path}) as ydl:
            ydl.download([chosen['url']])
        
        if os.path.exists(path):
            await callback.message.answer_audio(types.FSInputFile(path), caption="Marhamat! ✅")
            os.remove(path)
            await callback.message.delete()
    except:
        await callback.message.answer("❌ Yuklashda xatolik bo'ldi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
