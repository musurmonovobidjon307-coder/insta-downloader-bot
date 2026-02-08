import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🎥 **Salom!** Men @Obidjon_Musurmonov yaratgan botman.\n\nInstagram link yuboring, video va audiosini yuklab beraman! 🚀")

@dp.message()
async def download(message: types.Message):
    if "instagram.com" not in message.text: return
    
    msg = await message.answer("Jarayon boshlandi... ⏳")
    v_path = f"{message.from_user.id}.mp4"
    a_path = f"{message.from_user.id}.mp3"

    try:
        # 1. Videoni yuklash
        with yt_dlp.YoutubeDL({'format': 'best', 'outtmpl': v_path, 'quiet': True}) as ydl:
            ydl.download([message.text])
        await message.answer_video(types.FSInputFile(v_path), caption="Tayyor! ✅\nMuallif: @Obidjon_Musurmonov")

        # 2. Audioni (qo'shiqni) ajratish
        # Ba'zi videolarda audio ajratish murakkab bo'lgani uchun oddiyroq usuldan foydalanamiz
        ydl_opts_a = {
            'format': 'bestaudio/best',
            'outtmpl': a_path.replace(".mp3", ""),
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts_a) as ydl:
            ydl.download([message.text])
        
        if os.path.exists(a_path):
            await message.answer_audio(types.FSInputFile(a_path), caption="Videodagi qo'shiq! 🎶")

    except Exception as e:
        # Xatolikni aniqroq ko'rish uchun (faqat tekshirishda)
        print(f"Xato: {e}")
        await message.answer("❌ Qo'shiqni ajratishda xatolik bo'ldi. Linkni qayta tekshiring.")
    
    finally:
        for p in [v_path, a_path]:
            if os.path.exists(p): os.remove(p)
        await msg.delete()

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
