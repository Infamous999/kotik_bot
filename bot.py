import os
import ssl
import tempfile
import whisper
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, Application
from pydub import AudioSegment

ssl._create_default_https_context = ssl._create_unverified_context
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

    # Получаем аудиофайл или голосовое сообщение
    audio_file = None
    if message.audio:
        audio_file = await message.audio.get_file()
    elif message.voice:
        audio_file = await message.voice.get_file()
    else:
        return

    # Создаем временную директорию для файлов
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, f"{audio_file.file_id}.ogg")
        wav_path = os.path.join(tmpdir, f"{audio_file.file_id}.wav")
        text_path = os.path.join(tmpdir, f"{audio_file.file_id}.txt")

        # Скачиваем аудиофайл
        await audio_file.download_to_drive(audio_path)

        # Конвертируем аудио в WAV
        audio = AudioSegment.from_file(audio_path)
        audio.export(wav_path, format="wav")

        # Транскрибируем аудио
        transcription = transcribe_audio(wav_path)

        # Записываем транскрипцию в текстовый файл
        with open(text_path, "w") as file:
            file.write(transcription)

        # Отправляем текстовый файл с транскрипцией
        with open(text_path, "rb") as file:
            await message.reply_document(InputFile(file, filename="transcription.txt"))

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
