import asyncio
import os
import yt_dlp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Qidiruv natijalari uchun vaqtinchalik xotira
search_results = {}

YDL_OPTS = {
    'quiet': True, 'no_warnings': True, 'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🤖 **Assalomu alaykum!**\nYouTube yoki Instagram linkini yuboring. To'liq qo'shiqni topish uchun esa **qo'shiq nomini** yozib yuboring!")

# 1. Video linki kelganda uni yuklab berish
@dp.message(F.text.startswith("http"))
async def handle_link(message: types.Message):
    msg = await message.answer("Video yuklanmoqda... ⏳")
    path = f"v_{message.from_user.id}.mp4"
    try:
        with yt_dlp.YoutubeDL({**YDL_OPTS, 'format': 'best', 'outtmpl': path}) as ydl:
            ydl.download([message.text])
        if os.path.exists(path):
            await message.answer_video(types.FSInputFile(path), caption="Tayyor! ✅\n\n💡 _Qo'shiqni topish uchun uning nomini yozib yuboring._")
            os.remove(path)
    except:
        await message.answer("❌ Yuklashda xatolik yuz berdi. Linkni tekshiring.")
    finally:
        await msg.delete()

# 2. Qo'shiq nomi yozilganda YouTube'dan qidirish (Sozandabot uslubida)
@dp.message(F.text)
async def handle_search(message: types.Message):
    q = message.text
    if q.startswith("/") or q.startswith("http"): return
    
    wait_msg = await message.answer(f"🔍 **{q}** qidirilmoqda...")
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            # 5 ta natijani qidirish
            search_data = ydl.extract_info(f"ytsearch5:{q} official audio", download=False)['entries']
            
            if not search_data:
                await wait_msg.edit_text("❌ Hech narsa topilmadi.")
                return

            results_text = f"🎶 **{q}** bo'yicha topilgan natijalar:\n\n"
            buttons = []
            temp_list = []
            for i, entry in enumerate(search_data, 1):
                t = entry.get('title')[:35]
                d = entry.get('duration_string', '0:00')
                results_text += f"{i}. {t} [**{d}**]\n"
                temp_list.append({'url': entry.get('webpage_url'), 'title': t})
                buttons.append(types.InlineKeyboardButton(text=str(i), callback_data=f"dl:{i}"))

            search_results[message.from_user.id] = temp_list
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons])
            await message.answer(results_text, reply_markup=keyboard)
            await wait_msg.delete()
    except:
        await wait_msg.edit_text("❌ Qidiruvda xatolik bo'ldi.")

@dp.callback_query(F.data.startswith("dl:"))
async def download_audio(callback: types.CallbackQuery):
    idx = int(callback.data.split(":")[1]) - 1
    user_id = callback.from_user.id
    if user_id not in search_results: return

    chosen = search_results[user_id][idx]
    await callback.answer(f"📥 {chosen['title']} yuklanmoqda...")
    status = await callback.message.answer("📥 Qo'shiq yuklanmoqda...")
    
    path = f"a_{user_id}.mp3"
    try:
        with yt_dlp.YoutubeDL({**YDL_OPTS, 'format': 'bestaudio/best', 'outtmpl': path}) as ydl:
            ydl.download([chosen['url']])
        await callback.message.answer_audio(types.FSInputFile(path), caption=f"🎵 {chosen['title']}\nTayyor! ✅")
        os.remove(path)
        await status.delete()
    except:
        await callback.message.answer("❌ Yuklashda xatolik.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
