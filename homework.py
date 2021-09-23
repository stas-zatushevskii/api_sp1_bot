import logging
from logging.handlers import RotatingFileHandler
import os
import time


from dotenv import load_dotenv
import requests
from telegram import Bot

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'

bot = Bot(token=TELEGRAM_TOKEN)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        filename='main.log',
        filemode='w',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',

    ), os.path.expanduser('~/main.log')


logger = logging.getLogger(__name__)
handler = RotatingFileHandler(
    'my_logger.log', maxBytes=50000000, backupCount=5
)

PHRASE_FOR_rejected = 'К сожалению, в работе нашлись ошибки.'
PHRASE_FOR_reviewing = 'Работа взята в ревью'
PHRASE_FOR_approved = 'Ревьюеру всё понравилось, работа зачтена!'
PHRASE_FOR_otvet = (
    'У вас проверили работу "{name_to_insert}" !\n\n{verdict_to_insert}')


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    if homework['status'] == 'rejected':
        verdict = PHRASE_FOR_rejected
    elif homework['status'] == 'reviewing':
        verdict = PHRASE_FOR_reviewing
    else:
        verdict = PHRASE_FOR_approved
    return PHRASE_FOR_otvet.format(
        name_to_insert=homework_name, verdict_to_insert=verdict)

HEADERS = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}


def get_homeworks(current_timestamp):
    headers = HEADERS
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(URL, headers=headers, params=payload)
    except TypeError as error:
        logging.error(error, exc_info=True)
        raise error('что-то не так с {homework_statuses}')
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(message)


def main():
    current_timestamp = int(time.time())  # Начальное значение timestamp

    while True:
        try:
            home_work_status = get_homeworks(current_timestamp)
            for homework in reversed(home_work_status['homeworks']):
                result = parse_homework_status(homework[1])
                send_message(result)
            time.sleep(5 * 60)  # Опрашивать раз в пять минут

        except Exception as error:
            print(f'Не получилось достать домашку: {error}')
            logging.error(error, exc_info=True)
            time.sleep(13 * 60)


if __name__ == '__main__':
    main()
