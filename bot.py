import asyncio
import os
import re
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

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
    await message.answer("🤖 **Musiqa qidiruvchi bot!**\nLink yuboring, men qo'shiqning to'liq versiyasini topib beraman.")

@dp.message()
async def main_handler(message: types.Message):
    url = message.text
    if not url or not url.startswith("http"): return

    msg = await message.answer("Video tahlil qilinmoqda... ⏳")
    v_name = f"v_{message.from_user.id}.mp4"

    try:
        with yt_dlp.YoutubeDL({**YDL_OPTS, 'format': 'best', 'outtmpl': v_name}) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'Musiqa') 

        builder = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🎵 To'liq (Full) versiyasini topish", callback_data="find_full")]
        ])

        if os.path.exists(v_name):
            await message.answer_video(
                types.FSInputFile(v_name), 
                caption=f"✅ {video_title}\n\n🔗 Havola: {url}", 
                reply_markup=builder
            )
            os.remove(v_name)
    except:
        await message.answer("❌ Xatolik yuz berdi.")
    finally:
        if msg: await msg.delete()

@dp.callback_query()
async def audio_handler(callback: types.CallbackQuery):
    if callback.data == "find_full":
        caption = callback.message.caption
        # Videoning nomini caption-dan olamiz
        video_title = caption.split('\n')[0].replace('✅ ', '')
        
        await callback.answer("To'liq qo'shiq qidirilmoqda... 🎶")
        full_a = f"full_{callback.from_user.id}.mp3"
        
        # QIDIRUV MANTIQI: Video nomi orqali YouTube'dan to'liq audioni qidirish
        # 'ytsearch1:' buyrug'i YouTube'dan birinchi chiqqan to'liq videoni oladi
        search_query = f"ytsearch1:{video_title} full audio"
        
        search_opts = {
            **YDL_OPTS,
            'format': 'bestaudio/best',
            'outtmpl': full_a,
        }

        wait_msg = await callback.message.answer(f"🔍 **{video_title}** qidirilmoqda...")

        try:
            with yt_dlp.YoutubeDL(search_opts) as ydl:
                ydl.download([search_query])
            
            if os.path.exists(full_a):
                await callback.message.answer_audio(
                    types.FSInputFile(full_a), 
                    caption=f"🎵 {video_title}\n\n✨ To'liq original versiya topildi!"
                )
                os.remove(full_a)
                await wait_msg.delete()
        except:
            await wait_msg.edit_text("❌ Afsuski, qo'shiqning to'liq versiyasini topib bo'lmadi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
