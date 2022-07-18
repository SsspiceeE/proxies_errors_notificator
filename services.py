import json
import requests
import re
from datetime import datetime
import telebot
import time
import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from config import BOT_TOKEN, CHAT_ID, CREDENTIALS_FILE, SPREADSHEET_ID


def get_urls():
    """Получаем список ссылок из json файла"""
    with open('urls.json', 'r', encoding='UTF-8') as file:
        data = json.load(file)
        urls = [i['url'] for i in data]
        return urls


def get_proxies_errors_list(url):
    """Получаем список зафиксированных ошибок по ссылке"""
    try:
        response = requests.get(url=url)
        if response.status_code == 200:
            data = response.json().get('proxies')
            return data
    except requests.exceptions.ConnectionError:
        pass


def write_data_into_google_sheets(proxy_error_data: dict):
    """Записываем данные в гугл таблицу"""
    date_time = proxy_error_data.get('date_time')
    date_time = datetime.strptime(date_time, '%Y.%m.%d, %H:%M:%S').strftime('%d.%m.%Y %H:%M:%S')
    ip = proxy_error_data.get('ip')
    city = proxy_error_data.get('city')
    server = proxy_error_data.get('server')
    operator = proxy_error_data.get('operator')

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE,
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive'])

    httpAuth = credentials.authorize(httplib2.Http())

    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)

    add_new_row = service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={
            'requests': [
                {
                    'insertDimension': {
                        'range': {
                            'sheetId': 0,
                            'dimension': 'ROWS',
                            'startIndex': 1,
                            'endIndex': 2
                        },
                        'inheritFromBefore': True
                    }
                }
            ]
        }
    )

    add_new_row.execute()  # создаем новую строку в гугл таблице

    with open('server_colors.json', 'r', encoding='UTF-8') as file:
        data = json.load(file)
        server_colors = data[server]
        red = server_colors['red']
        green = server_colors['green']
        blue = server_colors['blue']
        alpha = server_colors['alpha']

    add_row_color = service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body=
        {
            "requests":
                [
                    {
                        "repeatCell":
                            {
                                "cell":
                                    {
                                        "userEnteredFormat":
                                            {
                                                "backgroundColor": {
                                                    "red": red,
                                                    "green": green,
                                                    "blue": blue,
                                                    "alpha": alpha,
                                                },
                                                "textFormat":
                                                    {
                                                        "bold": True,
                                                        "fontSize": 11
                                                    }
                                            }
                                    },
                                "range":
                                    {
                                        "sheetId": 0,
                                        "startRowIndex": 1,
                                        "endRowIndex": 2,
                                        "startColumnIndex": 0,
                                        "endColumnIndex": 5
                                    },
                                "fields": "userEnteredFormat"
                            }
                    }
                ]
        })

    add_row_color.execute()  # окрашиваем строку в нужный цвет в зависимости от сервера

    insert_values = service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": 'A2:G2',
                 "majorDimension": "ROWS",
                 "values": [[server, ip, city, operator, date_time]]}

            ]
        }
    )

    insert_values.execute()  # записываем данные в таблицу


def create_message_text(proxy_error_data: dict):
    """Составляем сообщение для отправки в телеграм-чат из словаря"""
    date_time = proxy_error_data.get('date_time')
    date_time = datetime.strptime(date_time, '%Y.%m.%d, %H:%M:%S').strftime('%d.%m.%Y %H:%M:%S')
    proxy_error_data['date_time'] = date_time
    text = [f"<b>{key}</b>: {proxy_error_data[key]}" for key in proxy_error_data]
    title = '<b>Информация об ошибке:\n</b>'
    text.insert(0, title)
    text = '\n'.join(text)
    text = re.sub('server', 'Сервер', text)
    text = re.sub('city', 'Город', text)
    text = re.sub('operator', 'Оператор', text)
    text = re.sub('date_time', 'Дата и время инцидента', text)
    return text


def send_message(text: str):
    """Отправляем сообщение об ошибке в чат"""
    bot = telebot.TeleBot(token=BOT_TOKEN, parse_mode='HTML')
    while True:
        try:
            bot.send_message(chat_id=CHAT_ID, text=text)
            break
        except telebot.apihelper.ApiTelegramException:
            time.sleep(30)
            pass
