from .core import Base, SessionLocal
from sqlalchemy import Column, Integer, String, DateTime


class UpTimeError(Base):
    """Модель записи об ошибке"""
    __tablename__ = 'up_time_errors'

    id = Column(Integer, primary_key=True, unique=True, index=True)
    date_time = Column(String)
    server = Column(String)
    ip = Column(String)
    city = Column(String)
    operator = Column(String)


class UpTimeErrorsWorker:
    def __init__(self):
        pass

    def is_record_exist(self, proxy_error_data: dict):
        """Проверяем есть ли запись о данной ошибке в нашей базе данных"""
        date_time = proxy_error_data.get('datetime')
        server = proxy_error_data.get('server')
        ip = proxy_error_data.get('ip')
        city = proxy_error_data.get('city')
        operator = proxy_error_data.get('operator')

        session = SessionLocal()
        record = session.query(UpTimeError).\
            filter(UpTimeError.date_time == date_time).\
            filter(UpTimeError.server == server).\
            filter(UpTimeError.ip == ip).\
            filter(UpTimeError.city == city).\
            filter(UpTimeError.operator == operator)
        session.close()
        result = list(record)

        if result:
            return True
        return False

    def log_uptime_error_record(self, proxy_error_data: dict):
        """Записываем ошибку в нашу базу данных"""
        proxy_error_data['date_time'] = proxy_error_data.pop('datetime')

        session = SessionLocal()
        record = UpTimeError(**proxy_error_data)
        session.add(record)
        session.commit()
        session.close()





