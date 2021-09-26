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
        filename=os.path.expanduser('~/main.log'),
        filemode='w',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',

    )


REJECTED = 'К сожалению, в работе нашлись ошибки.'
REVIEWING = 'Работа взята в ревью'
PPROVED = 'Ревьюеру всё понравилось, работа зачтена!'
ANSWER = (
    'У вас проверили работу "{name}" !\n\n{verdict}')
UNEXPECTED_RESPONSE = 'Неожиданный статус в ответе сервера: {status_name}'
ERROR = 'Сервер сообщил об отказ'
HEADERS = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
MAIN_ERROR = 'что-то не получилось {error}'
UNEXPECTED_KEY = ('Яндекс полмался :{JSON_ERROR},'
+ '{HEADERS}, {payload}, {URL}')

STATUSES = {
    'rejected': REJECTED,
    'reviewing': REVIEWING,
    'approved': PPROVED
}

JSON_ERROR = {
    'error': ERROR,
    'code': ERROR
}


def parse_homework_status(homework):
    status = homework['status']
    if status in STATUSES:
        verdict = STATUSES[status]
    else:
        raise ValueError(
            UNEXPECTED_RESPONSE.format(status_name=STATUSES[status]))
    return ANSWER.format(
        name=homework['homework_name'], verdict=verdict)
    # ход конём, чёт функция подозрительно похудела


def get_homeworks(current_timestamp):
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(URL, headers=HEADERS, params=payload)
    except AttributeError as error:
        raise requests.ConnectionError(
            (f'Ошибка соединения, :{payload},'
                + f'{HEADERS}, ошибка : {error}, {URL}'))
    # на случай если ответ от яндекса не утешающий
    for response in homework_statuses.json():
        if response in JSON_ERROR.keys():
            raise ValueError(
            UNEXPECTED_KEY.format(JSON_ERROR=ERROR[response],
                HEADERS=HEADERS, payload=payload, URL=URL))
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(message)


def main():
    current_timestamp = int(time.time())  # Начальное значение timestamp

    while True:
        try:
            homework_statuses = get_homeworks(current_timestamp)
            current_timestamp = homework_statuses.get("current_date")
            homework = homework_statuses['homeworks']
            message = parse_homework_status(homework[0])
            send_message(message)

            time.sleep(5 * 60)  # Опрашивать раз в пять минут

        except Exception as error:
            print(MAIN_ERROR.format(error=error))
            logging.error(MAIN_ERROR, exc_info=True)
            time.sleep(13 * 60)


if __name__ == '__main__':
    main()
