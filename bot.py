import asyncio
import os
import re
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Tokenni Railway Variables-dan olamiz
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Barqarorlik uchun asosiy sozlamalar
YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🤖 **Bot qayta tiklandi!**\nYouTube yoki Instagram linkini yuboring, men to'liq musiqasini topaman.")

@dp.message()
async def main_handler(message: types.Message):
    url = message.text
    if not url or not url.startswith("http"): return

    msg = await message.answer("Video yuklanmoqda... ⏳")
    v_name = f"v_{message.from_user.id}.mp4"

    try:
        # Videoni yuklaymiz va uning nomini (title) olamiz
        with yt_dlp.YoutubeDL({**YDL_OPTS, 'format': 'best', 'outtmpl': v_name}) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'Musiqa') # Videoning nomi

        builder = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🎵 To'liq original musiqani topish", callback_data="find_full")]
        ])

        if os.path.exists(v_name):
            # Videoning nomini caption-da yashirib ketamiz
            await message.answer_video(
                types.FSInputFile(v_name), 
                caption=f"✅ {video_title}\n\n🔗 Havola: {url}", 
                reply_markup=builder
            )
            os.remove(v_name)
    except:
        await message.answer("❌ Yuklashda xatolik. Linkni tekshiring.")
    finally:
        if msg: await msg.delete()

@dp.callback_query()
async def audio_handler(callback: types.CallbackQuery):
    if callback.data == "find_full":
        # Caption-dan video nomini va linkni ajratamiz
        caption = callback.message.caption
        video_title = caption.split('\n')[0].replace('✅ ', '')
        links = re.findall(r'(https?://[^\s]+)', caption)
        
        if not links: return
        url = links[0]

        await callback.answer("To'liq musiqa qidirilmoqda... 🎶")
        full_a = f"full_{callback.from_user.id}.mp3"
        
        # Qidiruv mantiqi: avval videoni o'zini audiosini yuklaydi (eng aniq yo'l)
        search_opts = {
            **YDL_OPTS,
            'format': 'bestaudio/best',
            'outtmpl': full_a,
        }

        try:
            with yt_dlp.YoutubeDL(search_opts) as ydl:
                ydl.download([url])
            
            if os.path.exists(full_a):
                await callback.message.answer_audio(
                    types.FSInputFile(full_a), 
                    caption=f"🎵 {video_title}\nTo'liq versiya ✅"
                )
                os.remove(full_a)
        except:
            await callback.message.answer("❌ Musiqani topib bo'lmadi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
