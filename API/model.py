from mysql.connector.connection import MySQLConnection
from mysql.connector import Error


class Database(MySQLConnection):
    def __init__(self, host, user, password, database):
        # Инициализация подключения через родительский конструктор
        super().__init__(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.autocommit = False

    def execute_query(self, query, params=None):
        """Выполняет запрос к базе данных без возврата результата"""
        cursor = self.cursor()
        cursor.execute(query, params)
        cursor.close()

    def fetch_query(self, query, params=None):
        """Выполняет запрос к базе данных и возвращает все результаты"""
        cursor = self.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        return result

    def close(self):
        """Закрывает подключение к базе данных"""
        if self.is_connected():
            super().close()


def return_db():
    db = Database(host='5.183.188.132',
                  user='2024_mysql_k_usr',
                  password='KgT4gD9eWNS7Cque',
                  database='2024_mysql_kon')
    return db
