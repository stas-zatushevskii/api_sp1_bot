import logging
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
        filename=os.path.expanduser('~/api_sp1_bot/main.log'),
        filemode='w',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',

    ),


REJECTED = 'К сожалению, в работе нашлись ошибки.'
REVIEWING = 'Работа взята в ревью'
PPROVED = 'Ревьюеру всё понравилось, работа зачтена!'
ANSWER = (
    'У вас проверили работу "{name}" !\n\n{verdict}')
UNEXPECTED_RESPONSE = 'Неожиданный ответ от сервера'
ERROR = 'Сервер сообщил про отказ'


def parse_homework_status(homework):
    if homework['status'] == 'rejected':
        verdict = REJECTED
    elif homework['status'] == 'reviewing':
        verdict = REVIEWING
    elif homework['status'] == 'approved':
        verdict = PPROVED
    else:
        verdict = UNEXPECTED_RESPONSE

    return ANSWER.format(
        name=homework['homework_name'], verdict=verdict)


HEADERS = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}


def get_homeworks(current_timestamp):
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(URL, headers=HEADERS, params=payload)
    except ConnectionError as error:
        raise error(f'Ошибка соединения, {payload}')
    # на случай если ответ от яндекса не утешающий
    if homework_statuses == 'error':
        return ERROR
    elif homework_statuses == 'code':
        return ERROR
    else:
        return homework_statuses.json()


def send_message(message):
    return bot.send_message(message)


def main():
    current_timestamp = int(time.time())  # Начальное значение timestamp

    while True:
        try:
            home_work_status = get_homeworks(current_timestamp)
            homework = reversed(home_work_status['homeworks'])
            result = parse_homework_status(homework[1])
            # на случай если не правильно -
            # (не понимаю как тут обойтись без цыкла)
            send_message(result)
            time.sleep(5 * 60)  # Опрашивать раз в пять минут

        except Exception as error:
            print(f'что-то не получилось {error}')
            logging.error(error, exc_info=True)
            time.sleep(13 * 60)


if __name__ == '__main__':
    main()
