from io import BytesIO
import io
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
import asyncio

from aiogram.enums.parse_mode import ParseMode


from src.features.update_user_location.services import get_update_user_location
from src.shared.libs.s3 import S3Adapter
from src.shared.configs import settings

from src.shared.api.yandex.map import YandexMapClient, YandexMapResult

import uuid


def _s3_create_adapter():
    return S3Adapter(
        settings.s3.host,
        settings.s3.port,
        settings.s3.access_key,
        settings.s3.secret_key,
        use_ssl=settings.s3.use_ssl,
    ).initialize()


USER_TOKEN = settings.telegram_bot.user_token
SERVICE_TOKEN = settings.telegram_bot.service_token
TARGET_CHAT_ID = settings.telegram_bot.service_chat_id

user_bot = Bot(token=USER_TOKEN)
dp = Dispatcher()

service_bot = Bot(token=SERVICE_TOKEN)

from src.app.init import pipeline

from aiogram.filters import Command
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import F


def _to_message(yandex_map_results: list[YandexMapResult]) -> str:
    message = "Список потенциальных целей:"
    
    yandex_map_results = sorted(yandex_map_results, key=lambda yandex_map_result: yandex_map_result.distance.value)
    
    for i, yandex_map_result in enumerate(yandex_map_results, start=1):
        distanse = yandex_map_result.distance.text
        message += f"\n{i}) <b>{distanse}</b>: {yandex_map_result.title}"
    return message


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

    video_file = await user_bot.get_file(message.video.file_id)
    video_bytes = await user_bot.download_file(video_file.file_path)
    
    
    latitude, longitude = get_update_user_location().get_location(message.from_user.id)
        
    id = str(uuid.uuid4())
    file_name = id + ".mp4"

    _s3_create_adapter().upload_file("drones", f"rows/{file_name}", video_bytes)
    result = pipeline.detect(id)
    video_name, video_bytes = _s3_create_adapter().download_file_bytes(
        "drones", result.detection_video_url
    )

    message = await service_bot.send_message(
        chat_id=TARGET_CHAT_ID,
        text="❗ВНИМАНИЕ❗\nГраждане сообщают об атаке БПЛА"
    )
    
    await service_bot.send_location(
        chat_id=TARGET_CHAT_ID,
        latitude=latitude,
        longitude=longitude,
        reply_to_message_id=message.message_id,
    )

    await service_bot.send_video(
        chat_id=TARGET_CHAT_ID,
        video=types.BufferedInputFile(file=video_bytes, filename=video_name),
        caption="Обработанное видео 📹: ",
        reply_to_message_id=message.message_id,
    )

    report_name, report_bytes = _s3_create_adapter().download_file_bytes(
        "drones", result.report_url
    )

    await service_bot.send_photo(
        chat_id=TARGET_CHAT_ID,
        photo=types.BufferedInputFile(report_bytes, filename=report_name),
        caption="Статистика 📊: ",
        reply_to_message_id=message.message_id,
    )

    if result.model_info:
        await service_bot.send_message(
            chat_id=TARGET_CHAT_ID, 
            text=f"Модель БПЛА: {result.model_info.model} / {(result.model_info.average_confidence * 100):.0f}%",
            reply_to_message_id=message.message_id,
        )
    client = YandexMapClient(api_key="de0a0eed-8f3e-4a79-89e5-9e47b7d2b164")
    results = await client.set_ll(
        longitude,
        latitude,
    ).set_results(5).set_attrs().send("Производственное предприятие")

    if len(results) > 0:
        await service_bot.send_message(
            chat_id=TARGET_CHAT_ID, 
            text=_to_message(results),
            reply_to_message_id=message.message_id,
            parse_mode=ParseMode.HTML
        )
    
    

async def main():
    print("Бот 1 запущен...")
    await dp.start_polling(user_bot)


if __name__ == "__main__":
    asyncio.run(main())
