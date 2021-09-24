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
URL = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'

bot = Bot(token=TELEGRAM_TOKEN)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        filename='main.log',
        filemode='w',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',

    ),


REJECTED = 'К сожалению, в работе нашлись ошибки.'
REVIEWING = 'Работа взята в ревью'
PPROVED = 'Ревьюеру всё понравилось, работа зачтена!'
ANSWER = (
    'У вас проверили работу "{name}" !\n\n{verdict}')
UNEXPECTED_RESPONSE = 'Неожиданный ответ от сервера'
ERROR = 'Сервер сообщил об отказ'
HEADERS = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}


ANSWER_FOR_STATUS = {
    'rejected': REJECTED,
    'reviewing': REVIEWING,
    'approved': PPROVED
}

ANSWER_FOR_JSON_ERROR = {
    'error': ERROR,
    'code': ERROR
}


def parse_homework_status(homework):
    try:
        status = homework['status']
        verdict = ANSWER_FOR_STATUS[status]
    except:
        verdict = UNEXPECTED_RESPONSE
    return ANSWER.format(
        name=homework['homework_name'], verdict=verdict)
    # ход конём, чёт функция подозрительно похудела


def get_homeworks(current_timestamp):
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(URL, headers=HEADERS, params=payload)
    except ValueError as error:
        raise error(
            f'Ошибка соединения, параметры запроса : ' +
            f' {payload}, {HEADERS}, ошибка : {error}')
    # на случай если ответ от яндекса не утешающий
    for status in homework_statuses:
        if 'error' or 'code' in status:
            raise ValueError(
                f'Яндекс не дал домашку, ответ сервера:{homework_statuses}, ' +
                f'параметры запроса {HEADERS}, {payload}')


def send_message(message):
    return bot.send_message(message)


def main():
    current_timestamp = int(time.time())  # Начальное значение timestamp

    while True:
        try:
            homework_statuses = get_homeworks(current_timestamp)
            current_timestamp = homework_statuses['current_date']
            for homework in homework_statuses['homeworks']:
                message = parse_homework_status(homework)
                send_message(message)

            time.sleep(5 * 60)  # Опрашивать раз в пять минут

        except Exception as error:
            print(f'что-то не получилось {error}')
            logging.error(error, exc_info=True)
            time.sleep(13 * 60)


if __name__ == '__main__':
    main()
