from services import get_urls, get_proxies_errors_list, create_message_text, send_message, write_data_into_google_sheets
from db.models import UpTimeErrorsWorker

up_time_errors_worker = UpTimeErrorsWorker()


def main():
    urls = get_urls()  # получаем список ссылок с записями об ошибках
    for url in urls:
        proxies_errors_list = get_proxies_errors_list(url=url)  # получаем список записей об ошибке из ссылки
        for proxy_error_data in proxies_errors_list:
            if up_time_errors_worker.is_record_exist(
                    proxy_error_data=proxy_error_data):  # проверяем существует ли такая запись в нашей базе данных
                break
            up_time_errors_worker.log_uptime_error_record(
                proxy_error_data=proxy_error_data)  # делаем запись об ошибке в базу данных
            write_data_into_google_sheets(proxy_error_data=proxy_error_data)  # записываем данные в гугл таблицу
            text = create_message_text(proxy_error_data=proxy_error_data)  # создаем сообщение для отправки в телеграм
            send_message(text=text)  # отправляем сообщение


if __name__ == '__main__':
    main()
