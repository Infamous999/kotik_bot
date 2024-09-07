import os
import ssl
import urllib.request
import openai
import whisper
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, Application
from pydub import AudioSegment
ssl._create_default_https_context = ssl._create_unverified_context



# Инициализация модели Whisper
model = whisper.load_model("base")

# Токен вашего Telegram бота
TELEGRAM_TOKEN = "7446911137:AAEL-k3xq1SGVeOEtyILe04Vfk0i6iFWjG0"


# Функция для транскрипции аудио
def transcribe_audio(audio_path):
    result = model.transcribe(audio_path)
    return result["text"]


# Обработчик команды /start
async def start(update: Update, context):
    await update.message.reply_text("Привет! Отправьте мне аудиофайл, и я транскрибирую его для вас.")


# Обработчик аудиофайлов
async def handle_audio(update: Update, context):
    message = update.message
    if message.audio:
        audio_file = await message.audio.get_file()
    elif message.voice:
        audio_file = await message.voice.get_file()
    else:
        return

    audio_path = f"{audio_file.file_id}.ogg"

    # Скачивание аудиофайла
    await audio_file.download_to_drive(audio_path)

    # Конвертация в WAV
    audio = AudioSegment.from_file(audio_path)
    wav_path = f"{audio_file.file_id}.wav"
    audio.export(wav_path, format="wav")

    # Транскрипция аудио
    transcription = transcribe_audio(wav_path)

    # Отправка результата
    await message.reply_text(f"Транскрипция: {transcription}")

    # Удаление временных файлов
    os.remove(audio_path)
    os.remove(wav_path)


# Основная функция запуска бота
def main():
    # Создание приложения бота
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.AUDIO | filters.VOICE, handle_audio))

    # Запуск бота
    application.run_polling()


if __name__ == '__main__':
    main()
