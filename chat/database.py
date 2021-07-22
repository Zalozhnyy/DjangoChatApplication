import psycopg2
from dataclasses import dataclass


@dataclass
class DataBaseMessage:
    id: int
    chat_id: int
    message_value: str
    sender: str


class PostgresDB:
    def __init__(self):
        self._database = 'chatapp'
        self._user = 'postgres'
        self._password = '753159'

        self._connection = self._init_connection()
        self._cursor = self._connection.cursor()

    def _init_connection(self):
        con = psycopg2.connect(
            database=self._database,
            user=self._user,
            password=self._password,
            host="127.0.0.1",
            port="5432"
        )
        return con

    def store_message(self, message, username, room_name):
        self._cursor.execute(f'SELECT chat_id from chat_id_users WHERE user_names = \'{room_name}\';')
        chat_id = self._cursor.fetchall()[0][0]
        sql = f'''
        INSERT INTO messages(chat_id, message_value, date_time, sender)
        VALUES ('{chat_id}', '{message}', 'NOW()', '{username}');
        '''

        self._cursor.execute(sql)
        self._connection.commit()

    def create_chat_id(self, room_name):
        self._cursor.execute(f'SELECT * from chat_id_users WHERE user_names = \'{room_name}\';')
        a = self._cursor.fetchall()

        if not a:
            sql = f'''
            INSERT INTO chat_id_users(user_names) VALUES ('{room_name}')
            ON CONFLICT DO NOTHING;
            '''
            self._cursor.execute(sql)
            self._connection.commit()

    def get_chat_history(self, room_name):
        self._cursor.execute(f'''
        SELECT message_id, chat_id, message_value, sender from messages 
            WHERE  chat_id = (SELECT chat_id FROM chat_id_users WHERE user_names = '{room_name}')
            ORDER BY date_time ASC;
            ''')
        a = self._cursor.fetchall()

        return [DataBaseMessage(*message) for message in a]
