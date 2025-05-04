from io import BytesIO
import io
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
import asyncio


from src.features.update_user_location.services import get_update_user_location
from src.shared.libs.s3 import S3Adapter
from src.shared.configs import settings

import uuid


def _s3_create_adapter():
    return S3Adapter(
        settings.s3.host,
        settings.s3.port,
        settings.s3.access_key,
        settings.s3.secret_key,
        use_ssl=settings.s3.use_ssl,
    ).initialize()


TOKEN1 = "7110892014:AAFPEvzIiD5PG_pt_sFG7x6dNwbdkchZynU"
TOKEN2 = "7869796693:AAHsQnHgDHNuX-gCjF0a22XDxTB0vhshfu8"
TARGET_CHAT_ID = "511246625"

bot1 = Bot(token=TOKEN1)
dp = Dispatcher()

bot2 = Bot(token=TOKEN2)

from src.app.init import pipeline

from aiogram.filters import Command
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import F


async def _cmd_start(message: Message):
    location_button = KeyboardButton(
        text="📍 Отправить геопозицию", request_location=True
    )
    keyboard = ReplyKeyboardMarkup(keyboard=[[location_button]], resize_keyboard=True)
    return await message.answer(
        "💌 Нажми кнопку, чтобы отправить геопозицию", reply_markup=keyboard
    )

@dp.message(Command("start"))
async def cmd_start(message: Message):
    return await _cmd_start(message)


@dp.message(lambda msg: msg.location is not None)
async def relay_message(message: Message):
    get_update_user_location().update_location(
        message.from_user.id,
        message.location.latitude,
        message.location.longitude
    )
    return await message.answer(
        "📍 Координаты успешно обновлены"
    )


@dp.message(lambda msg: msg.video is not None)
async def detection_drone(message: Message):
    time_to_update = get_update_user_location().time_to_update_location(
        message.from_user.id,
    )
    
    if time_to_update:
        return await _cmd_start(message)

    video_file = await bot1.get_file(message.video.file_id)
    video_bytes = await bot1.download_file(video_file.file_path)
    
    
    latitude, longitude = get_update_user_location().get_location(message.from_user.id)
        
    id = str(uuid.uuid4())
    file_name = id + ".mp4"

    _s3_create_adapter().upload_file("drones", f"rows/{file_name}", video_bytes)
    result = pipeline.detect(id)
    video_name, video_bytes = _s3_create_adapter().download_file_bytes(
        "drones", result["detection_video"]
    )

    message = await bot2.send_message(
        chat_id=TARGET_CHAT_ID,
        text="❗ВНИМАНИЕ❗\nГраждание сообщают об атаке БПЛА"
    )
    
    await bot2.send_location(
        chat_id=TARGET_CHAT_ID,
        latitude=latitude,
        longitude=longitude,
        reply_to_message_id=message.message_id,
    )

    await bot2.send_video(
        chat_id=TARGET_CHAT_ID,
        video=types.BufferedInputFile(file=video_bytes, filename=video_name),
        caption="Обработанное видео 📹: ",
        reply_to_message_id=message.message_id,
    )
    report_name, report_bytes = _s3_create_adapter().download_file_bytes(
        "drones", result["report"]
    )
    await bot2.send_photo(
        chat_id=TARGET_CHAT_ID,
        photo=types.BufferedInputFile(report_bytes, filename=report_name),
        caption="Статистика 📊: ",
        reply_to_message_id=message.message_id,
    )

async def main():
    print("Бот 1 запущен...")
    await dp.start_polling(bot1)


if __name__ == "__main__":
    asyncio.run(main())
