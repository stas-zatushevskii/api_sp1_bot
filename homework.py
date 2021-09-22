import logging
import os
import time
from logging.handlers import RotatingFileHandler

import requests
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

logging.basicConfig(level=logging.INFO)
PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
BOT_TOKEN = os.getenv('BOT_TOKEN')
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'

bot = Bot(token=BOT_TOKEN)

logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    filemode='w',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)
handler = RotatingFileHandler('my_logger.log', maxBytes=50000000, backupCount=5)
logger.addHandler(handler) 

def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    try:
        if homework.get('status') == 'rejected':
            verdict = 'К сожалению, в работе нашлись ошибки.'
        else:
            verdict = 'Ревьюеру всё понравилось, работа зачтена!'
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    except Exception as error:
        print(f'Чет не то: {error}')
        logging.error(error, exc_info=True)

def get_homeworks(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(URL, headers=headers, params=payload)
    except Exception as error:
        print(f'Чет не то: {error}')
        logging.error(error, exc_info=True)
    return homework_statuses.json()

def send_message(message):
    return bot.send_message(message)

def main():
    current_timestamp = int(time.time())  # Начальное значение timestamp

    while True:
        try:
            home_work_status = get_homeworks(current_timestamp)
            for homework in reversed(home_work_status['homeworks']):
                result = parse_homework_status(homework)
                send_message(result)
            time.sleep(5 * 60) # Опрашивать раз в пять минут

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            logging.error(e, exc_info=True)

if __name__ == '__main__':
    main()
